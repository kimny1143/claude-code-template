"""claude-history-mcp: Claude conversation history search MCP server.

Supports two data sources:
1. claude.ai export (conversations.json) — DATA_DIR/*.json
2. Claude Code local transcripts (~/.claude/projects/**/*.jsonl) — CLAUDE_CODE_DIR
"""

import json, os, re, math
from pathlib import Path
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

DATA_DIR = Path(os.environ.get("CLAUDE_HISTORY_DIR", "./data"))
CLAUDE_CODE_DIR = Path(os.environ.get("CLAUDE_CODE_DIR", str(Path.home() / ".claude" / "projects")))
mcp = FastMCP("claude-history")


class ConversationIndex:
    """In-memory TF-IDF index over Claude conversations."""

    def __init__(self):
        self.conversations = []
        self.inv = defaultdict(set)
        self.idf = {}
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        self._load_claude_ai()
        self._load_claude_code()
        self._build()
        self._loaded = True

    # ── claude.ai export (JSON) ───────────────────────

    def _load_claude_ai(self):
        if not DATA_DIR.exists():
            return
        jfiles = [f for f in sorted(DATA_DIR.glob("*.json")) if f.name != "_index.json"]
        all_c = []
        for jf in jfiles:
            with open(jf, "r", encoding="utf-8") as f:
                d = json.load(f)
                all_c.extend(d) if isinstance(d, list) else all_c.append(d)
        for i, c in enumerate(all_c):
            n = self._norm_web(c, i)
            if n:
                self.conversations.append(n)

    # ── Claude Code local transcripts (JSONL) ────────

    def _load_claude_code(self):
        if not CLAUDE_CODE_DIR.exists():
            return
        for jsonl_file in sorted(CLAUDE_CODE_DIR.glob("*/*.jsonl")):
            try:
                n = self._norm_code(jsonl_file)
                if n:
                    self.conversations.append(n)
            except Exception:
                continue

    def _norm_code(self, jsonl_path):
        """Parse a Claude Code JSONL transcript into normalized format."""
        msgs = []
        session_id = jsonl_path.stem
        project_dir = jsonl_path.parent.name

        first_ts = None
        last_ts = None

        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = d.get("type", "")
                if msg_type not in ("user", "assistant"):
                    continue

                message = d.get("message", {})
                content = message.get("content", [])
                text = ""
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text_parts = []
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text_parts.append(c.get("text", ""))
                        elif isinstance(c, str):
                            text_parts.append(c)
                    text = " ".join(text_parts)

                if not text or len(text) < 5:
                    continue
                if text.startswith("[Request interrupted") or text.startswith("[Tool Result"):
                    continue

                ts = d.get("timestamp", "")
                if ts and not first_ts:
                    first_ts = ts
                if ts:
                    last_ts = ts

                msgs.append({
                    "role": msg_type,
                    "text": text,
                    "created_at": ts,
                })

        if not msgs:
            return None

        first_user = next((m for m in msgs if m["role"] == "user"), None)
        title = ""
        if first_user:
            title = first_user["text"][:80].replace("\n", " ")

        ft = title + " " + " ".join(m["text"] for m in msgs)
        created = first_ts or ""
        updated = last_ts or created

        return {
            "id": session_id,
            "title": title,
            "created_at": created,
            "updated_at": updated,
            "messages": msgs,
            "full_text": ft,
            "message_count": len(msgs),
            "source": "claude-code",
            "project": project_dir,
        }

    # ── claude.ai normalize ──────────────────────────

    def _norm_web(self, raw, idx):
        uid = raw.get("uuid") or raw.get("id") or raw.get("conversation_id") or f"conv_{idx}"
        title = raw.get("name") or raw.get("title") or ""
        created = raw.get("created_at") or raw.get("create_time") or ""
        updated = raw.get("updated_at") or raw.get("update_time") or created
        msgs = self._msgs_web(raw)
        if not msgs:
            return None
        ft = title + " " + " ".join(m["text"] for m in msgs)
        return {"id": uid, "title": title, "created_at": created,
                "updated_at": updated, "messages": msgs,
                "full_text": ft, "message_count": len(msgs),
                "source": "claude-ai"}

    def _msgs_web(self, raw):
        """Parse 3 message format patterns."""
        msgs = []

        if "chat_messages" in raw:
            for m in raw["chat_messages"]:
                txt = ""
                if isinstance(m.get("content"), list):
                    txt = " ".join(
                        c.get("text", "") for c in m["content"]
                        if isinstance(c, dict) and c.get("type") == "text"
                    )
                elif isinstance(m.get("content"), str):
                    txt = m["content"]
                else:
                    txt = m.get("text", "")
                s = m.get("sender", m.get("role", "unknown"))
                msgs.append({
                    "role": "user" if s in ("human", "user") else "assistant",
                    "text": txt,
                    "created_at": m.get("created_at", ""),
                })

        elif "messages" in raw:
            for m in raw["messages"]:
                r = m.get("role", m.get("sender", ""))
                txt = m.get("content", m.get("text", ""))
                if isinstance(txt, list):
                    txt = " ".join(
                        c.get("text", "") for c in txt if isinstance(c, dict)
                    )
                if r in ("user", "human", "assistant"):
                    msgs.append({
                        "role": "user" if r in ("user", "human") else "assistant",
                        "text": str(txt),
                        "created_at": m.get("created_at", ""),
                    })

        elif "mapping" in raw:
            for node in raw["mapping"].values():
                m = node.get("message")
                if not m:
                    continue
                r = m.get("author", {}).get("role", "")
                if r not in ("user", "assistant"):
                    continue
                parts = m.get("content", {}).get("parts", [])
                txt = " ".join(str(p) for p in parts if isinstance(p, str))
                msgs.append({"role": r, "text": txt, "created_at": ""})

        return msgs

    # ── Index ────────────────────────────────────────

    def _build(self):
        n = len(self.conversations)
        if n == 0:
            return
        for i, c in enumerate(self.conversations):
            for t in set(self._tok(c["full_text"])):
                self.inv[t].add(i)
        for t, ids in self.inv.items():
            self.idf[t] = math.log(n / (1 + len(ids)))

    def _tok(self, text):
        """Tokenizer for mixed Japanese/English: words for EN, unigram+bigram for JA."""
        text = text.lower()
        tokens = re.findall(
            r"[a-z0-9]+|[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]+", text
        )
        exp = []
        for t in tokens:
            if re.match(r"[a-z0-9]+", t):
                exp.append(t)
            else:
                for ch in t:
                    exp.append(ch)
                for j in range(len(t) - 1):
                    exp.append(t[j : j + 2])
        return exp

    # ── Search ───────────────────────────────────────

    def search(self, query, max_results=5, source=None):
        self.load()
        qt = self._tok(query)
        if not qt:
            return []
        sc = defaultdict(float)
        for t in qt:
            if t in self.inv:
                iv = self.idf.get(t, 1.0)
                for did in self.inv[t]:
                    sc[did] += iv
        ranked = sorted(sc.items(), key=lambda x: x[1], reverse=True)
        res = []
        for did, score in ranked:
            if len(res) >= max_results:
                break
            c = self.conversations[did]
            if source and c.get("source") != source:
                continue
            snip = self._snip(c, set(qt))
            entry = {
                "id": c["id"], "title": c["title"],
                "created_at": c["created_at"], "updated_at": c["updated_at"],
                "message_count": c["message_count"],
                "source": c.get("source", "unknown"),
                "score": round(score, 3), "snippet": snip,
            }
            if c.get("project"):
                entry["project"] = c["project"]
            res.append(entry)
        return res

    def recent(self, n=5, before=None, after=None, source=None):
        self.load()
        fl = self.conversations[:]
        if source:
            fl = [c for c in fl if c.get("source") == source]
        if before:
            fl = [c for c in fl if c["updated_at"] < before]
        if after:
            fl = [c for c in fl if c["updated_at"] > after]
        fl.sort(key=lambda c: c["updated_at"], reverse=True)
        res = []
        for c in fl[:n]:
            sm = []
            if c["messages"]:
                sm.append(c["messages"][0]["text"][:200])
                if len(c["messages"]) > 1:
                    sm.append(c["messages"][-1]["text"][:200])
            entry = {
                "id": c["id"], "title": c["title"],
                "created_at": c["created_at"], "updated_at": c["updated_at"],
                "message_count": c["message_count"],
                "source": c.get("source", "unknown"),
                "summary": " ... ".join(sm),
            }
            if c.get("project"):
                entry["project"] = c["project"]
            res.append(entry)
        return res

    def get(self, cid):
        self.load()
        for c in self.conversations:
            if c["id"] == cid:
                result = {
                    "id": c["id"], "title": c["title"],
                    "created_at": c["created_at"], "updated_at": c["updated_at"],
                    "messages": c["messages"],
                    "source": c.get("source", "unknown"),
                }
                if c.get("project"):
                    result["project"] = c["project"]
                return result
        return None

    def _snip(self, conv, qs):
        bm, bs = "", 0
        for m in conv["messages"]:
            ov = len(set(self._tok(m["text"])) & qs)
            if ov > bs:
                bs = ov
                bm = m["text"]
        return bm[:300] + ("..." if len(bm) > 300 else "")

    def stats(self):
        self.load()
        web_count = sum(1 for c in self.conversations if c.get("source") == "claude-ai")
        code_count = sum(1 for c in self.conversations if c.get("source") == "claude-code")
        return {
            "total_conversations": len(self.conversations),
            "claude_ai_conversations": web_count,
            "claude_code_conversations": code_count,
            "total_messages": sum(c["message_count"] for c in self.conversations),
            "index_terms": len(self.inv),
            "data_dir": str(DATA_DIR.resolve()),
            "claude_code_dir": str(CLAUDE_CODE_DIR.resolve()),
        }


# -- Singleton --
ix = ConversationIndex()


# -- MCP Tools --

@mcp.tool()
def conversation_search(query: str, max_results: int = 5, source: str = None) -> str:
    """Search past Claude conversations by keyword.
    Searches both claude.ai and Claude Code local history.
    Args:
        query: search keywords (Japanese/English)
        max_results: max results (1-20)
        source: filter by source — "claude-ai" or "claude-code" (optional, default: both)
    """
    max_results = min(max(1, max_results), 20)
    r = ix.search(query, max_results, source=source)
    if not r:
        return json.dumps({"message": "no results", "results": []}, ensure_ascii=False)
    return json.dumps({"results": r}, ensure_ascii=False, indent=2)


@mcp.tool()
def recent_chats(n: int = 5, before: str = None, after: str = None, source: str = None) -> str:
    """Get recent conversations chronologically.
    Args:
        n: number of chats (1-20)
        before: before this datetime (ISO 8601)
        after: after this datetime (ISO 8601)
        source: filter by source — "claude-ai" or "claude-code" (optional)
    """
    n = min(max(1, n), 20)
    r = ix.recent(n, before=before, after=after, source=source)
    return json.dumps({"results": r}, ensure_ascii=False, indent=2)


@mcp.tool()
def get_conversation(conversation_id: str) -> str:
    """Get full messages of a conversation by ID.
    Use IDs from conversation_search or recent_chats results.
    """
    c = ix.get(conversation_id)
    if not c:
        return json.dumps({"error": "not found"}, ensure_ascii=False)
    return json.dumps(c, ensure_ascii=False, indent=2)


@mcp.tool()
def history_stats() -> str:
    """Show index statistics. Use to verify data is loaded correctly."""
    return json.dumps(ix.stats(), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()

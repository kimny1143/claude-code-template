"""claude-history-mcp: Claude Code -> claude.ai conversation history search MCP server"""

import json, os, re, math
from pathlib import Path
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

DATA_DIR = Path(os.environ.get("CLAUDE_HISTORY_DIR", "./data"))
mcp = FastMCP("claude-history", description="claude.ai conversation history search")


class ConversationIndex:
    """In-memory TF-IDF index over exported claude.ai conversations."""

    def __init__(self):
        self.conversations = []
        self.inv = defaultdict(set)
        self.idf = {}
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        jfiles = [f for f in sorted(DATA_DIR.glob("*.json")) if f.name != "_index.json"]
        all_c = []
        for jf in jfiles:
            with open(jf, "r", encoding="utf-8") as f:
                d = json.load(f)
                all_c.extend(d) if isinstance(d, list) else all_c.append(d)
        for i, c in enumerate(all_c):
            n = self._norm(c, i)
            if n:
                self.conversations.append(n)
        self._build()
        self._loaded = True

    # -- Normalize: supports multiple claude.ai export formats --

    def _norm(self, raw, idx):
        uid = raw.get("uuid") or raw.get("id") or raw.get("conversation_id") or f"conv_{idx}"
        title = raw.get("name") or raw.get("title") or ""
        created = raw.get("created_at") or raw.get("create_time") or ""
        updated = raw.get("updated_at") or raw.get("update_time") or created
        msgs = self._msgs(raw)
        if not msgs:
            return None
        ft = title + " " + " ".join(m["text"] for m in msgs)
        return {"id": uid, "title": title, "created_at": created,
                "updated_at": updated, "messages": msgs,
                "full_text": ft, "message_count": len(msgs)}

    def _msgs(self, raw):
        """Parse 3 message format patterns."""
        msgs = []

        # Pattern 1: chat_messages (claude.ai standard export)
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

        # Pattern 2: messages array (generic)
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

        # Pattern 3: mapping (OpenAI-style, fallback)
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

    # -- Index --

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

    # -- Search --

    def search(self, query, max_results=5):
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
        for did, score in ranked[:max_results]:
            c = self.conversations[did]
            snip = self._snip(c, set(qt))
            res.append({
                "id": c["id"], "title": c["title"],
                "created_at": c["created_at"], "updated_at": c["updated_at"],
                "message_count": c["message_count"],
                "score": round(score, 3), "snippet": snip,
            })
        return res

    def recent(self, n=5, before=None, after=None):
        self.load()
        fl = self.conversations[:]
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
            res.append({
                "id": c["id"], "title": c["title"],
                "created_at": c["created_at"], "updated_at": c["updated_at"],
                "message_count": c["message_count"],
                "summary": " ... ".join(sm),
            })
        return res

    def get(self, cid):
        self.load()
        for c in self.conversations:
            if c["id"] == cid:
                return {
                    "id": c["id"], "title": c["title"],
                    "created_at": c["created_at"], "updated_at": c["updated_at"],
                    "messages": c["messages"],
                }
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
        return {
            "total_conversations": len(self.conversations),
            "total_messages": sum(c["message_count"] for c in self.conversations),
            "index_terms": len(self.inv),
            "data_dir": str(DATA_DIR.resolve()),
        }


# -- Singleton --
ix = ConversationIndex()


# -- MCP Tools (same names as claude.ai built-in tools) --

@mcp.tool()
def conversation_search(query: str, max_results: int = 5) -> str:
    """Search past claude.ai conversations by keyword.
    Args:
        query: search keywords (Japanese/English)
        max_results: max results (1-20)
    """
    max_results = min(max(1, max_results), 20)
    r = ix.search(query, max_results)
    if not r:
        return json.dumps({"message": "no results", "results": []}, ensure_ascii=False)
    return json.dumps({"results": r}, ensure_ascii=False, indent=2)


@mcp.tool()
def recent_chats(n: int = 5, before: str = None, after: str = None) -> str:
    """Get recent conversations chronologically.
    Args:
        n: number of chats (1-20)
        before: before this datetime (ISO 8601)
        after: after this datetime (ISO 8601)
    """
    n = min(max(1, n), 20)
    r = ix.recent(n, before=before, after=after)
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

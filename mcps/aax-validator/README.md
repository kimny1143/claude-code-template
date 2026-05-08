# aax-validator MCP server

AAX plugin bundle (.aaxplugin) の structure / manifest / iLok署名 を Pro Tools build verification 前に自動validateする MCP server。**MUEDsp v1 Phase 5 (5/14- AAX版自社サイトリリース、Avid Developer Program審査連動) の critical infra layer**。

詳細: [.claude/skills/aax-validator/SKILL.md](../../.claude/skills/aax-validator/SKILL.md)

## Phase

- **0.1** ✅ (5/9): MCP server skeleton + 3 tools (validate_bundle / check_signature / validate_manifest) frame
- **0.2** (5/13 EOD): structural validation 全項目 + manifest schema 完納 + pytest fixture-based tests
- **1.0** (5/14-): PACE Connect SDK wiring + iLok署名 real check (kimny task #73 5/10完納後)
- **2.0** (5/22以降): Pro Tools 自動build test integration

## install / 起動

```bash
cd mcps/aax-validator
python3.10 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# stand-alone server起動
python server.py
```

## Claude Code への登録 (Phase 1.0以降)

`.mcp.json` に追加 (現段階stub、5/14- full wiring完納後):

```json
{
  "mcpServers": {
    "aax-validator": {
      "command": "python",
      "args": ["/abs/path/to/mcps/aax-validator/server.py"]
    }
  }
}
```

## MCP tools

### `mcp__aax-validator__validate_bundle`

```json
{"bundle_path": "/path/to/MyPlugin.aaxplugin"}
→ {
    "passed": true,
    "violations": [],
    "summary": "0 error, 0 warning"
  }
```

check項目:
- directory構造 (`Contents/MacOS/` / `Contents/Resources/` / `Contents/Info.plist`)
- Info.plist 必須keys (`CFBundleIdentifier` / `CFBundleVersion` / `CFBundleExecutable`)
- executable存在 + universal binary check (`lipo -info`)
- `Contents/Resources/AAXManifest.xml` 存在 (詳細schemaは validate_manifest)

### `mcp__aax-validator__check_signature`

```json
{"bundle_path": "/path/to/MyPlugin.aaxplugin"}
→ {
    "signed": false,
    "signature_status": "sdk_pending",
    "ilok_authorized": null,
    "pace_framework_present": true,
    "violations": [],
    "note": "Phase 0.1 stub: real iLok signature check requires PACE Connect SDK..."
  }
```

**Phase 0.1 stub**: PACE_AntiPiracy.framework presence check のみ。real署名check は Phase 1.0 wiring (kimny task #73 5/10完納後)。

### `mcp__aax-validator__validate_manifest`

```json
{"manifest_path": "/path/to/AAXManifest.xml"}
→ {
    "valid": false,
    "missing_required": ["AAXEffectID"],
    "invalid_values": [
      {"field": "AAXPluginID", "value": "abc", "reason": "expected UUID format"}
    ],
    "parse_errors": [],
    "summary": "1 missing, 1 invalid"
  }
```

check項目:
- XML/plist parse wellformedness
- 必須elements (`AAXPluginID` / `AAXEffectID` / `AAXPlugInVersion` / `AAXManufacturerID`)
- value制約 (UUID format / semver / 4-char manufacturer code)

## tests

```bash
cd mcps/aax-validator
source .venv/bin/activate
pytest -v
```

## SDK受領後 wiring (Phase 1.0、5/14-)

kimny task #73 (5/10着手予定) 完納で以下受領:
- AAX SDK (Avid Developer Program)
- PACE Connect SDK (PACE Anti-Piracy)
- iLok License Manager API

これらを `check_signature` 内に wiring:
- AAX SDK公式 manifest schema との照合
- PACE Connect SDK で executable preamble の wrapper有無 + hash verify
- iLok License Manager API で license signal status check

## 関連

- skill: [.claude/skills/aax-validator/SKILL.md](../../.claude/skills/aax-validator/SKILL.md)
- MUEDsp v1設計書: `_mued-dsp/_docs/MUEDsp_v1_design.md` Phase 5
- plan file: `~/.claude/plans/partitioned-wandering-scroll.md`
- conductor authorization: 5/9 04:10 JST claude-peers受領

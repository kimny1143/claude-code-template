---
name: aax-validator
description: >
  AAX plugin bundle (.aaxplugin) の structure / manifest / iLok署名 を Pro Tools build verification前に
  自動validateする MCP server skill。Avid Developer Program審査前 self-validation で kimny工数最小化。
  使用タイミング: (1) iPlug2 build後 (2) Avid審査提出前 self-check (3) iLok署名後 verify
  (4) MUEDsp Phase 5 (5/14- AAX target build) 各段階。
---

# aax-validator — AAX bundle / iLok署名 validation MCP server

## 概要

AAX plugin (.aaxplugin) bundle structureの自動validation MCP server。**Pro Tools build verification 自動化** + **Avid審査前 self-validation** で kimny検証依存解消 + 審査リジェクトリスク低減。

**位置付け**: MUEDsp v1 Phase 5 (5/14- AAX版自社サイトリリース、Avid Developer Program審査連動) を支える critical infra。AAX SDK受領 (kimny task #73 5/10完納待ち) 前に **MCP frame + structural validation logic** を draft化、SDK受領後 (5/14-) full wiring。

## なぜMCP serverか

- **Claude Code session内で直接呼べる**: `mcp__aax-validator__validate_bundle <path>` で会話内validation結果取得
- **build pipeline integration**: `iplug2-build-pipeline` skill (#1) が build後に自動validate呼び出し
- **CI/quality gate**: pytest + MCP tool として両用、commit前 quality gate準拠

## MCP tools (3個)

### 1. `mcp__aax-validator__validate_bundle`

AAX bundle (.aaxplugin) directory全体の structure validation。

**input**:
- `bundle_path` (str): `.aaxplugin` directory絶対path

**check項目**:
- directory構造 (`Contents/` / `Contents/MacOS/` / `Contents/Resources/` / `Contents/Info.plist`)
- Info.plist 必須keys (`CFBundleIdentifier`, `CFBundleVersion`, `CFBundleExecutable`)
- executable binary存在 + Mach-O / universal binary check (`lipo -info` 相当)
- AAX manifest存在 (`Contents/Resources/AAXManifest.xml` or `.plist`)

**output**: JSON `{passed: bool, violations: [{path, level, message}, ...], summary: str}`

### 2. `mcp__aax-validator__check_signature`

iLok署名状態 + PACE Anti-Piracy wrapper check。

**input**:
- `bundle_path` (str): `.aaxplugin` directory絶対path

**check項目**:
- PACE wrapper detection (executable preamble check)
- iLok license信号 (placeholder: AAX SDK受領後 PACE Connect SDK連携で実装)
- 署名失敗の典型パターン3種 (unsigned / expired cert / wrong cert chain) のerror message分類

**output**: JSON `{signed: bool, signature_status: str, ilok_authorized: bool|null, violations: [...]}`

**Phase 0 (5/9-5/13 draft)**: stub実装 — `signed=False, signature_status="sdk_pending"` 返却 + AAX SDK受領後 (5/14-) wiring計画明示。

### 3. `mcp__aax-validator__validate_manifest`

AAX manifest XML/plist の schema validation。

**input**:
- `manifest_path` (str): `AAXManifest.xml` または `Info.plist` 絶対path

**check項目**:
- XML/plist syntax wellformedness
- 必須elements (`AAXPluginID`, `AAXEffectID`, `AAXPlugInVersion`, `AAXManufacturerID`)
- value制約 (UUID format / version semver / manufacturer 4-char code)
- Pro Tools compatibility minimum version記述

**output**: JSON `{valid: bool, missing_required: [], invalid_values: [], summary: str}`

## 使用例

### Claude Code session内
```
> mcp__aax-validator__validate_bundle({"bundle_path": "/path/to/MyPlugin.aaxplugin"})

{
  "passed": false,
  "violations": [
    {"path": "Contents/Resources/AAXManifest.xml", "level": "error", "message": "missing required: AAXEffectID"}
  ],
  "summary": "1 error, 0 warnings"
}
```

### iplug2-build-pipeline (#1) integration想定
```bash
# build後の自動validation
python -m iplug2_build_pipeline build --target aax
mcp_validate_bundle ./build/MyPlugin.aaxplugin  # MCP tool call (CCO frame想定)
```

## AAX bundle structure (参考)

```
MyPlugin.aaxplugin/
└── Contents/
    ├── Info.plist                    # macOS bundle metadata
    ├── MacOS/
    │   └── MyPlugin                  # Mach-O executable (universal binary推奨)
    ├── Resources/
    │   ├── AAXManifest.xml           # AAX固有 manifest
    │   ├── icon.png
    │   └── PluginResources/...
    └── Frameworks/
        └── PACE_AntiPiracy.framework  # iLok wrapper (PACE Connect SDK)
```

## 実装layer

- **Python 3.10+**
- **mcp[cli]** (FastMCP server)
- **lxml** (XML schema validation、optional fallback to xml.etree)
- **plistlib** (標準ライブラリ、plist parse)
- **subprocess** (`lipo -info` / `codesign -dvvv` 相当 macOS-native check)

**SDK依存** (5/14- full wiring段階):
- AAX SDK (Avid Developer Program受領)
- PACE Connect SDK (PACE Anti-Piracy契約受領)
- 未受領段階 (5/9-5/13 draft) は signature関連 stub実装

## Phase / ロードマップ

| Phase | 機能 | 完納目処 |
|-------|------|---------|
| 0.1 | SKILL.md draft + MCP server skeleton (3 tools stub) | 5/9 EOD (本) |
| 0.2 | structural validation (bundle directory / Info.plist / manifest schema) 実装 | 5/13 EOD draft |
| 1.0 | PACE Connect SDK wiring + iLok署名real check | 5/14- (kimny task #73完納後) |
| 2.0 | Avid Pro Tools 自動build test integration (Pro Tools CLI連携、要kimny検証) | 5/22以降 |

## 関連skill

- `iplug2-build-pipeline` (#1) — AAX target build成果物を本MCPでvalidate
- `ilok-signing-flow` (#4) — 署名後の本MCP `check_signature` で verify
- `dsp-rta-comparison` (#2) — DSP正確性validation (本MCPはbinary/署名layer、相補的)
- `mcp` (template課既存) — MCPサーバ作成・設定patterns
- `coding-rules` — Python命名規則・型ヒント

## 配布判断

- `.mcp.json` への登録: 5/14- full wiring完納後検討 (現段階stubのため自peer内のみ起動test)
- 配布対象: dsp peer + native peer (build連携) → 5/22 通常peer体制移行時に検討

## 関連リソース

- 設計書: `_mued-dsp/_docs/MUEDsp_v1_design.md` Phase 5 (5/14- 着手)
- plan file: `~/.claude/plans/partitioned-wandering-scroll.md`
- AAX format公式 (Avid Developer Program受領後): "AAX SDK Documentation" / "Pro Tools Plugin Validation Guide"
- PACE iLok公式: ilok.com developer documentation (PACE Connect SDK)
- conductor authorization: 5/9 04:10 JST claude-peers受領 (本日着手承認)

# aax-validator Phase 1 prep design draft (5/14- SDK受領後 wiring)

**起案**: template課 (CCO) — 2026-05-09
**Tier判定**: Tier 3 (新規外部SDK連携 + 全課波及 infra) → conductor承認後 kimny task #73 SDK受領 (5/10予定) → 5/14- 実装着手
**status**: design draft — implementation 未着手 (kimny task #73 完納待ち)

## 目的

Phase 0.1-0.3 で完納した structural validation (`validate_bundle` / `validate_manifest`) に加えて、Phase 1.0 で **iLok署名 real check** (`check_signature`) を wiring。kimny task #73 (PACE Connect SDK受領) を blocker としつつ、**offline-completable 部分は task #73 受領前に着手** (本draft、5/9-5/13)。

## Phase scope

| Phase | 完納目処 | scope | dependency |
|-------|---------|-------|-----------|
| 0.1 ✅ | 5/9 | 3 tools skeleton | なし |
| 0.2 ✅ | 5/9 | structural validation full coverage (87 tests) | なし |
| 0.3 ✅ | 5/9 | parametric fixture builder + integration tests | なし |
| **1 prep** | **5/13 EOD** | **本draft + offline fixture自動generation logic + SDK integration interface 設計** | **なし (offline完結)** |
| 1.0 | 5/22- | PACE Connect SDK wiring + iLok real check | kimny task #73 (5/14受領目処) |
| 2.0 | 6/1- | Pro Tools auto build test integration | Avid Developer Program審査 (5/14- 申請) |

## Phase 1 prep の3 deliverable (5/13 EOD完納目処、offline完結)

### 1. offline-completable fixture自動generation logic

現状の `tests/fixture_builder.py` は **structural placeholder** (executable bytes は `b"\x00\x00\x00\x00" + arch_marker`、PACE framework は空 directory のみ) で、real binary / signed bundle simulation は未対応。

Phase 1 prep で追加する fixture generation:

#### 1a. signed bundle simulator (offline)

PACE Connect SDK wiring 後の `check_signature` が判定する **wrapper marker** を offline で再現:

```python
# AAXBundleBuilder 拡張案
def with_pace_signed_marker(
    self,
    signed: bool = True,
    ilok_authorized: bool = True,
    signature_metadata: dict | None = None,
) -> AAXBundleBuilder:
    """signed bundle marker simulation (Phase 1.0 SDK wiring 前 fallback)."""
    self._pace_signed = signed
    self._ilok_authorized = ilok_authorized
    self._signature_metadata = signature_metadata or {}
    return self
```

**build時挙動**:
- `signed=True` → `Frameworks/PACE_AntiPiracy.framework/_PACE_SIGNED_MARKER` (sentinel file) 配置
- `ilok_authorized=True` → `Frameworks/PACE_AntiPiracy.framework/_ILOK_AUTHORIZED_MARKER` 配置
- `signature_metadata` → `Frameworks/PACE_AntiPiracy.framework/Resources/signature_metadata.plist` 配置

→ `check_signature` 内で **real SDK call失敗時の fallback path** として marker check を実装 (Phase 1.0 wiring中の SDK install 未完納環境でも tests pass を担保)。

#### 1b. binary architecture simulator (Mach-O magic byte)

現状の `_check_executable` は magic bytes `\xCA\xFE\xBA\xBE` (universal2) の検出を試みるが、AAXBundleBuilder は placeholder bytes のみ生成。Phase 1 prep で **fake Mach-O fat header** generation を追加:

```python
# fixture_builder.py 拡張案
FAT_MAGIC = b"\xCA\xFE\xBA\xBE"
ARM64_CPUTYPE = 0x0100000C
X86_64_CPUTYPE = 0x01000007

def _generate_fake_fat_header(arch_set: set[str]) -> bytes:
    """nfat_arch + fat_arch entries の fake header 生成 (binary parse test用)."""
    archs = sorted(arch_set)
    n = len(archs)
    body = FAT_MAGIC + n.to_bytes(4, "big")
    for arch in archs:
        cputype = ARM64_CPUTYPE if arch == "arm64" else X86_64_CPUTYPE
        body += cputype.to_bytes(4, "big") + b"\x00" * 16  # cpusubtype/offset/size/align stub
    return body
```

→ `_check_executable` の `lipo -info` 呼び出しを **fake header parse path** で代替可能にする (CI環境で `lipo` 未install / Linux runner 対応)。

#### 1c. AAX manifest schema enrichment (real schema追従)

現状の `validate_manifest` は 4 required + 3 optional element check のみ。Phase 1 prep で **AAX SDK公式 manifest schema** (Avid公開分) に追従:

- `AAXProductCategory` → 14 categoriesの enum check (Phase 0.3 で追加済)
- `AAXPlugInCategory` (新規追加検討、SDK manifest例に存在) → enum check
- `AAXMeterTypes` (新規追加検討、analyzer plugin用) → 整数 list check
- `AAXSupportsAudioSuite` (新規追加検討、AudioSuite対応plugin marker) → bool check

→ AAX SDK受領後 (5/14-) に公式 schema 確認して enum値最終化。**現段階 schema enrichment は draft only、SDK受領前 commit禁止** (実 schema 違いの risk)。

### 2. SDK integration interface 設計

`server.py` の `check_signature` を **SDK plug-in point** として明示化:

```python
# server.py 拡張案 (Phase 1 prep design)

class SignatureChecker:
    """signature check の SDK plug-in interface。

    Phase 0.1: stub implementation (sdk_pending返却)
    Phase 1.0: PaceSignatureChecker (PACE Connect SDK wiring) に差し替え
    test: FakeSignatureChecker (marker-based simulator) で offline test担保
    """

    def check(self, bundle_path: Path) -> SignatureResult:
        raise NotImplementedError


class StubSignatureChecker(SignatureChecker):
    """Phase 0.1 stub: 常に sdk_pending返却。"""

    def check(self, bundle_path: Path) -> SignatureResult:
        return SignatureResult(
            signed=False,
            signature_status="sdk_pending",
            ilok_authorized=None,
        )


class MarkerSignatureChecker(SignatureChecker):
    """Phase 1 prep: offline-completable (fixture marker file 検出ベース)。

    Phase 1.0 wiring 前の test/CI 環境用。real SDK 不要。
    """

    def check(self, bundle_path: Path) -> SignatureResult:
        pace_dir = bundle_path / "Contents" / "Frameworks" / "PACE_AntiPiracy.framework"
        signed = (pace_dir / "_PACE_SIGNED_MARKER").exists()
        ilok = (pace_dir / "_ILOK_AUTHORIZED_MARKER").exists()
        return SignatureResult(
            signed=signed,
            signature_status="marker_simulated" if signed else "unsigned",
            ilok_authorized=ilok if signed else None,
        )


# Phase 1.0 で追加予定:
# class PaceSignatureChecker(SignatureChecker):
#     """PACE Connect SDK wiring (kimny task #73 完納後)."""
#     def check(self, bundle_path: Path) -> SignatureResult:
#         # PACE SDK call → signed/ilok status 取得
#         ...


# instance選択 (env variable / config経由):
def _get_signature_checker() -> SignatureChecker:
    mode = os.environ.get("AAX_SIG_CHECKER", "stub")
    if mode == "marker":
        return MarkerSignatureChecker()
    if mode == "pace" and _pace_sdk_available():
        from .pace_signature import PaceSignatureChecker
        return PaceSignatureChecker()
    return StubSignatureChecker()
```

**transition path**:
1. **5/9-5/13 (Phase 1 prep)**: `StubSignatureChecker` + `MarkerSignatureChecker` 実装、`AAX_SIG_CHECKER=marker` で test通過
2. **5/14-5/21 (kimny task #73受領後)**: `PaceSignatureChecker` 追加実装、real binary に対して `AAX_SIG_CHECKER=pace` で動作確認
3. **5/22- (Phase 1.0完納)**: Avid Developer Program審査前 self-validation で `pace` モード default化

### 3. test coverage matrix (offline vs SDK必須の境界明示)

| 検証項目 | Phase 0.2 | Phase 1 prep | Phase 1.0 (SDK後) |
|---------|----------|--------------|-------------------|
| directory structure | ✅ offline | — | — |
| Info.plist required keys | ✅ offline | — | — |
| binary architecture (lipo) | ✅ offline (lipo必須) | ✅ offline (fake fat header) | — |
| AAX manifest required elements | ✅ offline | — | — |
| AAX manifest enum (category) | ✅ offline | — | — |
| AAX manifest schema enrichment | — | 🔄 design only | ✅ SDK受領後 |
| Resources asset (icon) | ✅ offline | — | — |
| PACE framework presence | ✅ offline (warning) | ✅ offline | ✅ SDK後 (error条件化) |
| **PACE signed marker** | — | ✅ offline (marker simulator) | — |
| **iLok authorized status** | — | ✅ offline (marker simulator) | ✅ real SDK call |
| **signature timestamp** | — | — | ✅ real SDK call |
| **certificate chain** | — | — | ✅ real SDK call |
| Pro Tools build test | — | — | Phase 2.0 |

→ **Phase 1 prep完納後**: 全 offline-completable 検証 100% 完納、SDK受領後 wiring箇所明確化 (`PaceSignatureChecker` 1 class追加のみ、既存test全 pass維持)。

## kimny task #73 dependency

| 受領物 | 用途 | 受領期日目処 |
|-------|------|------------|
| PACE Connect SDK (PACE社) | iLok real signature check API | 5/10予定 |
| AAX SDK (Avid Developer Program) | manifest schema 公式版 + Pro Tools build test API | 5/14- (Avid審査連動) |
| iLok USB key (kimny保有) | physical signature検証時 | 既受領 |

**現段階 (5/9 EOD) 着手可能項目**:
- ✅ deliverable 1a-1c (offline fixture自動generation logic)
- ✅ deliverable 2 (SDK integration interface 設計、stub/marker class実装)
- 🔄 deliverable 3 (test coverage matrix明示) ← 本draft

**SDK受領待ち項目** (本draft scope外):
- PACE Connect SDK API 呼び出し実装 (`PaceSignatureChecker`)
- AAX SDK schema最終確認 (manifest enrichment 1c の実 enum値)
- Avid Developer Program審査前 self-validation 統合

## 想定される implementation cost

| 作業 | LOC見積 | 工数 |
|------|--------|------|
| AAXBundleBuilder 拡張 (1a + 1b) | +80 | 1h |
| server.py SignatureChecker class階層 (deliverable 2) | +120 | 2h |
| test_validator.py marker simulator tests | +60 | 1h |
| test_integration.py marker simulator integration | +40 | 0.5h |
| docs/drafts/ → README.md / SKILL.md 反映 | +50 | 1h |
| **計** | **+350 LOC** | **5.5h** |

→ **5/13 EOD単日完納可能**、PR sequence: PR #56/#59 conductor merge後 → Phase 1 prep PR着手。

## 5/14- SDK受領後の implementation cost (参考、本draft scope外)

| 作業 | LOC見積 | 工数 |
|------|--------|------|
| PaceSignatureChecker 実装 (PACE SDK wiring) | +100 | 3h |
| AAX manifest schema enrichment (実 enum値確定) | +50 | 1h |
| real binary signed/unsigned 両方の test fixture追加 | +80 | 2h |
| Avid審査前 self-validation runbook | +30 | 1h |
| **計** | **+260 LOC** | **7h** |

## Open questions (kimny / conductor承認事項)

1. **PACE Connect SDK受領経路**: kimny task #73 で **PACE社直接 SDK受領** か、**Avid Developer Program経由** (AAX SDK同梱) か、どちら想定か → 受領経路次第で `PaceSignatureChecker` 実装ABI 差異 risk。
2. **`AAX_SIG_CHECKER` env variable許容**: stub/marker/pace の env制御は最低限の plug-in pattern として妥当か、**`.mcp.json` 内 args経由** に変更すべきか → MCP server起動時 mode指定方式の選好。
3. **Phase 1.0 完納目処の前倒し可否**: kimny task #73 5/10受領 + Phase 1 prep 5/13完納の場合、**Phase 1.0 を 5/22 → 5/17-5/19 前倒し** できる可能性あり、kimny / conductor承認下りる場合は前倒し実行。

## 関連ドキュメント

- `mcps/aax-validator/server.py` (Phase 0.1-0.2 implementation)
- `mcps/aax-validator/tests/fixture_builder.py` (Phase 0.3 prep — 拡張対象)
- `mcps/aax-validator/README.md` (Phase 1.0以降 .mcp.json登録instructions)
- `.claude/skills/aax-validator/SKILL.md` (使用タイミング / トリガー条件)
- kimny task #73 (PACE Connect SDK受領、5/10予定)
- Avid Developer Program審査 (5/14- 申請、AAX SDK受領連動)

## 5/9 EOD時点 完納evidence (本draft根拠)

- PR #53 (aax-validator MCP Phase 0.1) squash merged: `4d9cb6e`
- PR #57 (Phase 0.3 prep — parametric fixture builder + integration tests 87/87 pass) squash merged: `846a7a6`
- 累計pytest: 87/87 pass (server.py 47 + fixture_builder integration 40)
- AAXBundleBuilder fluent pattern確立 → Phase 1 prep deliverable 1a-1c の foundation

---
name: dsp-rta-comparison
description: >
  DSP実機 (Shadow Hills / Kirchhoff EQ / Pro-L 2 等) 出力 vs 自実装出力の差分を
  自動計測する quality gate skill。MUEDsp開発で kimny検聴依存scaling解消 + commit前 機械的check。
  使用タイミング: (1) 新DSP module実装完納時 (2) regression test (既存module update時)
  (3) kimny検聴前の機械的quality check (4) MUEDsp Phase 1-3 (Limiter / Glue Comp / Dynamic EQ) 各実装時。
---

# dsp-rta-comparison — DSP実機比較自動テストフレーム

## 概要

DSP plugin開発で「実機 (commercial plugin) 出力」 vs 「自実装出力」 の差分を自動計測し、人間検聴前の **機械的 quality gate** を提供する。MUEDsp v1 開発で kimny検聴依存scaling解消 (合計1-2時間範囲内に kimny工数を収める) ための critical infra。

**位置付け**: MUEDsp_v1_design.md §4.1 「DSP生成 → 検聴ループの運用設計」を実装するskill。Claude Codeはこのテストが通った状態でしかcommit不可、kimnyの検聴は「個別モジュールの音」ではなく「チェーン全体の最終音」に集中。

## なぜ必要か

- **scaling問題**: DSP module 1個実装時に5-10回iterate × 比較対象3-5実機 × 既知入力4種類 = 60-200比較ペア = kimny検聴 unscaling
- **regression防止**: 既存module update時に他module への影響検出が手動では困難
- **commit前 quality gate**: 自動テスト pass までcommit不可ルール (設計書 §4.1) を実装可能化

## 使用方法

### CLI

```bash
# 1ペア比較
python -m lib \
  --reference reference/shadow_hills_sin1k.wav \
  --test test-output/my_comp_sin1k.wav \
  --output reports/comparison_$(date +%Y%m%d).md

# batch比較 (ディレクトリ全体)
python -m lib \
  --reference-dir reference/ \
  --test-dir test-output/ \
  --output-dir reports/
```

### pytest integration (commit前 quality gate)

```python
from lib import compare, ComparisonResult

def test_glue_comp_matches_shadow_hills():
    result: ComparisonResult = compare(
        reference="reference/shadow_hills_pinknoise.wav",
        test="test-output/glue_comp_pinknoise.wav",
        thresholds={
            "spectrum_diff_max_db": 1.5,    # spectrum -1.5/+1.5 dB以内
            "transient_diff_ms": 5.0,        # transient ±5ms以内
            "lufs_diff": 0.3,                 # LUFS ±0.3以内
            "tp_diff_db": 0.2,                # TP ±0.2 dB以内
        }
    )
    assert result.passed, result.report
```

## 比較対象とリファレンス入力

### 比較対象 commercial plugin (MUEDsp v1スコープ)

| Plugin | maker | MUEDsp v1 ステージ |
|--------|-------|-------------------|
| Shadow Hills Mastering Compressor | Brainworx | ステージ1 Glue Comp |
| Kirchhoff EQ | TBTECH | ステージ2 Dynamic EQ |
| Pro-L 2 | FabFilter | ステージ3 True Peak Limiter |

### 既知入力 (input wavs、 reference/ 配下)

| input名 | 用途 | 必須 |
|---------|------|------|
| `sin_1k_-12dBFS.wav` | sine 1kHz、ピーク-12dBFS、5秒 | 周波数応答 |
| `impulse.wav` | impulse 1 sample、48kHz、0.5秒 | impulse response |
| `pink_noise_-20LUFS.wav` | pink noise、-20LUFS、10秒 | spectrum + dynamic |
| `reference_master.wav` | kimny指定マスター音源 | 実運用近似 |

実機wav録音 = MUEDsp dsp peer Phase 1着手時に kimny依頼 (`feedback_zero_kimny_manual_work.md` 整合、CCO設計時のkimny工数発生回避)。

## 計測項目

### 1. Spectrum Diff (周波数応答差分)

- 1/3 octave band毎の dB差分
- threshold: ±1.5 dB (Glue Comp) / ±0.5 dB (EQ) / ±0.3 dB (Limiter Modern style)

### 2. Transient Response (時間応答差分)

- attack/release時間の deviation
- threshold: ±5ms (Comp) / ±0.1ms (Limiter lookahead)

### 3. LUFS / TP / Dynamic Range

- Integrated LUFS差分 (BS.1770-4)
- True Peak差分 (8x oversampling)
- Dynamic Range (PLR / EBU R128)

### 4. Phase Response (位相応答)

- minimum phase EQ実装verify
- linear phase mode (Kirchhoff相当) detection

## pass/fail判定

```python
@dataclass
class ComparisonResult:
    passed: bool
    spectrum_diff_max_db: float
    transient_diff_ms: float
    lufs_diff: float
    tp_diff_db: float
    phase_alignment: float
    report: str  # markdown report
```

threshold外 = `passed=False` + `report` で違反項目を明示。

## 実装layer

- **Python 3.11+**
- **librosa** (spectrum / chroma / onset)
- **numpy / scipy** (signal processing)
- **pyloudnorm** (BS.1770-4 LUFS)
- **pytest** (既存 `tdd` skill流用、commit前 quality gate)

## 関連skill

- `tdd` — pytest integration、TDDワークフロー
- `coding-rules` — Python命名規則・型ヒント
- `git-worktree` — Phase 1-3 並行開発時のbranch管理
- `iplug2-build-pipeline` (#1) — 自実装ビルド出力 → test-output/連携
- `ab-audio-comparison` (#5) — 機械test pass後の kimny ABX聴感評価

## ロードマップ

| Phase | 機能 | 完納目処 |
|-------|------|---------|
| 0.1 | SKILL.md draft + ディレクトリ構造 | 5/9 EOD (本) |
| 0.2 | core lib (spectrum/transient/LUFS) + pytest sample | 5/10-5/11 |
| 0.3 | CLI wrapper + markdown report | 5/11 EOD |
| 1.0 | Phase 1着手時 dsp peer連携 + kimny録音wav受領 → end-to-end稼働 | 5/14- |

## 既知の制約

- **比較対象実機の license**: kimny保有 (Brainworx Shadow Hills / TBTECH Kirchhoff / FabFilter Pro-L 2)、3rd party検証では別途License必要
- **threshold tuning**: 初期値は MUEDsp_v1_design.md §2 のチェーン設定根拠、kimny検聴 cross-validateで微調整 (Phase 1-3反復)
- **AAX target binary differences**: AAX format特有の sample alignment / iLok wrapper分はテスト対象外 (#3 aax-validator MCP担当)

## 関連リソース

- 設計書: `_mued-dsp/_docs/MUEDsp_v1_design.md` (5/9 AAX先行版)
- plan file: `~/.claude/plans/partitioned-wandering-scroll.md`
- handoff memory: `project_handoff_20260509.md`

# dsp-rta-comparison

DSP実機 (Shadow Hills / Kirchhoff EQ / Pro-L 2 等) 出力 vs 自実装出力の差分自動計測 quality gate。MUEDsp Phase 1-3 開発で kimny検聴依存scaling解消 + commit前 機械的check。

詳細: `SKILL.md` 参照。

## Phase

- **0.1** ✅ (5/9): skeleton + dataclass + pytest sample
- **0.2** ✅ (5/9): core lib実装 (spectrum / transient / loudness / phase) + 20/20 pytest pass
- **0.3** ✅ (5/9): CLI wrapper (`python -m lib`) + markdown report + batch比較対応
- **1.0** (5/14-): Phase 1着手時 dsp peer連携 + kimny録音wav受領 → end-to-end稼働

## CI / pytest

```bash
cd .claude/skills/dsp-rta-comparison
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
# expect: 20 passed
```

## CLI

```bash
# 1ペア比較
python -m lib \
  --reference reference/shadow_hills_pinknoise.wav \
  --test test-output/glue_comp_pinknoise.wav \
  --output reports/comparison.md

# batch比較 (同一 stem 名でペア)
python -m lib \
  --reference-dir reference/ \
  --test-dir test-output/ \
  --output-dir reports/

# 終了コード: 0=PASS / 1=FAIL (CI quality gate)
```

## thresholds custom

```json
// thresholds.json (例: Limiter Modern style)
{
  "spectrum_diff_max_db": 0.3,
  "transient_diff_ms": 0.1,
  "lufs_diff": 0.2,
  "tp_diff_db": 0.1,
  "phase_alignment_min": 0.95
}
```

```bash
python -m lib --reference ... --test ... --thresholds-json thresholds.json
```

## pytest integration (commit前 quality gate)

```python
from lib import compare

def test_glue_comp_matches_shadow_hills():
    result = compare(
        reference="reference/shadow_hills_pinknoise.wav",
        test="test-output/glue_comp_pinknoise.wav",
        thresholds={"spectrum_diff_max_db": 1.5, "lufs_diff": 0.3},
    )
    assert result.passed, result.report
```

## 実装layer

- Python 3.11+
- numpy / scipy (spectrum / cross-correlation / coherence / resample)
- pyloudnorm (BS.1770-4 LUFS)
- soundfile (wav I/O)
- pytest (commit前 quality gate)

> Note: librosa は pyproject.toml に宣言済だが Phase 0.2 内では未使用 (numpy/scipyで完結)。Phase 1.0以降の高度な特徴量 (chroma / onset 等) で使用予定。

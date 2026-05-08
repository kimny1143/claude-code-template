# dsp-rta-comparison

DSP実機 (Shadow Hills / Kirchhoff EQ / Pro-L 2 等) 出力 vs 自実装出力の差分自動計測 quality gate。MUEDsp Phase 1-3 開発で kimny検聴依存scaling解消 + commit前 機械的check。

詳細: `SKILL.md` 参照。

## Phase

- **0.1** (5/9 EOD): skeleton + dataclass + pytest sample (current)
- **0.2** (5/10-5/11): core lib実装 (spectrum / transient / LUFS / phase)
- **0.3** (5/11 EOD): CLI wrapper + markdown report
- **1.0** (5/14-): Phase 1着手時 dsp peer連携 + kimny録音wav受領 → end-to-end稼働

## CI / pytest

```bash
cd .claude/skills/dsp-rta-comparison
pip install -e ".[dev]"
pytest
```

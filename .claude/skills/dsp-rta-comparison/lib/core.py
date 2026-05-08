"""Core comparison API (skeleton). Phase 0.2で各moduleを実装する。"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ComparisonThresholds:
    """各計測項目の pass/fail threshold."""

    spectrum_diff_max_db: float = 1.5
    transient_diff_ms: float = 5.0
    lufs_diff: float = 0.3
    tp_diff_db: float = 0.2
    phase_alignment_min: float = 0.95


@dataclass
class ComparisonResult:
    """比較結果。passed=False時はreport markdownに違反項目を明示。"""

    passed: bool
    spectrum_diff_max_db: float
    transient_diff_ms: float
    lufs_diff: float
    tp_diff_db: float
    phase_alignment: float
    report: str = field(default="")


def compare(
    reference: str | Path,
    test: str | Path,
    thresholds: ComparisonThresholds | dict | None = None,
) -> ComparisonResult:
    """実機reference wav vs 自実装test wav の差分計測。

    Phase 0.2 で実装予定:
        - spectrum diff (1/3 octave band)
        - transient response (attack/release deviation)
        - LUFS / TP / DR (BS.1770-4)
        - phase alignment

    現在 (Phase 0.1) は skeleton のみ、NotImplementedError raise。
    """
    raise NotImplementedError(
        "dsp_rta_comparison.compare() is in Phase 0.1 skeleton state. "
        "Phase 0.2 (5/10-5/11) で実装予定。"
    )

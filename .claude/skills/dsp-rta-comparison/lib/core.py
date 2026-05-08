"""Core comparison API. Phase 0.2実装。"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

import numpy as np

from .io import load_wav
from .loudness import loudness_diff
from .phase import phase_alignment
from .report import render_report
from .spectrum import spectrum_diff
from .transient import transient_diff


@dataclass
class ComparisonThresholds:
    """各計測項目の pass/fail threshold。

    initial値は MUEDsp_v1_design.md §4.1 Glue Comp 想定。EQ / Limiter は呼出側で上書き。
    """

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


SignalLike = Union[str, Path, np.ndarray]


def _coerce_signal(
    src: SignalLike, sr: int | None
) -> tuple[np.ndarray, int]:
    if isinstance(src, np.ndarray):
        if sr is None:
            raise ValueError("ndarray入力時はsr (sample rate) を明示すること")
        return src, sr
    signal, loaded_sr = load_wav(src)
    return signal, loaded_sr


def _normalize_thresholds(
    thresholds: ComparisonThresholds | dict | None,
) -> ComparisonThresholds:
    if thresholds is None:
        return ComparisonThresholds()
    if isinstance(thresholds, ComparisonThresholds):
        return thresholds
    return ComparisonThresholds(**thresholds)


def compare(
    reference: SignalLike,
    test: SignalLike,
    thresholds: ComparisonThresholds | dict | None = None,
    sr: int | None = None,
) -> ComparisonResult:
    """実機reference wav vs 自実装test wav の差分計測。

    引数:
        reference / test:
            wav file path または numpy array (sr必須)。
        thresholds:
            ComparisonThresholds または dict、未指定時はdefault (Glue Comp想定)。
        sr:
            ndarray入力時のsample rate指定。

    返り値:
        ComparisonResult (markdown report含む)。
    """
    th = _normalize_thresholds(thresholds)

    ref_signal, ref_sr = _coerce_signal(reference, sr)
    test_signal, test_sr = _coerce_signal(test, sr)

    if ref_sr != test_sr:
        raise ValueError(
            f"sample rate mismatch: reference={ref_sr}Hz, test={test_sr}Hz"
        )
    sr_used = ref_sr

    ref_mono = ref_signal if ref_signal.ndim == 1 else ref_signal.mean(axis=1)
    test_mono = test_signal if test_signal.ndim == 1 else test_signal.mean(axis=1)
    n = min(len(ref_mono), len(test_mono))
    ref_mono = ref_mono[:n]
    test_mono = test_mono[:n]

    spec = spectrum_diff(ref_mono, test_mono, sr_used)
    trans = transient_diff(ref_mono, test_mono, sr_used)
    loud = loudness_diff(ref_signal, test_signal, sr_used)
    ph = phase_alignment(ref_mono, test_mono, sr_used)

    spectrum_pass = abs(spec.max_diff_db) <= th.spectrum_diff_max_db
    transient_pass = abs(trans.max_diff_ms) <= th.transient_diff_ms
    lufs_pass = abs(loud.lufs_diff) <= th.lufs_diff
    tp_pass = abs(loud.tp_diff_db) <= th.tp_diff_db
    phase_pass = ph.alignment >= th.phase_alignment_min

    passed = all(
        [spectrum_pass, transient_pass, lufs_pass, tp_pass, phase_pass]
    )

    result = ComparisonResult(
        passed=passed,
        spectrum_diff_max_db=spec.max_diff_db,
        transient_diff_ms=trans.max_diff_ms,
        lufs_diff=loud.lufs_diff,
        tp_diff_db=loud.tp_diff_db,
        phase_alignment=ph.alignment,
    )
    ref_label = str(reference) if not isinstance(reference, np.ndarray) else "<ndarray>"
    test_label = str(test) if not isinstance(test, np.ndarray) else "<ndarray>"
    result.report = render_report(result, th, ref_label, test_label)
    return result

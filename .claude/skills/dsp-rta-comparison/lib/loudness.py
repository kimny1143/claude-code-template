"""Loudness measurement: Integrated LUFS, True Peak (8x oversampled), Dynamic Range.

BS.1770-4 / EBU R128 準拠。pyloudnorm をベースに、TP は scipy 8x polyphase resample で算出。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class LoudnessDiffResult:
    lufs_diff: float
    tp_diff_db: float
    dr_diff: float
    reference_lufs: float
    reference_tp_db: float
    reference_dr: float
    test_lufs: float
    test_tp_db: float
    test_dr: float


def _to_mono(signal: np.ndarray) -> np.ndarray:
    if signal.ndim == 1:
        return signal
    return signal.mean(axis=1)


def integrated_lufs(signal: np.ndarray, sr: int) -> float:
    """BS.1770-4 integrated loudness (LUFS)。pyloudnorm が必要。"""
    import pyloudnorm as pyln

    meter = pyln.Meter(sr)
    return float(meter.integrated_loudness(signal))


def true_peak_db(signal: np.ndarray, sr: int, oversample: int = 8) -> float:
    """8x oversampling後の True Peak (dBFS)。"""
    from scipy.signal import resample_poly

    mono = _to_mono(signal)
    upsampled = resample_poly(mono, oversample, 1)
    peak = float(np.max(np.abs(upsampled)))
    eps = 1e-20
    return 20.0 * np.log10(max(peak, eps))


def dynamic_range(signal: np.ndarray, sr: int, window_ms: float = 400.0) -> float:
    """short-term loudness の P10/P95 比 (DR proxy、簡易PLR)。

    BS.1770短期ウィンドウで RMS-LUFS を算出し、上位5%と下位10%の差を返す。
    """
    mono = _to_mono(signal)
    win = int(sr * window_ms / 1000.0)
    if win < 1 or len(mono) < win:
        return 0.0
    hop = max(win // 4, 1)
    n_frames = (len(mono) - win) // hop + 1
    rms = np.empty(n_frames, dtype=np.float64)
    for i in range(n_frames):
        frame = mono[i * hop : i * hop + win]
        rms[i] = float(np.sqrt(np.mean(frame ** 2)))
    eps = 1e-20
    rms_db = 20.0 * np.log10(np.maximum(rms, eps))
    p95 = float(np.percentile(rms_db, 95))
    p10 = float(np.percentile(rms_db, 10))
    return p95 - p10


def loudness_diff(
    reference: np.ndarray,
    test: np.ndarray,
    sr: int,
) -> LoudnessDiffResult:
    ref_lufs = integrated_lufs(reference, sr)
    test_lufs = integrated_lufs(test, sr)
    ref_tp = true_peak_db(reference, sr)
    test_tp = true_peak_db(test, sr)
    ref_dr = dynamic_range(reference, sr)
    test_dr = dynamic_range(test, sr)

    return LoudnessDiffResult(
        lufs_diff=float(test_lufs - ref_lufs),
        tp_diff_db=float(test_tp - ref_tp),
        dr_diff=float(test_dr - ref_dr),
        reference_lufs=float(ref_lufs),
        reference_tp_db=float(ref_tp),
        reference_dr=float(ref_dr),
        test_lufs=float(test_lufs),
        test_tp_db=float(test_tp),
        test_dr=float(test_dr),
    )

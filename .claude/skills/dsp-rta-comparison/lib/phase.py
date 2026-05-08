"""Phase alignment via cross-correlation peak + magnitude-squared coherence.

reference / test wav の位相整合度 (0.0-1.0) を返す。1.0 = 完全整合。
EQ minimum-phase / linear-phase mode の verify用。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PhaseAlignmentResult:
    alignment: float
    lag_samples: int
    coherence_mean: float


def _to_mono(signal: np.ndarray) -> np.ndarray:
    if signal.ndim == 1:
        return signal
    return signal.mean(axis=1)


def _normalized_cross_correlation_peak(
    a: np.ndarray, b: np.ndarray, max_lag: int
) -> tuple[float, int]:
    """正規化cross-correlation の peak (-max_lag..+max_lag) を返す。"""
    eps = 1e-20
    a_norm = a / (np.linalg.norm(a) + eps)
    b_norm = b / (np.linalg.norm(b) + eps)
    n = len(a_norm)
    lags = np.arange(-max_lag, max_lag + 1)
    best_corr = -1.0
    best_lag = 0
    for lag in lags:
        if lag < 0:
            x = a_norm[: n + lag]
            y = b_norm[-lag : n]
        elif lag > 0:
            x = a_norm[lag : n]
            y = b_norm[: n - lag]
        else:
            x = a_norm
            y = b_norm
        if len(x) == 0:
            continue
        corr = float(np.dot(x, y))
        if corr > best_corr:
            best_corr = corr
            best_lag = int(lag)
    return best_corr, best_lag


def phase_alignment(
    reference: np.ndarray,
    test: np.ndarray,
    sr: int,
    max_lag_ms: float = 50.0,
) -> PhaseAlignmentResult:
    """位相整合度 [0,1]、サンプルlag、平均coherenceを返す。

    alignment は **reference power-weighted** magnitude-squared coherence で算出。
    無信号bandの数値ノイズが metricに混入することを避ける (sinusoid等の sparse spectrum対応)。
    """
    from scipy.signal import coherence, welch

    ref = _to_mono(reference).astype(np.float64)
    tst = _to_mono(test).astype(np.float64)
    n = min(len(ref), len(tst))
    ref = ref[:n]
    tst = tst[:n]

    max_lag = int(sr * max_lag_ms / 1000.0)
    max_lag = min(max_lag, n - 1)
    _, lag = _normalized_cross_correlation_peak(ref, tst, max_lag)

    nperseg = min(n, 4096)
    _, coh = coherence(ref, tst, fs=sr, nperseg=nperseg)
    _, ref_psd = welch(ref, fs=sr, nperseg=nperseg)

    weights = ref_psd / (ref_psd.sum() + 1e-20)
    weighted_coh = float(np.sum(coh * weights))
    unweighted_mean = float(np.mean(coh))

    return PhaseAlignmentResult(
        alignment=float(np.clip(weighted_coh, 0.0, 1.0)),
        lag_samples=lag,
        coherence_mean=unweighted_mean,
    )

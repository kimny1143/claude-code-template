"""1/3 octave band spectrum diff.

reference / test wav の周波数応答を 1/3 octave band で集約し、
band毎の dB差分の最大値を返す (spectrum_diff_max_db)。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ISO 266 / ANSI S1.11 1/3 octave band 中心周波数 (20Hz - 20kHz)
ONE_THIRD_OCTAVE_CENTERS_HZ: tuple[float, ...] = (
    25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200,
    250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
    2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000,
)


@dataclass
class SpectrumDiffResult:
    max_diff_db: float
    band_centers_hz: tuple[float, ...]
    diff_db_per_band: tuple[float, ...]
    reference_db_per_band: tuple[float, ...]
    test_db_per_band: tuple[float, ...]


def _band_edges_hz(centers: tuple[float, ...]) -> tuple[tuple[float, float], ...]:
    factor = 2.0 ** (1.0 / 6.0)
    return tuple((c / factor, c * factor) for c in centers)


def _power_spectrum(signal: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray]:
    """Welch's method power spectrum を返す (freq_hz, power)。"""
    from scipy.signal import welch

    nperseg = min(len(signal), 8192)
    freq, power = welch(
        signal, fs=sr, nperseg=nperseg, noverlap=nperseg // 2, scaling="density"
    )
    return freq, power


def _aggregate_to_bands(
    freq: np.ndarray,
    power: np.ndarray,
    centers: tuple[float, ...],
) -> np.ndarray:
    edges = _band_edges_hz(centers)
    band_power = np.empty(len(centers), dtype=np.float64)
    for i, (lo, hi) in enumerate(edges):
        mask = (freq >= lo) & (freq < hi)
        band_power[i] = power[mask].sum() if mask.any() else 0.0
    return band_power


def _to_db(power: np.ndarray, eps: float = 1e-20) -> np.ndarray:
    return 10.0 * np.log10(np.maximum(power, eps))


def spectrum_diff(
    reference: np.ndarray,
    test: np.ndarray,
    sr: int,
    band_centers_hz: tuple[float, ...] = ONE_THIRD_OCTAVE_CENTERS_HZ,
) -> SpectrumDiffResult:
    """reference vs test の 1/3 octave band 毎 dB差分を返す。

    sr が Nyquist 未満の上端bandは差分計算から除外 (NaN含み)。
    """
    valid_centers = tuple(c for c in band_centers_hz if c < sr / 2.0)

    ref_freq, ref_power = _power_spectrum(reference, sr)
    test_freq, test_power = _power_spectrum(test, sr)

    ref_band = _aggregate_to_bands(ref_freq, ref_power, valid_centers)
    test_band = _aggregate_to_bands(test_freq, test_power, valid_centers)

    ref_db = _to_db(ref_band)
    test_db = _to_db(test_band)
    diff_db = test_db - ref_db

    return SpectrumDiffResult(
        max_diff_db=float(np.max(np.abs(diff_db))),
        band_centers_hz=valid_centers,
        diff_db_per_band=tuple(float(x) for x in diff_db),
        reference_db_per_band=tuple(float(x) for x in ref_db),
        test_db_per_band=tuple(float(x) for x in test_db),
    )

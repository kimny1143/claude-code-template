"""Transient response (attack / release time) deviation.

reference / test wav の envelope を比較し、attack / release時間 (ms) の差分を返す。
Compressor / Limiter の time-domain整合をverifyするための指標。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TransientDiffResult:
    attack_diff_ms: float
    release_diff_ms: float
    max_diff_ms: float
    reference_attack_ms: float
    reference_release_ms: float
    test_attack_ms: float
    test_release_ms: float


def _envelope(signal: np.ndarray, sr: int, smoothing_ms: float = 1.0) -> np.ndarray:
    """RMS-style envelope follower (one-pole low-pass on |x|)。"""
    abs_signal = np.abs(signal)
    if smoothing_ms <= 0:
        return abs_signal
    alpha = float(np.exp(-1.0 / (sr * smoothing_ms / 1000.0)))
    env = np.empty_like(abs_signal, dtype=np.float64)
    env[0] = abs_signal[0]
    for i in range(1, len(abs_signal)):
        env[i] = alpha * env[i - 1] + (1.0 - alpha) * abs_signal[i]
    return env


def _attack_release_ms(env: np.ndarray, sr: int) -> tuple[float, float]:
    """envelope から attack / release時間を抽出。

    attack = 10% → 90% peakまでの時間
    release = 90% peak → 10% までの時間 (peak後)
    """
    peak_idx = int(np.argmax(env))
    peak = float(env[peak_idx])
    if peak <= 0:
        return 0.0, 0.0

    threshold_low = peak * 0.1
    threshold_high = peak * 0.9

    rising = env[: peak_idx + 1]
    above_low_indices = np.where(rising >= threshold_low)[0]
    above_high_indices = np.where(rising >= threshold_high)[0]
    if len(above_low_indices) == 0 or len(above_high_indices) == 0:
        attack_samples = 0
    else:
        attack_samples = int(above_high_indices[0] - above_low_indices[0])

    falling = env[peak_idx:]
    below_high_indices = np.where(falling <= threshold_high)[0]
    below_low_indices = np.where(falling <= threshold_low)[0]
    if len(below_high_indices) == 0 or len(below_low_indices) == 0:
        release_samples = 0
    else:
        release_samples = int(below_low_indices[0] - below_high_indices[0])

    return attack_samples / sr * 1000.0, release_samples / sr * 1000.0


def transient_diff(
    reference: np.ndarray,
    test: np.ndarray,
    sr: int,
    smoothing_ms: float = 1.0,
) -> TransientDiffResult:
    ref_env = _envelope(reference, sr, smoothing_ms)
    test_env = _envelope(test, sr, smoothing_ms)

    ref_attack, ref_release = _attack_release_ms(ref_env, sr)
    test_attack, test_release = _attack_release_ms(test_env, sr)

    attack_diff = test_attack - ref_attack
    release_diff = test_release - ref_release
    max_diff = max(abs(attack_diff), abs(release_diff))

    return TransientDiffResult(
        attack_diff_ms=float(attack_diff),
        release_diff_ms=float(release_diff),
        max_diff_ms=float(max_diff),
        reference_attack_ms=float(ref_attack),
        reference_release_ms=float(ref_release),
        test_attack_ms=float(test_attack),
        test_release_ms=float(test_release),
    )

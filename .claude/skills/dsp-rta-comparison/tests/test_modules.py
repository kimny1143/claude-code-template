"""Phase 0.2 module-level behavior tests (spectrum / transient / loudness / phase)。"""
from __future__ import annotations

import numpy as np
import pytest

from lib import (
    loudness_diff,
    phase_alignment,
    spectrum_diff,
    transient_diff,
)


# ---------- spectrum ----------

def test_spectrum_identical_returns_zero(pink_noise, sr):
    result = spectrum_diff(pink_noise, pink_noise, sr)
    assert result.max_diff_db == pytest.approx(0.0, abs=0.01)


def test_spectrum_band_centers_filtered_below_nyquist(pink_noise):
    sr = 24000
    result = spectrum_diff(pink_noise[: sr * 5], pink_noise[: sr * 5], sr)
    assert all(c < sr / 2.0 for c in result.band_centers_hz)


def test_spectrum_lpf_increases_max_diff(pink_noise, sr):
    """LPFをかけたtest signalは高域bandが下がるためmax_diff_db>0."""
    from scipy.signal import butter, sosfilt

    sos = butter(4, 1000.0, btype="low", fs=sr, output="sos")
    filtered = sosfilt(sos, pink_noise)
    result = spectrum_diff(pink_noise, filtered, sr)
    assert result.max_diff_db > 1.0


# ---------- transient ----------

def test_transient_identical_returns_zero(step, sr):
    result = transient_diff(step, step, sr)
    assert result.attack_diff_ms == pytest.approx(0.0, abs=0.01)
    assert result.release_diff_ms == pytest.approx(0.0, abs=0.01)


def test_transient_slowed_attack_detected(step, sr):
    """one-pole low-passをtestに追加するとattack時間が伸び、attack_diff_ms>0."""
    from scipy.signal import butter, sosfilt

    sos = butter(2, 50.0, btype="low", fs=sr, output="sos")
    slowed = sosfilt(sos, step)
    result = transient_diff(step, slowed, sr)
    assert result.attack_diff_ms > 1.0


# ---------- loudness ----------

def test_loudness_identical_returns_zero(pink_noise, sr):
    result = loudness_diff(pink_noise, pink_noise, sr)
    assert result.lufs_diff == pytest.approx(0.0, abs=0.01)
    assert result.tp_diff_db == pytest.approx(0.0, abs=0.05)


def test_loudness_attenuated_test_negative_lufs(pink_noise, sr):
    """test signal -6dB attenuation で lufs_diff ~ -6LU."""
    test = pink_noise * (10 ** (-6.0 / 20.0))
    result = loudness_diff(pink_noise, test, sr)
    assert result.lufs_diff == pytest.approx(-6.0, abs=0.5)


def test_loudness_tp_diff_negative_when_attenuated(pink_noise, sr):
    test = pink_noise * 0.5
    result = loudness_diff(pink_noise, test, sr)
    assert result.tp_diff_db < -5.0


# ---------- phase ----------

def test_phase_identical_alignment_one(sine_1k, sr):
    result = phase_alignment(sine_1k, sine_1k, sr)
    assert result.alignment >= 0.99
    assert result.lag_samples == 0


def test_phase_shifted_signal_lag_detected(sine_1k, sr):
    """test signalを 100 sample遅延させるとlag_samples ≈ -100。"""
    delayed = np.concatenate([np.zeros(100), sine_1k[:-100]])
    result = phase_alignment(sine_1k, delayed, sr)
    assert result.alignment >= 0.95  # coherence still high (same source)
    assert result.lag_samples == pytest.approx(-100, abs=2)


def test_phase_uncorrelated_alignment_low(pink_noise, sr):
    rng = np.random.default_rng(seed=99)
    other = rng.standard_normal(len(pink_noise)) * 0.3
    result = phase_alignment(pink_noise, other, sr)
    assert result.alignment < 0.5

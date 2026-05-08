"""pytest fixtures: synthetic audio inputs (sine / impulse / pink noise)。

実機wav録音 (Phase 1着手時 kimny依頼) を待たずに module behavior を verifyする。
"""
from __future__ import annotations

import numpy as np
import pytest


SR_DEFAULT = 48000


@pytest.fixture
def sr() -> int:
    return SR_DEFAULT


@pytest.fixture
def sine_1k(sr: int) -> np.ndarray:
    """1kHz sine、ピーク -12dBFS、5秒。"""
    duration_s = 5.0
    t = np.arange(int(sr * duration_s)) / sr
    amplitude = 10 ** (-12.0 / 20.0)
    return (amplitude * np.sin(2 * np.pi * 1000.0 * t)).astype(np.float64)


@pytest.fixture
def impulse(sr: int) -> np.ndarray:
    """impulse 1サンプル先頭、48kHzで0.5秒。"""
    duration_s = 0.5
    n = int(sr * duration_s)
    sig = np.zeros(n, dtype=np.float64)
    sig[0] = 1.0
    return sig


@pytest.fixture
def pink_noise(sr: int) -> np.ndarray:
    """簡易pink noise (Voss-McCartney algorithm 近似) 10秒。"""
    rng = np.random.default_rng(seed=42)
    duration_s = 10.0
    n = int(sr * duration_s)
    n_rows = 16
    array = rng.standard_normal((n_rows, n))
    sums = np.cumsum(array, axis=0)[-1]
    sig = sums / np.max(np.abs(sums))
    return (sig * 0.3).astype(np.float64)


@pytest.fixture
def step(sr: int) -> np.ndarray:
    """attack/release検証用 step input: 0 → 1 → 0、各1秒。"""
    seg = sr
    return np.concatenate(
        [
            np.zeros(seg // 4),
            np.ones(seg // 2) * 0.5,
            np.zeros(seg // 4),
        ]
    ).astype(np.float64)

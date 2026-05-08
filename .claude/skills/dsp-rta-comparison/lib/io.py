"""wav file I/O wrapper. soundfile依存を1箇所に閉じ込める。"""
from __future__ import annotations

from pathlib import Path

import numpy as np


def load_wav(path: str | Path) -> tuple[np.ndarray, int]:
    """wav file を読み込み、(signal, sr) を返す。

    multi-channel は下流で .ndim>1 として扱う。
    """
    import soundfile as sf

    signal, sr = sf.read(str(path), dtype="float64", always_2d=False)
    return signal, int(sr)

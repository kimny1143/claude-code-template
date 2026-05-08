"""dsp-rta-comparison — DSP実機 vs 自実装 出力差分自動計測 quality gate."""
from .core import ComparisonResult, ComparisonThresholds, compare
from .loudness import LoudnessDiffResult, loudness_diff
from .phase import PhaseAlignmentResult, phase_alignment
from .spectrum import SpectrumDiffResult, spectrum_diff
from .transient import TransientDiffResult, transient_diff

__all__ = [
    "compare",
    "ComparisonResult",
    "ComparisonThresholds",
    "spectrum_diff",
    "SpectrumDiffResult",
    "transient_diff",
    "TransientDiffResult",
    "loudness_diff",
    "LoudnessDiffResult",
    "phase_alignment",
    "PhaseAlignmentResult",
]
__version__ = "0.2.0"

"""dsp-rta-comparison — DSP実機 vs 自実装 出力差分自動計測 quality gate."""
from .core import compare, ComparisonResult, ComparisonThresholds

__all__ = ["compare", "ComparisonResult", "ComparisonThresholds"]
__version__ = "0.1.0"

"""Phase 0.1 skeleton tests. Phase 0.2でreal implementation tests追加予定。"""
import pytest

from lib import ComparisonResult, ComparisonThresholds, compare


def test_thresholds_default_values():
    """default thresholdsが MUEDsp_v1_design.md §4.1 整合の値で初期化される."""
    th = ComparisonThresholds()
    assert th.spectrum_diff_max_db == 1.5
    assert th.transient_diff_ms == 5.0
    assert th.lufs_diff == 0.3
    assert th.tp_diff_db == 0.2
    assert th.phase_alignment_min == 0.95


def test_compare_phase_01_skeleton_raises():
    """Phase 0.1 skeleton state = NotImplementedError raise を期待."""
    with pytest.raises(NotImplementedError, match="Phase 0.1 skeleton"):
        compare(reference="dummy.wav", test="dummy.wav")


def test_comparison_result_dataclass():
    """ComparisonResultが必要field全て含む dataclass."""
    result = ComparisonResult(
        passed=True,
        spectrum_diff_max_db=0.8,
        transient_diff_ms=2.1,
        lufs_diff=0.15,
        tp_diff_db=0.08,
        phase_alignment=0.98,
        report="all metrics within threshold",
    )
    assert result.passed is True
    assert result.report.startswith("all metrics")

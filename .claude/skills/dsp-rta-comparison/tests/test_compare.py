"""Phase 0.2 tests — synthetic input で各moduleと統合 compare() のbehavior verify。"""
from __future__ import annotations

import numpy as np
import pytest

from lib import (
    ComparisonResult,
    ComparisonThresholds,
    compare,
)


def test_thresholds_default_values():
    """default thresholdsが MUEDsp_v1_design.md §4.1 整合の値で初期化される."""
    th = ComparisonThresholds()
    assert th.spectrum_diff_max_db == 1.5
    assert th.transient_diff_ms == 5.0
    assert th.lufs_diff == 0.3
    assert th.tp_diff_db == 0.2
    assert th.phase_alignment_min == 0.95


def test_thresholds_dict_override():
    """dict渡しで個別field override可能."""
    th = ComparisonThresholds(spectrum_diff_max_db=0.5, lufs_diff=0.1)
    assert th.spectrum_diff_max_db == 0.5
    assert th.lufs_diff == 0.1
    assert th.transient_diff_ms == 5.0


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


def test_compare_identical_signals_passes(sine_1k, sr):
    """同一signal同士はthreshold内で全 pass."""
    result = compare(reference=sine_1k, test=sine_1k, sr=sr)
    assert result.passed is True
    assert result.spectrum_diff_max_db == pytest.approx(0.0, abs=0.01)
    assert result.lufs_diff == pytest.approx(0.0, abs=0.01)
    assert result.tp_diff_db == pytest.approx(0.0, abs=0.01)
    assert result.phase_alignment >= 0.99


def test_compare_ndarray_without_sr_raises(sine_1k):
    """ndarray入力時にsr未指定でValueError raise."""
    with pytest.raises(ValueError, match="ndarray入力時はsr"):
        compare(reference=sine_1k, test=sine_1k, sr=None)


def test_compare_attenuated_test_lufs_diff(pink_noise, sr):
    """test signalのLUFSが下がるとlufs_diff <0、threshold超過でFAIL."""
    test = pink_noise * 0.5  # ~6dB attenuation
    result = compare(
        reference=pink_noise,
        test=test,
        sr=sr,
        thresholds={"lufs_diff": 0.3, "spectrum_diff_max_db": 1.5},
    )
    assert result.lufs_diff < -3.0
    assert result.passed is False
    assert "lufs_diff" in result.report.lower()


def test_compare_filtered_test_spectrum_diff(pink_noise, sr):
    """test signalにLPFをかけるとspectrum_diff_max_db増加、threshold超過でFAIL."""
    from scipy.signal import butter, sosfilt

    sos = butter(4, 1000.0, btype="low", fs=sr, output="sos")
    filtered = sosfilt(sos, pink_noise)
    result = compare(reference=pink_noise, test=filtered, sr=sr)
    assert result.spectrum_diff_max_db > 1.5
    assert result.passed is False


def test_compare_returns_markdown_report(sine_1k, sr):
    """reportはmarkdown format (header + table) を含む."""
    result = compare(reference=sine_1k, test=sine_1k, sr=sr)
    assert "# DSP RTA Comparison Report" in result.report
    assert "| metric | value | threshold | verdict |" in result.report


def test_compare_thresholds_dict_input(sine_1k, sr):
    """thresholdsをdictで渡せる (pytest integration想定)."""
    result = compare(
        reference=sine_1k,
        test=sine_1k,
        sr=sr,
        thresholds={"spectrum_diff_max_db": 0.5, "lufs_diff": 0.1},
    )
    assert result.passed is True

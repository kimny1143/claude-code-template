"""Markdown report generator for ComparisonResult."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import ComparisonResult, ComparisonThresholds


def render_report(
    result: "ComparisonResult",
    thresholds: "ComparisonThresholds",
    reference_path: str,
    test_path: str,
) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines: list[str] = [
        f"# DSP RTA Comparison Report — {status}",
        "",
        f"- reference: `{reference_path}`",
        f"- test: `{test_path}`",
        "",
        "## Metrics vs Thresholds",
        "",
        "| metric | value | threshold | verdict |",
        "|--------|-------|-----------|---------|",
        _row(
            "spectrum_diff_max_db",
            result.spectrum_diff_max_db,
            thresholds.spectrum_diff_max_db,
            cmp="abs<=",
            unit="dB",
        ),
        _row(
            "transient_diff_ms",
            result.transient_diff_ms,
            thresholds.transient_diff_ms,
            cmp="abs<=",
            unit="ms",
        ),
        _row(
            "lufs_diff",
            result.lufs_diff,
            thresholds.lufs_diff,
            cmp="abs<=",
            unit="LU",
        ),
        _row(
            "tp_diff_db",
            result.tp_diff_db,
            thresholds.tp_diff_db,
            cmp="abs<=",
            unit="dB",
        ),
        _row(
            "phase_alignment",
            result.phase_alignment,
            thresholds.phase_alignment_min,
            cmp=">=",
            unit="",
        ),
    ]
    if not result.passed:
        lines += ["", "## Violations", ""]
        for v in _violations(result, thresholds):
            lines.append(f"- {v}")
    return "\n".join(lines) + "\n"


def _row(name: str, value: float, threshold: float, cmp: str, unit: str) -> str:
    if cmp == "abs<=":
        ok = abs(value) <= threshold
        rule = f"|x|<={threshold}{unit}"
    elif cmp == ">=":
        ok = value >= threshold
        rule = f">={threshold}"
    else:
        ok = True
        rule = ""
    verdict = "OK" if ok else "FAIL"
    return f"| {name} | {value:.3f}{unit} | {rule} | {verdict} |"


def _violations(
    result: "ComparisonResult", thresholds: "ComparisonThresholds"
) -> list[str]:
    out: list[str] = []
    if abs(result.spectrum_diff_max_db) > thresholds.spectrum_diff_max_db:
        out.append(
            f"spectrum_diff_max_db={result.spectrum_diff_max_db:.2f}dB exceeds ±{thresholds.spectrum_diff_max_db}dB"
        )
    if abs(result.transient_diff_ms) > thresholds.transient_diff_ms:
        out.append(
            f"transient_diff_ms={result.transient_diff_ms:.2f}ms exceeds ±{thresholds.transient_diff_ms}ms"
        )
    if abs(result.lufs_diff) > thresholds.lufs_diff:
        out.append(
            f"lufs_diff={result.lufs_diff:.2f}LU exceeds ±{thresholds.lufs_diff}LU"
        )
    if abs(result.tp_diff_db) > thresholds.tp_diff_db:
        out.append(
            f"tp_diff_db={result.tp_diff_db:.2f}dB exceeds ±{thresholds.tp_diff_db}dB"
        )
    if result.phase_alignment < thresholds.phase_alignment_min:
        out.append(
            f"phase_alignment={result.phase_alignment:.3f} below {thresholds.phase_alignment_min}"
        )
    return out

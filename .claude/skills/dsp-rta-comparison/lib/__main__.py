"""CLI wrapper: `python -m lib --reference <ref.wav> --test <test.wav> [--output <out.md>]`。

batch比較も対応 (`--reference-dir / --test-dir / --output-dir` で同一stemペア比較)。
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .core import ComparisonResult, ComparisonThresholds, compare


def _load_thresholds(path: str | None) -> ComparisonThresholds:
    if path is None:
        return ComparisonThresholds()
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return ComparisonThresholds(**data)


def _write_report(result: ComparisonResult, output_path: Path | None) -> None:
    if output_path is None:
        print(result.report)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.report, encoding="utf-8")


def _run_single(
    reference: Path,
    test: Path,
    thresholds: ComparisonThresholds,
    output: Path | None,
) -> bool:
    result = compare(reference=reference, test=test, thresholds=thresholds)
    _write_report(result, output)
    return result.passed


def _run_batch(
    reference_dir: Path,
    test_dir: Path,
    thresholds: ComparisonThresholds,
    output_dir: Path,
) -> tuple[int, int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    ref_files = sorted(reference_dir.glob("*.wav"))
    if not ref_files:
        print(f"warning: no .wav files in {reference_dir}", file=sys.stderr)
        return 0, 0

    passed = 0
    failed = 0
    summary_rows: list[dict] = []
    for ref_path in ref_files:
        test_path = test_dir / ref_path.name
        if not test_path.exists():
            print(f"skip: {ref_path.name} (no matching test wav)", file=sys.stderr)
            continue
        result = compare(reference=ref_path, test=test_path, thresholds=thresholds)
        out_path = output_dir / f"{ref_path.stem}.md"
        _write_report(result, out_path)
        if result.passed:
            passed += 1
        else:
            failed += 1
        summary_rows.append(
            {
                "input": ref_path.name,
                "passed": result.passed,
                "spectrum_diff_max_db": result.spectrum_diff_max_db,
                "transient_diff_ms": result.transient_diff_ms,
                "lufs_diff": result.lufs_diff,
                "tp_diff_db": result.tp_diff_db,
                "phase_alignment": result.phase_alignment,
            }
        )

    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(
            {"passed": passed, "failed": failed, "results": summary_rows},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return passed, failed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dsp_rta_comparison",
        description="DSP実機 vs 自実装出力 差分自動計測 quality gate",
    )
    parser.add_argument("--reference", type=Path, help="reference wav file")
    parser.add_argument("--test", type=Path, help="test wav file")
    parser.add_argument("--output", type=Path, help="出力markdown report path")
    parser.add_argument(
        "--reference-dir",
        type=Path,
        help="batch: reference wav directory (.wav stem matchで対応 test wavを自動選択)",
    )
    parser.add_argument(
        "--test-dir", type=Path, help="batch: test wav directory"
    )
    parser.add_argument(
        "--output-dir", type=Path, help="batch: 出力markdown reports directory"
    )
    parser.add_argument(
        "--thresholds-json",
        type=str,
        help="custom thresholds JSON file (default: ComparisonThresholds default)",
    )
    args = parser.parse_args(argv)

    thresholds = _load_thresholds(args.thresholds_json)

    is_single = args.reference is not None and args.test is not None
    is_batch = args.reference_dir is not None and args.test_dir is not None

    if is_single == is_batch:
        parser.error(
            "Specify either --reference + --test OR --reference-dir + --test-dir"
        )

    if is_single:
        passed = _run_single(args.reference, args.test, thresholds, args.output)
        return 0 if passed else 1

    output_dir = args.output_dir or Path("reports")
    n_pass, n_fail = _run_batch(
        args.reference_dir, args.test_dir, thresholds, output_dir
    )
    print(f"batch: {n_pass} pass / {n_fail} fail (reports: {output_dir})")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

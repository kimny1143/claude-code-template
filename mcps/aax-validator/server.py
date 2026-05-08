"""aax-validator MCP server: AAX plugin bundle / iLok署名 validation.

Phase 0.1 draft (5/9):
    - 3 MCP tools (validate_bundle / check_signature / validate_manifest) frame実装
    - structural validation logic (directory / Info.plist / AAX manifest schema) 実装
    - signature関連は AAX SDK + PACE Connect SDK 受領前のため stub (5/14- full wiring)

Phase 1.0 (5/14- kimny task #73完納後):
    - PACE Connect SDK wiring + iLok署名 real check
    - AAX SDK公式 manifest schema 連携
"""
from __future__ import annotations

import json
import plistlib
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("aax-validator")


# ============================================================
# 1. validate_bundle — directory structure + Info.plist + binary
# ============================================================

REQUIRED_INFO_PLIST_KEYS = (
    "CFBundleIdentifier",
    "CFBundleVersion",
    "CFBundleExecutable",
)


@dataclass
class Violation:
    path: str
    level: str  # "error" | "warning"
    message: str


def _check_directory_structure(bundle_path: Path) -> list[Violation]:
    """`.aaxplugin/Contents/` 配下の必須subdirectory check."""
    violations: list[Violation] = []
    contents = bundle_path / "Contents"
    if not contents.is_dir():
        violations.append(
            Violation(
                path=str(contents),
                level="error",
                message="missing required directory: Contents/",
            )
        )
        return violations

    for sub in ("MacOS", "Resources"):
        sub_path = contents / sub
        if not sub_path.is_dir():
            violations.append(
                Violation(
                    path=str(sub_path),
                    level="error",
                    message=f"missing required directory: Contents/{sub}/",
                )
            )

    info_plist = contents / "Info.plist"
    if not info_plist.is_file():
        violations.append(
            Violation(
                path=str(info_plist),
                level="error",
                message="missing required file: Contents/Info.plist",
            )
        )

    return violations


def _check_info_plist(bundle_path: Path) -> tuple[list[Violation], dict | None]:
    """Info.plist 必須keys check + 値返却."""
    violations: list[Violation] = []
    info_plist_path = bundle_path / "Contents" / "Info.plist"
    if not info_plist_path.is_file():
        return violations, None
    try:
        with open(info_plist_path, "rb") as fh:
            data = plistlib.load(fh)
    except Exception as exc:
        violations.append(
            Violation(
                path=str(info_plist_path),
                level="error",
                message=f"plist parse error: {exc}",
            )
        )
        return violations, None

    for key in REQUIRED_INFO_PLIST_KEYS:
        if key not in data:
            violations.append(
                Violation(
                    path=str(info_plist_path),
                    level="error",
                    message=f"Info.plist missing required key: {key}",
                )
            )
    return violations, data


def _check_executable(
    bundle_path: Path, info_plist: dict | None
) -> list[Violation]:
    """executable binary存在 + universal binary check (lipo -info 相当)."""
    violations: list[Violation] = []
    if info_plist is None:
        return violations
    exe_name = info_plist.get("CFBundleExecutable")
    if not exe_name:
        return violations
    exe_path = bundle_path / "Contents" / "MacOS" / exe_name
    if not exe_path.is_file():
        violations.append(
            Violation(
                path=str(exe_path),
                level="error",
                message=f"executable not found: Contents/MacOS/{exe_name}",
            )
        )
        return violations

    try:
        result = subprocess.run(
            ["lipo", "-info", str(exe_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = (result.stdout + result.stderr).strip()
        if "is not a fat file" in out and "Non-fat" not in out:
            pass  # single-arch binary OK as warning, not error
        elif "x86_64" in out and "arm64" in out:
            pass  # universal2 binary
        elif result.returncode != 0:
            violations.append(
                Violation(
                    path=str(exe_path),
                    level="warning",
                    message=f"lipo -info failed: {out}",
                )
            )
        if "is not a fat file" in out and "x86_64 arm64" not in out:
            violations.append(
                Violation(
                    path=str(exe_path),
                    level="warning",
                    message="not universal binary (Apple Silicon + Intel推奨)",
                )
            )
    except FileNotFoundError:
        violations.append(
            Violation(
                path=str(exe_path),
                level="warning",
                message="lipo not available (macOS only); skip binary arch check",
            )
        )
    except subprocess.TimeoutExpired:
        violations.append(
            Violation(
                path=str(exe_path),
                level="warning",
                message="lipo -info timeout",
            )
        )
    return violations


def _check_aax_manifest_present(bundle_path: Path) -> list[Violation]:
    """Resources/AAXManifest.xml の存在check (validate_manifest が schema詳細check)。"""
    violations: list[Violation] = []
    manifest_xml = bundle_path / "Contents" / "Resources" / "AAXManifest.xml"
    if not manifest_xml.is_file():
        violations.append(
            Violation(
                path=str(manifest_xml),
                level="error",
                message="missing AAX manifest: Contents/Resources/AAXManifest.xml",
            )
        )
    return violations


@mcp.tool()
def validate_bundle(bundle_path: str) -> str:
    """AAX bundle (.aaxplugin) directory structure validation.

    Args:
        bundle_path: `.aaxplugin` directory絶対path

    Returns:
        JSON string: {passed, violations: [{path, level, message}], summary}
    """
    p = Path(bundle_path).expanduser().resolve()
    violations: list[Violation] = []

    if not p.exists():
        return json.dumps(
            {
                "passed": False,
                "violations": [
                    asdict(
                        Violation(
                            path=str(p),
                            level="error",
                            message=f"bundle path not found: {p}",
                        )
                    )
                ],
                "summary": "bundle path not found",
            },
            ensure_ascii=False,
        )

    if not p.name.endswith(".aaxplugin"):
        violations.append(
            Violation(
                path=str(p),
                level="warning",
                message=f"path does not end with .aaxplugin: {p.name}",
            )
        )

    violations += _check_directory_structure(p)
    plist_violations, plist_data = _check_info_plist(p)
    violations += plist_violations
    violations += _check_executable(p, plist_data)
    violations += _check_aax_manifest_present(p)

    n_error = sum(1 for v in violations if v.level == "error")
    n_warn = sum(1 for v in violations if v.level == "warning")
    return json.dumps(
        {
            "passed": n_error == 0,
            "violations": [asdict(v) for v in violations],
            "summary": f"{n_error} error, {n_warn} warning",
        },
        ensure_ascii=False,
    )


# ============================================================
# 2. check_signature — iLok署名 + PACE wrapper (Phase 0.1 stub)
# ============================================================

@mcp.tool()
def check_signature(bundle_path: str) -> str:
    """iLok署名 + PACE Anti-Piracy wrapper status check.

    Phase 0.1 (5/9-5/13): stub返却。AAX SDK + PACE Connect SDK 受領前のため
    real check は Phase 1.0 (5/14- kimny task #73完納後) で wiring。

    Args:
        bundle_path: `.aaxplugin` directory絶対path

    Returns:
        JSON: {signed, signature_status, ilok_authorized, violations}
    """
    p = Path(bundle_path).expanduser().resolve()
    violations: list[dict] = []

    if not p.exists():
        return json.dumps(
            {
                "signed": False,
                "signature_status": "bundle_not_found",
                "ilok_authorized": None,
                "violations": [
                    {"path": str(p), "level": "error", "message": "bundle path not found"}
                ],
            },
            ensure_ascii=False,
        )

    pace_framework = p / "Contents" / "Frameworks" / "PACE_AntiPiracy.framework"
    pace_present = pace_framework.exists()
    if not pace_present:
        violations.append(
            {
                "path": str(pace_framework),
                "level": "warning",
                "message": "PACE_AntiPiracy.framework not detected (Phase 0.1 stub: 検証は5/14-)",
            }
        )

    return json.dumps(
        {
            "signed": False,
            "signature_status": "sdk_pending",
            "ilok_authorized": None,
            "pace_framework_present": pace_present,
            "violations": violations,
            "note": "Phase 0.1 stub: real iLok signature check requires PACE Connect SDK (kimny task #73 5/10予定 + AAX SDK受領後 5/14-)",
        },
        ensure_ascii=False,
    )


# ============================================================
# 3. validate_manifest — AAX manifest XML/plist schema
# ============================================================

REQUIRED_AAX_MANIFEST_ELEMENTS = (
    "AAXPluginID",
    "AAXEffectID",
    "AAXPlugInVersion",
    "AAXManufacturerID",
)

UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
SEMVER_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9.+-]+)?$")


def _parse_xml_manifest(manifest_path: Path) -> tuple[dict[str, str], list[str]]:
    """XML manifest を parse、{element_name: text_value} 返却。"""
    elements: dict[str, str] = {}
    parse_errors: list[str] = []
    try:
        tree = ET.parse(str(manifest_path))
    except ET.ParseError as exc:
        parse_errors.append(f"XML parse error: {exc}")
        return elements, parse_errors
    root = tree.getroot()
    for elem in root.iter():
        if elem.text and elem.tag not in elements:
            elements[elem.tag] = elem.text.strip()
    return elements, parse_errors


def _parse_plist_manifest(manifest_path: Path) -> tuple[dict[str, Any], list[str]]:
    parse_errors: list[str] = []
    try:
        with open(manifest_path, "rb") as fh:
            data = plistlib.load(fh)
        return data, parse_errors
    except Exception as exc:
        parse_errors.append(f"plist parse error: {exc}")
        return {}, parse_errors


def _validate_manifest_values(elements: dict[str, Any]) -> list[dict]:
    invalid: list[dict] = []

    plugin_id = elements.get("AAXPluginID", "")
    if plugin_id and not UUID_PATTERN.match(str(plugin_id)):
        invalid.append(
            {
                "field": "AAXPluginID",
                "value": str(plugin_id),
                "reason": "expected UUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)",
            }
        )

    version = elements.get("AAXPlugInVersion", "")
    if version and not SEMVER_PATTERN.match(str(version)):
        invalid.append(
            {
                "field": "AAXPlugInVersion",
                "value": str(version),
                "reason": "expected semver (e.g. 1.0.0 / 1.0.0-beta1)",
            }
        )

    mfr = elements.get("AAXManufacturerID", "")
    if mfr and len(str(mfr)) != 4:
        invalid.append(
            {
                "field": "AAXManufacturerID",
                "value": str(mfr),
                "reason": "expected 4-character code (Avid registered manufacturer ID)",
            }
        )

    return invalid


@mcp.tool()
def validate_manifest(manifest_path: str) -> str:
    """AAX manifest XML/plist schema validation.

    Args:
        manifest_path: `AAXManifest.xml` または `Info.plist` 絶対path

    Returns:
        JSON: {valid, missing_required, invalid_values, summary, parse_errors}
    """
    p = Path(manifest_path).expanduser().resolve()
    if not p.is_file():
        return json.dumps(
            {
                "valid": False,
                "missing_required": [],
                "invalid_values": [],
                "parse_errors": [f"manifest not found: {p}"],
                "summary": "manifest not found",
            },
            ensure_ascii=False,
        )

    if p.suffix.lower() == ".xml":
        elements, parse_errors = _parse_xml_manifest(p)
    elif p.suffix.lower() == ".plist":
        elements, parse_errors = _parse_plist_manifest(p)
    else:
        return json.dumps(
            {
                "valid": False,
                "missing_required": [],
                "invalid_values": [],
                "parse_errors": [
                    f"unsupported manifest format: {p.suffix} (.xml or .plist required)"
                ],
                "summary": "unsupported format",
            },
            ensure_ascii=False,
        )

    if parse_errors:
        return json.dumps(
            {
                "valid": False,
                "missing_required": [],
                "invalid_values": [],
                "parse_errors": parse_errors,
                "summary": "parse error",
            },
            ensure_ascii=False,
        )

    missing = [
        field for field in REQUIRED_AAX_MANIFEST_ELEMENTS if field not in elements
    ]
    invalid = _validate_manifest_values(elements)
    valid = not missing and not invalid
    return json.dumps(
        {
            "valid": valid,
            "missing_required": missing,
            "invalid_values": invalid,
            "parse_errors": [],
            "summary": (
                "ok"
                if valid
                else f"{len(missing)} missing, {len(invalid)} invalid"
            ),
        },
        ensure_ascii=False,
    )


# ============================================================
# entrypoint
# ============================================================

if __name__ == "__main__":
    mcp.run()

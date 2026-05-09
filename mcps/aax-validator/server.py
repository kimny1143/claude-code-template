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


def _detect_architectures(exe_path: Path) -> tuple[set[str], str | None]:
    """`lipo -info` で binary が含む architecture set を返す。

    Returns:
        (archs, error_message): 検出失敗時 archs=空集合 + error_messageに理由
    """
    try:
        result = subprocess.run(
            ["lipo", "-info", str(exe_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return set(), "lipo not available (macOS only)"
    except subprocess.TimeoutExpired:
        return set(), "lipo -info timeout"

    if result.returncode != 0:
        return set(), f"lipo -info failed: {(result.stdout + result.stderr).strip()}"

    out = (result.stdout + result.stderr).strip()
    archs: set[str] = set()
    for token in ("x86_64", "arm64", "i386", "ppc", "ppc64"):
        if token in out:
            archs.add(token)
    return archs, None


def _check_executable(
    bundle_path: Path, info_plist: dict | None
) -> list[Violation]:
    """executable binary存在 + architecture detection (universal2 / single-arch)."""
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

    archs, err = _detect_architectures(exe_path)
    if err is not None:
        violations.append(
            Violation(
                path=str(exe_path),
                level="warning",
                message=f"architecture detection skipped: {err}",
            )
        )
        return violations

    if not archs:
        violations.append(
            Violation(
                path=str(exe_path),
                level="warning",
                message="no recognized architecture detected (binary may be invalid)",
            )
        )
        return violations

    has_arm64 = "arm64" in archs
    has_x86_64 = "x86_64" in archs
    if has_arm64 and has_x86_64:
        return violations  # universal2 OK
    if has_arm64 and not has_x86_64:
        violations.append(
            Violation(
                path=str(exe_path),
                level="warning",
                message="single-arch arm64 binary (Intel Mac非対応、universal2推奨)",
            )
        )
    elif has_x86_64 and not has_arm64:
        violations.append(
            Violation(
                path=str(exe_path),
                level="warning",
                message="single-arch x86_64 binary (Apple Silicon非ネイティブ、universal2推奨)",
            )
        )
    else:
        violations.append(
            Violation(
                path=str(exe_path),
                level="error",
                message=f"unsupported architecture set: {sorted(archs)} (arm64 / x86_64 必須)",
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


def _check_resources(bundle_path: Path) -> list[Violation]:
    """Resources/配下の推奨asset check (icon / PluginResources等)。"""
    violations: list[Violation] = []
    resources = bundle_path / "Contents" / "Resources"
    if not resources.is_dir():
        return violations
    icon_candidates = [
        resources / "icon.png",
        resources / "icon.icns",
        resources / "Icon.png",
    ]
    if not any(p.is_file() for p in icon_candidates):
        violations.append(
            Violation(
                path=str(resources),
                level="warning",
                message="recommended asset missing: icon.png / icon.icns (Pro Tools UI表示推奨)",
            )
        )
    return violations


def _check_pace_framework(bundle_path: Path) -> list[Violation]:
    """Frameworks/PACE_AntiPiracy.framework の存在check (warning)。"""
    violations: list[Violation] = []
    pace = bundle_path / "Contents" / "Frameworks" / "PACE_AntiPiracy.framework"
    if not pace.exists():
        violations.append(
            Violation(
                path=str(pace),
                level="warning",
                message="PACE_AntiPiracy.framework not detected (Avid審査前 iLok署名必須、Phase 1.0で full check)",
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
    violations += _check_resources(p)
    violations += _check_pace_framework(p)

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

OPTIONAL_AAX_MANIFEST_ELEMENTS = (
    "AAXPlugInName",
    "AAXProductCategory",
    "AAXMinProToolsVersion",
)

VALID_PRODUCT_CATEGORIES = frozenset(
    {
        "EQ",
        "Dynamics",
        "PitchShift",
        "Reverb",
        "Delay",
        "Modulation",
        "Harmonic",
        "NoiseReduction",
        "Dither",
        "SoundField",
        "Effect",
        "Instrument",
        "MIDIEffect",
        "Other",
    }
)

UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
SEMVER_PATTERN = re.compile(r"^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9.+-]+)?$")
FOUR_CHAR_CODE_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9]{3}$")
PROTOOLS_VERSION_PATTERN = re.compile(r"^\d+(\.\d+){1,2}$")


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

    effect_id = elements.get("AAXEffectID", "")
    if effect_id and not FOUR_CHAR_CODE_PATTERN.match(str(effect_id)):
        invalid.append(
            {
                "field": "AAXEffectID",
                "value": str(effect_id),
                "reason": "expected 4-character code starting with uppercase letter (e.g. EFCT, Eq01)",
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
    if mfr:
        mfr_str = str(mfr)
        if len(mfr_str) != 4:
            invalid.append(
                {
                    "field": "AAXManufacturerID",
                    "value": mfr_str,
                    "reason": "expected 4-character code (Avid registered manufacturer ID)",
                }
            )
        elif not mfr_str[0].isupper() or not mfr_str.isascii():
            invalid.append(
                {
                    "field": "AAXManufacturerID",
                    "value": mfr_str,
                    "reason": "expected ASCII 4-char code starting with uppercase letter (Avid convention)",
                }
            )

    category = elements.get("AAXProductCategory", "")
    if category and str(category) not in VALID_PRODUCT_CATEGORIES:
        invalid.append(
            {
                "field": "AAXProductCategory",
                "value": str(category),
                "reason": (
                    "unknown category; expected one of: "
                    + ", ".join(sorted(VALID_PRODUCT_CATEGORIES))
                ),
            }
        )

    pt_version = elements.get("AAXMinProToolsVersion", "")
    if pt_version and not PROTOOLS_VERSION_PATTERN.match(str(pt_version)):
        invalid.append(
            {
                "field": "AAXMinProToolsVersion",
                "value": str(pt_version),
                "reason": "expected version format (e.g. 2023.6 / 12.5.0)",
            }
        )

    return invalid


def _detect_optional_present(elements: dict[str, Any]) -> list[str]:
    """validation OK時の参考情報: 検出された optional fields。"""
    return [field for field in OPTIONAL_AAX_MANIFEST_ELEMENTS if field in elements]


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
    optional_present = _detect_optional_present(elements)
    valid = not missing and not invalid
    return json.dumps(
        {
            "valid": valid,
            "missing_required": missing,
            "invalid_values": invalid,
            "optional_present": optional_present,
            "parse_errors": [],
            "summary": (
                f"ok ({len(optional_present)} optional fields present)"
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

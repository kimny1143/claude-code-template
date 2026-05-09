"""Phase 0.1 unit tests — synthetic .aaxplugin bundle で MCP tool behavior verify."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from server import (  # noqa: E402
    check_signature,
    validate_bundle,
    validate_manifest,
)


# ---------- validate_bundle ----------

def test_validate_bundle_valid(valid_bundle: Path):
    result = json.loads(validate_bundle(str(valid_bundle)))
    assert result["passed"] is True, result["violations"]
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert len(errors) == 0


def test_validate_bundle_missing_macos(bundle_missing_macos: Path):
    result = json.loads(validate_bundle(str(bundle_missing_macos)))
    assert result["passed"] is False
    error_messages = [v["message"] for v in result["violations"] if v["level"] == "error"]
    assert any("Contents/MacOS/" in m for m in error_messages)


def test_validate_bundle_missing_info_plist(bundle_missing_info_plist: Path):
    result = json.loads(validate_bundle(str(bundle_missing_info_plist)))
    assert result["passed"] is False
    error_messages = [v["message"] for v in result["violations"] if v["level"] == "error"]
    assert any("Info.plist" in m for m in error_messages)


def test_validate_bundle_path_not_found(tmp_path: Path):
    nonexistent = tmp_path / "DoesNotExist.aaxplugin"
    result = json.loads(validate_bundle(str(nonexistent)))
    assert result["passed"] is False
    assert "not found" in result["summary"]


def test_validate_bundle_warns_on_wrong_extension(tmp_path: Path):
    bundle = tmp_path / "WrongExt"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    result = json.loads(validate_bundle(str(bundle)))
    warning_messages = [
        v["message"] for v in result["violations"] if v["level"] == "warning"
    ]
    assert any("does not end with .aaxplugin" in m for m in warning_messages)


# ---------- check_signature ----------

def test_check_signature_phase01_stub_returns_sdk_pending(valid_bundle: Path):
    result = json.loads(check_signature(str(valid_bundle)))
    assert result["signature_status"] == "sdk_pending"
    assert result["signed"] is False
    assert result["ilok_authorized"] is None
    assert "Phase 0.1 stub" in result["note"]


def test_check_signature_bundle_not_found(tmp_path: Path):
    nonexistent = tmp_path / "DoesNotExist.aaxplugin"
    result = json.loads(check_signature(str(nonexistent)))
    assert result["signature_status"] == "bundle_not_found"


def test_check_signature_pace_framework_present(tmp_path: Path):
    bundle = tmp_path / "WithPACE.aaxplugin"
    pace = bundle / "Contents" / "Frameworks" / "PACE_AntiPiracy.framework"
    pace.mkdir(parents=True)
    result = json.loads(check_signature(str(bundle)))
    assert result["pace_framework_present"] is True


# ---------- validate_manifest ----------

def test_validate_manifest_xml_valid(manifest_xml_valid: Path):
    result = json.loads(validate_manifest(str(manifest_xml_valid)))
    assert result["valid"] is True, result
    assert len(result["missing_required"]) == 0
    assert len(result["invalid_values"]) == 0


def test_validate_manifest_missing_field(manifest_xml_missing_field: Path):
    result = json.loads(validate_manifest(str(manifest_xml_missing_field)))
    assert result["valid"] is False
    assert "AAXEffectID" in result["missing_required"]


def test_validate_manifest_invalid_uuid(manifest_xml_invalid_uuid: Path):
    result = json.loads(validate_manifest(str(manifest_xml_invalid_uuid)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXPluginID" in invalid_fields


def test_validate_manifest_malformed_xml(manifest_xml_malformed: Path):
    result = json.loads(validate_manifest(str(manifest_xml_malformed)))
    assert result["valid"] is False
    assert any("XML parse error" in e for e in result["parse_errors"])


def test_validate_manifest_unsupported_format(tmp_path: Path):
    p = tmp_path / "manifest.txt"
    p.write_text("foo")
    result = json.loads(validate_manifest(str(p)))
    assert result["valid"] is False
    assert any("unsupported" in e for e in result["parse_errors"])


def test_validate_manifest_not_found(tmp_path: Path):
    nonexistent = tmp_path / "DoesNotExist.xml"
    result = json.loads(validate_manifest(str(nonexistent)))
    assert result["valid"] is False
    assert any("not found" in e for e in result["parse_errors"])


def test_validate_manifest_invalid_manufacturer_id(tmp_path: Path):
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>TOOLONG</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    result = json.loads(validate_manifest(str(p)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXManufacturerID" in invalid_fields


def test_validate_manifest_invalid_version(tmp_path: Path):
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>not.a.version!</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    result = json.loads(validate_manifest(str(p)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXPlugInVersion" in invalid_fields


# ============================================================
# Phase 0.2 enrichment tests
# ============================================================

# ---------- validate_bundle Phase 0.2 ----------

def test_validate_bundle_full_passes(valid_bundle_full: Path):
    """全推奨asset揃ったbundleは error なし、 icon/PACE warning も0想定 (binary archは別)。"""
    result = json.loads(validate_bundle(str(valid_bundle_full)))
    assert result["passed"] is True
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert len(errors) == 0
    warnings = [v for v in result["violations"] if v["level"] == "warning"]
    icon_warnings = [
        w for w in warnings if "recommended asset missing" in w["message"]
    ]
    pace_warnings = [w for w in warnings if "PACE" in w["message"]]
    assert len(icon_warnings) == 0
    assert len(pace_warnings) == 0


def test_validate_bundle_missing_icon_warns(bundle_missing_icon: Path):
    result = json.loads(validate_bundle(str(bundle_missing_icon)))
    warnings = [v for v in result["violations"] if v["level"] == "warning"]
    assert any("recommended asset missing" in w["message"] for w in warnings)


def test_validate_bundle_missing_pace_warns(bundle_missing_pace: Path):
    result = json.loads(validate_bundle(str(bundle_missing_pace)))
    warnings = [v for v in result["violations"] if v["level"] == "warning"]
    assert any("PACE" in w["message"] for w in warnings)


def test_validate_bundle_executable_missing_errors(
    bundle_executable_missing: Path,
):
    """Info.plistにCFBundleExecutable記載あるが実体ファイル欠如 → error."""
    result = json.loads(validate_bundle(str(bundle_executable_missing)))
    assert result["passed"] is False
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert any("executable not found" in e["message"] for e in errors)


def test_validate_bundle_corrupt_plist_errors(bundle_corrupt_plist: Path):
    result = json.loads(validate_bundle(str(bundle_corrupt_plist)))
    assert result["passed"] is False
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert any("plist parse error" in e["message"] for e in errors)


def test_validate_bundle_missing_manifest_xml_errors(
    bundle_missing_manifest_xml: Path,
):
    result = json.loads(validate_bundle(str(bundle_missing_manifest_xml)))
    assert result["passed"] is False
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert any("AAXManifest.xml" in e["message"] for e in errors)


def test_validate_bundle_no_executable_field_errors(
    bundle_no_executable_field: Path,
):
    """Info.plist に CFBundleExecutable key欠如 → error。"""
    result = json.loads(validate_bundle(str(bundle_no_executable_field)))
    assert result["passed"] is False
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert any("CFBundleExecutable" in e["message"] for e in errors)


def test_validate_bundle_no_cfbundleversion_errors(
    bundle_no_cfbundleversion: Path,
):
    result = json.loads(validate_bundle(str(bundle_no_cfbundleversion)))
    assert result["passed"] is False
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert any("CFBundleVersion" in e["message"] for e in errors)


def test_validate_bundle_icon_icns_only_no_warning(bundle_icon_icns_only: Path):
    """icon.icns のみ存在は OK (icon警告出ない)。"""
    result = json.loads(validate_bundle(str(bundle_icon_icns_only)))
    warnings = [v for v in result["violations"] if v["level"] == "warning"]
    icon_asset_warnings = [
        w for w in warnings if "recommended asset missing" in w["message"]
    ]
    assert len(icon_asset_warnings) == 0


def test_validate_bundle_wrong_extension_warns(bundle_wrong_extension: Path):
    """`.aaxplugin` 拡張子なしはwarning (errorではない)。"""
    result = json.loads(validate_bundle(str(bundle_wrong_extension)))
    warnings = [v for v in result["violations"] if v["level"] == "warning"]
    assert any("does not end with .aaxplugin" in w["message"] for w in warnings)


# ---------- validate_manifest Phase 0.2 ----------

def test_validate_manifest_full_optional_valid(manifest_xml_full_optional: Path):
    """全optional fields埋まったmanifestは valid + optional_present 3件全て検出。"""
    result = json.loads(validate_manifest(str(manifest_xml_full_optional)))
    assert result["valid"] is True
    assert "AAXPlugInName" in result["optional_present"]
    assert "AAXProductCategory" in result["optional_present"]
    assert "AAXMinProToolsVersion" in result["optional_present"]


def test_validate_manifest_invalid_effect_id(
    manifest_xml_invalid_effect_id: Path,
):
    result = json.loads(validate_manifest(str(manifest_xml_invalid_effect_id)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXEffectID" in invalid_fields


def test_validate_manifest_effect_id_lowercase(
    manifest_xml_effect_id_lowercase: Path,
):
    result = json.loads(validate_manifest(str(manifest_xml_effect_id_lowercase)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXEffectID" in invalid_fields


def test_validate_manifest_effect_id_3char(manifest_xml_effect_id_3char: Path):
    result = json.loads(validate_manifest(str(manifest_xml_effect_id_3char)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXEffectID" in invalid_fields


def test_validate_manifest_invalid_category(manifest_xml_invalid_category: Path):
    result = json.loads(validate_manifest(str(manifest_xml_invalid_category)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXProductCategory" in invalid_fields


def test_validate_manifest_dynamics_category_valid(
    manifest_xml_dynamics_category: Path,
):
    """category=Dynamics は有効カテゴリ。"""
    result = json.loads(validate_manifest(str(manifest_xml_dynamics_category)))
    assert result["valid"] is True


def test_validate_manifest_eq_category_valid(manifest_xml_eq_category: Path):
    result = json.loads(validate_manifest(str(manifest_xml_eq_category)))
    assert result["valid"] is True


def test_validate_manifest_invalid_pt_version(
    manifest_xml_invalid_pt_version: Path,
):
    result = json.loads(validate_manifest(str(manifest_xml_invalid_pt_version)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXMinProToolsVersion" in invalid_fields


def test_validate_manifest_pt_version_short_valid(
    manifest_xml_pt_version_short: Path,
):
    """Pro Tools version 短形式 (12.5) は有効。"""
    result = json.loads(validate_manifest(str(manifest_xml_pt_version_short)))
    assert result["valid"] is True


def test_validate_manifest_pt_version_long_valid(
    manifest_xml_pt_version_long: Path,
):
    """Pro Tools version 長形式 (2023.6.0) は有効。"""
    result = json.loads(validate_manifest(str(manifest_xml_pt_version_long)))
    assert result["valid"] is True


def test_validate_manifest_lowercase_manufacturer(
    manifest_xml_lowercase_manufacturer: Path,
):
    result = json.loads(validate_manifest(str(manifest_xml_lowercase_manufacturer)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXManufacturerID" in invalid_fields


def test_validate_manifest_3char_manufacturer(
    manifest_xml_3char_manufacturer: Path,
):
    result = json.loads(validate_manifest(str(manifest_xml_3char_manufacturer)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXManufacturerID" in invalid_fields


def test_validate_manifest_5char_manufacturer(
    manifest_xml_5char_manufacturer: Path,
):
    result = json.loads(validate_manifest(str(manifest_xml_5char_manufacturer)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXManufacturerID" in invalid_fields


def test_validate_manifest_non_ascii_manufacturer(
    manifest_xml_non_ascii_manufacturer: Path,
):
    result = json.loads(validate_manifest(str(manifest_xml_non_ascii_manufacturer)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXManufacturerID" in invalid_fields


def test_validate_manifest_invalid_semver(manifest_xml_invalid_semver: Path):
    result = json.loads(validate_manifest(str(manifest_xml_invalid_semver)))
    assert result["valid"] is False
    invalid_fields = [iv["field"] for iv in result["invalid_values"]]
    assert "AAXPlugInVersion" in invalid_fields


def test_validate_manifest_semver_with_prerelease_valid(
    manifest_xml_semver_with_prerelease: Path,
):
    """1.0.0-beta.1 形式 semver pre-release は valid。"""
    result = json.loads(validate_manifest(str(manifest_xml_semver_with_prerelease)))
    assert result["valid"] is True


def test_validate_manifest_uuid_uppercase_valid(manifest_xml_uuid_uppercase: Path):
    """UUID大文字も valid (UUID pattern case insensitive)。"""
    result = json.loads(validate_manifest(str(manifest_xml_uuid_uppercase)))
    assert result["valid"] is True


def test_validate_manifest_minimal_required_valid(
    manifest_xml_minimal_required: Path,
):
    """必須fieldsのみ、optional全欠如でも valid。"""
    result = json.loads(validate_manifest(str(manifest_xml_minimal_required)))
    assert result["valid"] is True
    assert result["optional_present"] == []


# ---------- plist manifest tests ----------

def test_validate_manifest_plist_valid(manifest_plist_valid: Path):
    result = json.loads(validate_manifest(str(manifest_plist_valid)))
    assert result["valid"] is True


def test_validate_manifest_plist_invalid(manifest_plist_invalid: Path):
    result = json.loads(validate_manifest(str(manifest_plist_invalid)))
    assert result["valid"] is False
    assert "AAXEffectID" in result["missing_required"]


def test_validate_manifest_plist_corrupt(manifest_plist_corrupt: Path):
    result = json.loads(validate_manifest(str(manifest_plist_corrupt)))
    assert result["valid"] is False
    assert any("plist parse error" in e for e in result["parse_errors"])


def test_validate_manifest_unsupported_format(manifest_unsupported_format: Path):
    result = json.loads(validate_manifest(str(manifest_unsupported_format)))
    assert result["valid"] is False
    assert any("unsupported" in e for e in result["parse_errors"])

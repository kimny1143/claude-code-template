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

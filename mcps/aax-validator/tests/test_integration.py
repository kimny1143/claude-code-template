"""Phase 0.3 prep — integration tests using AAXBundleBuilder.

3 MCP tools (validate_bundle / check_signature / validate_manifest) を
end-to-end呼出し、相互整合性 + edge cases を programmatic fixtureで検証。
Phase 1.0 (5/14- SDK受領後) の real signature wiring transitionで、本integration
testが regression防止 foundation として機能する。
"""
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
from tests.fixture_builder import (  # noqa: E402
    AAXBundleBuilder,
    AAXManifestSpec,
    make_minimal_bundle,
    make_valid_bundle,
)


# ============================================================
# end-to-end integration: 3 tools全呼出 + 結果整合性
# ============================================================

def test_e2e_valid_bundle_all_tools_consistent(tmp_path: Path):
    """完全valid bundleに対し3 tools全てが期待通りの状態を返す。"""
    bundle = make_valid_bundle(tmp_path)

    bundle_result = json.loads(validate_bundle(str(bundle)))
    sig_result = json.loads(check_signature(str(bundle)))
    manifest_result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )

    assert bundle_result["passed"] is True, bundle_result["violations"]
    assert sig_result["pace_framework_present"] is True
    assert sig_result["signature_status"] == "sdk_pending"  # Phase 0.1 stub
    assert manifest_result["valid"] is True


def test_e2e_minimal_bundle_passes_with_warnings(tmp_path: Path):
    """必須fields onlyで bundle/manifest passes、警告は icon/PACE。"""
    bundle = make_minimal_bundle(tmp_path)

    bundle_result = json.loads(validate_bundle(str(bundle)))
    sig_result = json.loads(check_signature(str(bundle)))
    manifest_result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )

    assert bundle_result["passed"] is True
    assert sig_result["pace_framework_present"] is False
    assert manifest_result["valid"] is True
    assert manifest_result["optional_present"] == []


def test_e2e_corrupt_plist_propagates_error(tmp_path: Path):
    """corrupt plist は validate_bundleで error、他toolsは独立に動作。"""
    bundle = (
        AAXBundleBuilder(tmp_path / "Corrupt.aaxplugin")
        .with_corrupt_info_plist()
        .build()
    )
    bundle_result = json.loads(validate_bundle(str(bundle)))
    sig_result = json.loads(check_signature(str(bundle)))

    assert bundle_result["passed"] is False
    errors = [v for v in bundle_result["violations"] if v["level"] == "error"]
    assert any("plist parse error" in e["message"] for e in errors)
    # check_signatureは plist独立、pace_framework_presentのみ check
    assert sig_result["signature_status"] == "sdk_pending"


def test_e2e_missing_manifest_propagates(tmp_path: Path):
    """manifest不在で validate_bundleがerror、validate_manifestは not found。"""
    bundle = (
        AAXBundleBuilder(tmp_path / "NoManifest.aaxplugin")
        .with_info_plist(executable="NoManifest")
        .with_executable(arch_set={"arm64"})
        .with_icon()
        .build()
    )
    bundle_result = json.loads(validate_bundle(str(bundle)))
    manifest_path = bundle / "Contents" / "Resources" / "AAXManifest.xml"
    manifest_result = json.loads(validate_manifest(str(manifest_path)))

    assert bundle_result["passed"] is False
    assert any(
        "AAXManifest.xml" in v["message"]
        for v in bundle_result["violations"] if v["level"] == "error"
    )
    assert manifest_result["valid"] is False
    assert any("not found" in e for e in manifest_result["parse_errors"])


# ============================================================
# fluent builder一貫性テスト
# ============================================================

def test_builder_produces_valid_default(tmp_path: Path):
    """make_valid_bundle: 全default validation pass。"""
    bundle = make_valid_bundle(tmp_path)
    result = json.loads(validate_bundle(str(bundle)))
    assert result["passed"] is True
    errors = [v for v in result["violations"] if v["level"] == "error"]
    assert len(errors) == 0


def test_builder_with_full_optional_manifest(tmp_path: Path):
    """builder で全optional manifest fields埋込み → validate_manifest valid。"""
    bundle = (
        AAXBundleBuilder(tmp_path / "FullOpt.aaxplugin")
        .with_info_plist(executable="FullOpt")
        .with_executable(arch_set={"arm64", "x86_64"})
        .with_aax_manifest(
            plugin_name="Full Optional Plugin",
            product_category="Reverb",
            min_protools_version="2024.6",
        )
        .with_icon()
        .with_pace_framework()
        .build()
    )
    manifest_result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )
    assert manifest_result["valid"] is True
    assert "AAXPlugInName" in manifest_result["optional_present"]
    assert "AAXProductCategory" in manifest_result["optional_present"]
    assert "AAXMinProToolsVersion" in manifest_result["optional_present"]


def test_builder_with_invalid_category_propagates(tmp_path: Path):
    """builder で invalid category埋込み → validate_manifest invalid_values検出。"""
    bundle = (
        AAXBundleBuilder(tmp_path / "BadCat.aaxplugin")
        .with_info_plist(executable="BadCat")
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest(product_category="QuantumFlux")
        .build()
    )
    manifest_result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )
    assert manifest_result["valid"] is False
    invalid_fields = [iv["field"] for iv in manifest_result["invalid_values"]]
    assert "AAXProductCategory" in invalid_fields


def test_builder_with_extra_framework(tmp_path: Path):
    """builder.with_extra_framework: PACE以外のframeworkも追加可能 (e.g., custom Avid framework)。"""
    bundle = (
        AAXBundleBuilder(tmp_path / "ExtraFw.aaxplugin")
        .with_info_plist(executable="ExtraFw")
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest()
        .with_pace_framework()
        .with_extra_framework("CustomAvidLib.framework")
        .build()
    )
    custom_path = bundle / "Contents" / "Frameworks" / "CustomAvidLib.framework"
    pace_path = bundle / "Contents" / "Frameworks" / "PACE_AntiPiracy.framework"
    assert custom_path.is_dir()
    assert pace_path.is_dir()


def test_builder_with_extra_resource(tmp_path: Path):
    """builder.with_extra_resource: presets / images等の追加resource対応。"""
    preset_data = b"<?xml version='1.0'?><Preset name='Init' />"
    bundle = (
        AAXBundleBuilder(tmp_path / "WithPreset.aaxplugin")
        .with_info_plist(executable="WithPreset")
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest()
        .with_extra_resource("DefaultPreset.xml", preset_data)
        .build()
    )
    preset_path = bundle / "Contents" / "Resources" / "DefaultPreset.xml"
    assert preset_path.read_bytes() == preset_data


# ============================================================
# parametric matrix: 多数bundle variantsで一括 sanity check
# ============================================================

@pytest.mark.parametrize(
    "category",
    ["EQ", "Dynamics", "Reverb", "Delay", "Modulation", "Effect", "Instrument"],
)
def test_all_valid_categories_pass(tmp_path: Path, category: str):
    """全valid categoriesで manifest validation pass確認。"""
    bundle = (
        AAXBundleBuilder(tmp_path / f"Cat_{category}.aaxplugin")
        .with_info_plist(executable=f"Cat{category}")
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest(product_category=category)
        .build()
    )
    result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )
    assert result["valid"] is True, f"category {category} failed: {result}"


@pytest.mark.parametrize(
    "version,expected_valid",
    [
        ("1.0.0", True),
        ("1.0", True),
        ("1.0.0-beta1", True),
        ("1.0.0-rc.1", True),
        ("v1.0.0", False),  # leading v not allowed
        ("invalid", False),
        ("1.0.0.0.0", False),  # too many segments
    ],
)
def test_version_format_matrix(tmp_path: Path, version: str, expected_valid: bool):
    """semver matrix sanity check。"""
    bundle = (
        AAXBundleBuilder(tmp_path / f"Ver_{version.replace('.', '_')}.aaxplugin")
        .with_info_plist(executable="Ver")
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest(version=version)
        .build()
    )
    result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )
    assert result["valid"] is expected_valid, f"version={version}: got valid={result['valid']}, expected {expected_valid}"


@pytest.mark.parametrize(
    "manufacturer,expected_valid",
    [
        ("EXMP", True),
        ("Avid", True),
        ("Eq01", True),
        ("exmp", False),  # lowercase first letter
        ("EXM", False),  # 3 chars
        ("EXMPL", False),  # 5 chars
        ("あいうえ", False),  # non-ASCII
    ],
)
def test_manufacturer_id_matrix(tmp_path: Path, manufacturer: str, expected_valid: bool):
    """4-char manufacturer ID convention matrix。"""
    safe_name = manufacturer.encode("ascii", errors="replace").decode("ascii").replace("?", "Q")
    bundle = (
        AAXBundleBuilder(tmp_path / f"Mfr_{safe_name}.aaxplugin")
        .with_info_plist(executable="Mfr")
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest(manufacturer_id=manufacturer)
        .build()
    )
    result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )
    assert result["valid"] is expected_valid


@pytest.mark.parametrize(
    "pt_version,expected_valid",
    [
        ("12.5", True),
        ("12.5.0", True),
        ("2023.6", True),
        ("2024.10", True),
        ("12", False),  # single digit
        ("12.5.0.1", False),  # too many segments
        ("twentytwentyfour", False),
        ("12.5.x", False),
    ],
)
def test_protools_version_matrix(
    tmp_path: Path, pt_version: str, expected_valid: bool
):
    bundle = (
        AAXBundleBuilder(tmp_path / f"PT_{pt_version.replace('.', '_')}.aaxplugin")
        .with_info_plist(executable="PT")
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest(min_protools_version=pt_version)
        .build()
    )
    result = json.loads(
        validate_manifest(str(bundle / "Contents" / "Resources" / "AAXManifest.xml"))
    )
    assert result["valid"] is expected_valid


# ============================================================
# regression防止: Phase 0.1 stub状態を維持確認
# ============================================================

def test_check_signature_stub_status_unchanged(tmp_path: Path):
    """Phase 1.0 wiring前 = signature_status="sdk_pending" 維持確認。"""
    bundle = make_valid_bundle(tmp_path)
    result = json.loads(check_signature(str(bundle)))
    assert result["signature_status"] == "sdk_pending"
    assert "Phase 0.1 stub" in result["note"]


def test_check_signature_returns_none_for_ilok(tmp_path: Path):
    """Phase 1.0 wiring前 = ilok_authorized は None。"""
    bundle = make_valid_bundle(tmp_path)
    result = json.loads(check_signature(str(bundle)))
    assert result["ilok_authorized"] is None

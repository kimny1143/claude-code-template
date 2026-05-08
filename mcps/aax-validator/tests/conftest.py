"""pytest fixtures: synthetic .aaxplugin bundle + AAX manifest examples."""
from __future__ import annotations

import plistlib
from pathlib import Path

import pytest


@pytest.fixture
def valid_bundle(tmp_path: Path) -> Path:
    """完全な .aaxplugin directory structureを synthetic生成。"""
    bundle = tmp_path / "ValidPlugin.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)

    info = {
        "CFBundleIdentifier": "com.example.validplugin",
        "CFBundleVersion": "1.0.0",
        "CFBundleExecutable": "ValidPlugin",
    }
    with open(contents / "Info.plist", "wb") as fh:
        plistlib.dump(info, fh)

    exe = contents / "MacOS" / "ValidPlugin"
    exe.write_bytes(b"\x00\x00\x00\x00")  # placeholder binary

    manifest_xml = """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
"""
    (contents / "Resources" / "AAXManifest.xml").write_text(
        manifest_xml, encoding="utf-8"
    )

    return bundle


@pytest.fixture
def bundle_missing_macos(tmp_path: Path) -> Path:
    bundle = tmp_path / "MissingMacOS.aaxplugin"
    contents = bundle / "Contents"
    (contents / "Resources").mkdir(parents=True)
    info = {
        "CFBundleIdentifier": "com.example.missingmacos",
        "CFBundleVersion": "1.0.0",
        "CFBundleExecutable": "MissingMacOS",
    }
    with open(contents / "Info.plist", "wb") as fh:
        plistlib.dump(info, fh)
    return bundle


@pytest.fixture
def bundle_missing_info_plist(tmp_path: Path) -> Path:
    bundle = tmp_path / "NoInfoPlist.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    return bundle


@pytest.fixture
def manifest_xml_valid(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.2.3</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def manifest_xml_missing_field(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def manifest_xml_invalid_uuid(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>not-a-uuid</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def manifest_xml_malformed(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.xml"
    p.write_text("<not_well_formed>", encoding="utf-8")
    return p

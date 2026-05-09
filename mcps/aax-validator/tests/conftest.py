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


# ============================================================
# Phase 0.2 enrichment fixtures
# ============================================================

@pytest.fixture
def valid_bundle_full(tmp_path: Path) -> Path:
    """全推奨asset揃った完全bundle (icon + PACE framework + manifest)。"""
    bundle = tmp_path / "FullPlugin.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    pace = contents / "Frameworks" / "PACE_AntiPiracy.framework"
    pace.mkdir(parents=True)

    info = {
        "CFBundleIdentifier": "com.example.fullplugin",
        "CFBundleVersion": "1.0.0",
        "CFBundleExecutable": "FullPlugin",
    }
    with open(contents / "Info.plist", "wb") as fh:
        plistlib.dump(info, fh)

    (contents / "MacOS" / "FullPlugin").write_bytes(b"\x00\x00\x00\x00")
    (contents / "Resources" / "icon.png").write_bytes(b"\x89PNG")

    manifest_xml = """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
    <AAXPlugInName>Example Plugin</AAXPlugInName>
    <AAXProductCategory>Effect</AAXProductCategory>
    <AAXMinProToolsVersion>2023.6</AAXMinProToolsVersion>
</AAXManifest>
"""
    (contents / "Resources" / "AAXManifest.xml").write_text(
        manifest_xml, encoding="utf-8"
    )
    return bundle


@pytest.fixture
def bundle_missing_icon(tmp_path: Path) -> Path:
    """icon欠如bundle (warning想定)。"""
    bundle = tmp_path / "NoIcon.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    info = {
        "CFBundleIdentifier": "com.example.noicon",
        "CFBundleVersion": "1.0.0",
        "CFBundleExecutable": "NoIcon",
    }
    with open(contents / "Info.plist", "wb") as fh:
        plistlib.dump(info, fh)
    (contents / "MacOS" / "NoIcon").write_bytes(b"\x00\x00\x00\x00")
    (contents / "Resources" / "AAXManifest.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return bundle


@pytest.fixture
def bundle_missing_pace(tmp_path: Path) -> Path:
    """PACE framework欠如bundle (warning想定)。"""
    bundle = tmp_path / "NoPACE.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    info = {
        "CFBundleIdentifier": "com.example.nopace",
        "CFBundleVersion": "1.0.0",
        "CFBundleExecutable": "NoPACE",
    }
    with open(contents / "Info.plist", "wb") as fh:
        plistlib.dump(info, fh)
    (contents / "MacOS" / "NoPACE").write_bytes(b"\x00\x00\x00\x00")
    (contents / "Resources" / "icon.png").write_bytes(b"\x89PNG")
    (contents / "Resources" / "AAXManifest.xml").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return bundle


@pytest.fixture
def manifest_xml_full_optional(tmp_path: Path) -> Path:
    """全optional fields埋まったmanifest。"""
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.2.3</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
    <AAXPlugInName>Example Compressor</AAXPlugInName>
    <AAXProductCategory>Dynamics</AAXProductCategory>
    <AAXMinProToolsVersion>2023.6</AAXMinProToolsVersion>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def manifest_xml_invalid_effect_id(tmp_path: Path) -> Path:
    """AAXEffectID不正 (3-char、小文字始まり等)。"""
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>eff</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def manifest_xml_invalid_category(tmp_path: Path) -> Path:
    """AAXProductCategory が定義外。"""
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
    <AAXProductCategory>Quantum</AAXProductCategory>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def manifest_xml_invalid_pt_version(tmp_path: Path) -> Path:
    """AAXMinProToolsVersion 不正 format。"""
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>EXMP</AAXManufacturerID>
    <AAXMinProToolsVersion>twenty-twentythree</AAXMinProToolsVersion>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def manifest_xml_lowercase_manufacturer(tmp_path: Path) -> Path:
    """AAXManufacturerID 小文字始まり (Avid convention違反)。"""
    p = tmp_path / "AAXManifest.xml"
    p.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<AAXManifest>
    <AAXPluginID>12345678-1234-1234-1234-123456789012</AAXPluginID>
    <AAXEffectID>EFCT</AAXEffectID>
    <AAXPlugInVersion>1.0.0</AAXPlugInVersion>
    <AAXManufacturerID>exmp</AAXManufacturerID>
</AAXManifest>
""",
        encoding="utf-8",
    )
    return p


# ============================================================
# Phase 0.2 量産fixtures (kimny指示「産め産むほど速度も打率も上がる」)
# ============================================================

def _write_minimal_plist(path: Path, exe_name: str = "Plugin") -> None:
    info = {
        "CFBundleIdentifier": f"com.example.{exe_name.lower()}",
        "CFBundleVersion": "1.0.0",
        "CFBundleExecutable": exe_name,
    }
    with open(path, "wb") as fh:
        plistlib.dump(info, fh)


def _write_minimal_manifest(path: Path, **overrides) -> None:
    fields = {
        "AAXPluginID": "12345678-1234-1234-1234-123456789012",
        "AAXEffectID": "EFCT",
        "AAXPlugInVersion": "1.0.0",
        "AAXManufacturerID": "EXMP",
    }
    fields.update(overrides)
    body = "\n".join(f"    <{k}>{v}</{k}>" for k, v in fields.items())
    path.write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<AAXManifest>\n{body}\n</AAXManifest>\n',
        encoding="utf-8",
    )


@pytest.fixture
def bundle_executable_missing(tmp_path: Path) -> Path:
    """Info.plist にCFBundleExecutable記載あるが実体ファイル欠如。"""
    bundle = tmp_path / "ExeMissing.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    _write_minimal_plist(contents / "Info.plist", "ExeMissing")
    _write_minimal_manifest(contents / "Resources" / "AAXManifest.xml")
    return bundle


@pytest.fixture
def bundle_corrupt_plist(tmp_path: Path) -> Path:
    """Info.plist が壊れている (parse error)。"""
    bundle = tmp_path / "CorruptPlist.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    (contents / "Info.plist").write_bytes(b"not a valid plist content")
    return bundle


@pytest.fixture
def bundle_missing_manifest_xml(tmp_path: Path) -> Path:
    """AAXManifest.xml欠如。"""
    bundle = tmp_path / "NoManifest.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    _write_minimal_plist(contents / "Info.plist", "NoManifest")
    (contents / "MacOS" / "NoManifest").write_bytes(b"\x00\x00")
    (contents / "Resources" / "icon.png").write_bytes(b"\x89PNG")
    return bundle


@pytest.fixture
def bundle_no_executable_field(tmp_path: Path) -> Path:
    """Info.plist に CFBundleExecutable key欠如。"""
    bundle = tmp_path / "NoExeField.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    info = {
        "CFBundleIdentifier": "com.example.noexe",
        "CFBundleVersion": "1.0.0",
    }
    with open(contents / "Info.plist", "wb") as fh:
        plistlib.dump(info, fh)
    return bundle


@pytest.fixture
def bundle_no_cfbundleversion(tmp_path: Path) -> Path:
    """Info.plist に CFBundleVersion key欠如。"""
    bundle = tmp_path / "NoCFBVer.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    info = {
        "CFBundleIdentifier": "com.example.nover",
        "CFBundleExecutable": "NoCFBVer",
    }
    with open(contents / "Info.plist", "wb") as fh:
        plistlib.dump(info, fh)
    return bundle


@pytest.fixture
def bundle_icon_icns_only(tmp_path: Path) -> Path:
    """icon.icns のみ存在 (icon.png なし) — warning出ずパスする想定。"""
    bundle = tmp_path / "IconIcns.aaxplugin"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    _write_minimal_plist(contents / "Info.plist", "IconIcns")
    (contents / "MacOS" / "IconIcns").write_bytes(b"\x00")
    (contents / "Resources" / "icon.icns").write_bytes(b"icns")
    _write_minimal_manifest(contents / "Resources" / "AAXManifest.xml")
    return bundle


@pytest.fixture
def bundle_wrong_extension(tmp_path: Path) -> Path:
    """`.aaxplugin` 拡張子なし (warning想定)。"""
    bundle = tmp_path / "WrongExt"
    contents = bundle / "Contents"
    (contents / "MacOS").mkdir(parents=True)
    (contents / "Resources").mkdir(parents=True)
    _write_minimal_plist(contents / "Info.plist", "WrongExt")
    (contents / "MacOS" / "WrongExt").write_bytes(b"\x00")
    _write_minimal_manifest(contents / "Resources" / "AAXManifest.xml")
    return bundle


@pytest.fixture
def manifest_xml_3char_manufacturer(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXManufacturerID="EXM")
    return p


@pytest.fixture
def manifest_xml_5char_manufacturer(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXManufacturerID="EXMPL")
    return p


@pytest.fixture
def manifest_xml_non_ascii_manufacturer(tmp_path: Path) -> Path:
    """non-ASCII 4 chars (Avid convention違反、ASCII restriction)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXManufacturerID="あいうえ")
    return p


@pytest.fixture
def manifest_xml_invalid_semver(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXPlugInVersion="vee.one.zero")
    return p


@pytest.fixture
def manifest_xml_semver_with_prerelease(tmp_path: Path) -> Path:
    """1.0.0-beta.1 形式 (semver pre-release、validとして許容)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXPlugInVersion="1.0.0-beta.1")
    return p


@pytest.fixture
def manifest_xml_uuid_uppercase(tmp_path: Path) -> Path:
    """UUID大文字 (UUID patternは case insensitive、validで通る想定)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXPluginID="ABCDEF12-3456-7890-ABCD-EF1234567890")
    return p


@pytest.fixture
def manifest_xml_minimal_required(tmp_path: Path) -> Path:
    """必須fieldのみ、optional全て欠如 (valid想定)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p)
    return p


@pytest.fixture
def manifest_xml_dynamics_category(tmp_path: Path) -> Path:
    """category=Dynamics (compressor想定、有効カテゴリ)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXProductCategory="Dynamics")
    return p


@pytest.fixture
def manifest_xml_eq_category(tmp_path: Path) -> Path:
    """category=EQ (有効カテゴリ)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXProductCategory="EQ")
    return p


@pytest.fixture
def manifest_xml_pt_version_short(tmp_path: Path) -> Path:
    """Pro Tools version 短形式 (12.5)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXMinProToolsVersion="12.5")
    return p


@pytest.fixture
def manifest_xml_pt_version_long(tmp_path: Path) -> Path:
    """Pro Tools version 長形式 (2023.6.0)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXMinProToolsVersion="2023.6.0")
    return p


@pytest.fixture
def manifest_xml_effect_id_lowercase(tmp_path: Path) -> Path:
    """AAXEffectID が小文字始まり (4-char code条件違反)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXEffectID="effc")
    return p


@pytest.fixture
def manifest_xml_effect_id_3char(tmp_path: Path) -> Path:
    """AAXEffectID が3文字 (条件違反)。"""
    p = tmp_path / "AAXManifest.xml"
    _write_minimal_manifest(p, AAXEffectID="EFC")
    return p


@pytest.fixture
def manifest_plist_valid(tmp_path: Path) -> Path:
    """plist形式 manifest (validate_manifest 両形式対応 verify)。"""
    p = tmp_path / "AAXManifest.plist"
    data = {
        "AAXPluginID": "12345678-1234-1234-1234-123456789012",
        "AAXEffectID": "EFCT",
        "AAXPlugInVersion": "1.0.0",
        "AAXManufacturerID": "EXMP",
        "AAXProductCategory": "Effect",
    }
    with open(p, "wb") as fh:
        plistlib.dump(data, fh)
    return p


@pytest.fixture
def manifest_plist_invalid(tmp_path: Path) -> Path:
    """plist形式 manifest 必須field欠如。"""
    p = tmp_path / "AAXManifest.plist"
    data = {
        "AAXPluginID": "12345678-1234-1234-1234-123456789012",
        # AAXEffectID 欠如
        "AAXPlugInVersion": "1.0.0",
        "AAXManufacturerID": "EXMP",
    }
    with open(p, "wb") as fh:
        plistlib.dump(data, fh)
    return p


@pytest.fixture
def manifest_plist_corrupt(tmp_path: Path) -> Path:
    """plist parse不能 file。"""
    p = tmp_path / "AAXManifest.plist"
    p.write_bytes(b"not a valid plist")
    return p


@pytest.fixture
def manifest_unsupported_format(tmp_path: Path) -> Path:
    p = tmp_path / "AAXManifest.json"
    p.write_text('{"AAXPluginID": "..."}', encoding="utf-8")
    return p

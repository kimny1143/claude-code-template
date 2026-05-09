"""Parametric .aaxplugin fixture builder — Phase 0.3 prep.

synthetic .aaxplugin bundle を programmaticに組み立てる helper class。
Phase 1.0 (kimny task #73 SDK受領後 5/14-) の integration test foundationとして使用。
Phase 0.2 conftest.py の手書き fixture を programmable に generalize。

使用例:
    builder = AAXBundleBuilder(tmp_path / "MyPlugin.aaxplugin")
    builder.with_info_plist(executable="MyPlugin", version="1.0.0")
    builder.with_executable(arch_set={"arm64", "x86_64"})  # universal2 simulation
    builder.with_aax_manifest(plugin_id="...", effect_id="EFCT")
    builder.with_icon()
    builder.with_pace_framework()
    bundle_path = builder.build()
"""
from __future__ import annotations

import plistlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_PLUGIN_ID = "12345678-1234-1234-1234-123456789012"
DEFAULT_EFFECT_ID = "EFCT"
DEFAULT_VERSION = "1.0.0"
DEFAULT_MANUFACTURER = "EXMP"


@dataclass
class AAXManifestSpec:
    """AAX manifest field spec for builder。"""

    plugin_id: str = DEFAULT_PLUGIN_ID
    effect_id: str = DEFAULT_EFFECT_ID
    version: str = DEFAULT_VERSION
    manufacturer_id: str = DEFAULT_MANUFACTURER
    plugin_name: str | None = None
    product_category: str | None = None
    min_protools_version: str | None = None
    extra: dict[str, str] = field(default_factory=dict)

    def to_xml(self) -> str:
        fields: list[tuple[str, str]] = [
            ("AAXPluginID", self.plugin_id),
            ("AAXEffectID", self.effect_id),
            ("AAXPlugInVersion", self.version),
            ("AAXManufacturerID", self.manufacturer_id),
        ]
        if self.plugin_name is not None:
            fields.append(("AAXPlugInName", self.plugin_name))
        if self.product_category is not None:
            fields.append(("AAXProductCategory", self.product_category))
        if self.min_protools_version is not None:
            fields.append(("AAXMinProToolsVersion", self.min_protools_version))
        for k, v in self.extra.items():
            fields.append((k, v))

        body = "\n".join(f"    <{k}>{v}</{k}>" for k, v in fields)
        return f'<?xml version="1.0" encoding="UTF-8"?>\n<AAXManifest>\n{body}\n</AAXManifest>\n'


class AAXBundleBuilder:
    """fluent builder for synthetic .aaxplugin bundles。"""

    def __init__(self, bundle_path: Path) -> None:
        self.bundle_path = Path(bundle_path)
        self.contents = self.bundle_path / "Contents"
        self._info_plist: dict[str, Any] | None = None
        self._exe_name: str | None = None
        self._exe_arch_set: set[str] | None = None
        self._manifest: AAXManifestSpec | None = None
        self._has_icon = False
        self._icon_format = "png"
        self._has_pace_framework = False
        self._frameworks: list[str] = []
        self._extra_resources: list[tuple[str, bytes]] = []

    def with_info_plist(
        self,
        executable: str = "Plugin",
        version: str = "1.0.0",
        identifier: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> AAXBundleBuilder:
        info: dict[str, Any] = {
            "CFBundleIdentifier": identifier or f"com.example.{executable.lower()}",
            "CFBundleVersion": version,
            "CFBundleExecutable": executable,
        }
        if extra:
            info.update(extra)
        self._info_plist = info
        self._exe_name = executable
        return self

    def with_corrupt_info_plist(self) -> AAXBundleBuilder:
        """sentinel: 後で build()で corrupt content書き込み。"""
        self._info_plist = {"__corrupt__": True}
        return self

    def without_info_plist(self) -> AAXBundleBuilder:
        self._info_plist = None
        return self

    def with_executable(
        self, arch_set: set[str] | None = None
    ) -> AAXBundleBuilder:
        """executable bytes生成。arch_setに応じてplaceholder bytes生成 (lipoは実binaryでないと動作しないが、structureチェック用)."""
        self._exe_arch_set = arch_set
        return self

    def without_executable(self) -> AAXBundleBuilder:
        self._exe_arch_set = None
        return self

    def with_aax_manifest(
        self,
        plugin_id: str = DEFAULT_PLUGIN_ID,
        effect_id: str = DEFAULT_EFFECT_ID,
        version: str = DEFAULT_VERSION,
        manufacturer_id: str = DEFAULT_MANUFACTURER,
        plugin_name: str | None = None,
        product_category: str | None = None,
        min_protools_version: str | None = None,
        extra: dict[str, str] | None = None,
    ) -> AAXBundleBuilder:
        self._manifest = AAXManifestSpec(
            plugin_id=plugin_id,
            effect_id=effect_id,
            version=version,
            manufacturer_id=manufacturer_id,
            plugin_name=plugin_name,
            product_category=product_category,
            min_protools_version=min_protools_version,
            extra=extra or {},
        )
        return self

    def without_aax_manifest(self) -> AAXBundleBuilder:
        self._manifest = None
        return self

    def with_icon(self, format: str = "png") -> AAXBundleBuilder:
        """icon.png または icon.icns を生成。"""
        self._has_icon = True
        self._icon_format = format
        return self

    def with_pace_framework(self) -> AAXBundleBuilder:
        self._has_pace_framework = True
        return self

    def with_extra_framework(self, framework_name: str) -> AAXBundleBuilder:
        self._frameworks.append(framework_name)
        return self

    def with_extra_resource(self, name: str, content: bytes = b"") -> AAXBundleBuilder:
        self._extra_resources.append((name, content))
        return self

    def build(self) -> Path:
        """assemble bundle directory from accumulated specs。"""
        macos = self.contents / "MacOS"
        resources = self.contents / "Resources"
        macos.mkdir(parents=True, exist_ok=True)
        resources.mkdir(parents=True, exist_ok=True)

        if self._info_plist is not None:
            plist_path = self.contents / "Info.plist"
            if self._info_plist.get("__corrupt__"):
                plist_path.write_bytes(b"not a valid plist content")
            else:
                with open(plist_path, "wb") as fh:
                    plistlib.dump(self._info_plist, fh)

        if self._exe_name and self._exe_arch_set is not None:
            exe_path = macos / self._exe_name
            arch_marker = ",".join(sorted(self._exe_arch_set)).encode()
            exe_path.write_bytes(b"\x00\x00\x00\x00" + arch_marker)

        if self._manifest is not None:
            (resources / "AAXManifest.xml").write_text(
                self._manifest.to_xml(), encoding="utf-8"
            )

        if self._has_icon:
            ext = self._icon_format
            (resources / f"icon.{ext}").write_bytes(b"\x89PNG" if ext == "png" else b"icns")

        if self._has_pace_framework:
            (
                self.contents / "Frameworks" / "PACE_AntiPiracy.framework"
            ).mkdir(parents=True, exist_ok=True)
        for fw in self._frameworks:
            (self.contents / "Frameworks" / fw).mkdir(parents=True, exist_ok=True)

        for name, content in self._extra_resources:
            (resources / name).write_bytes(content)

        return self.bundle_path


def make_valid_bundle(tmp_path: Path, name: str = "ValidPlugin") -> Path:
    """convenience: 完全に valid な .aaxplugin bundle を生成。"""
    return (
        AAXBundleBuilder(tmp_path / f"{name}.aaxplugin")
        .with_info_plist(executable=name, version="1.0.0")
        .with_executable(arch_set={"arm64", "x86_64"})
        .with_aax_manifest()
        .with_icon()
        .with_pace_framework()
        .build()
    )


def make_minimal_bundle(tmp_path: Path, name: str = "MinimalPlugin") -> Path:
    """convenience: 必須fields only、optional asset/manifest fields欠如。"""
    return (
        AAXBundleBuilder(tmp_path / f"{name}.aaxplugin")
        .with_info_plist(executable=name)
        .with_executable(arch_set={"arm64"})
        .with_aax_manifest()
        .build()
    )

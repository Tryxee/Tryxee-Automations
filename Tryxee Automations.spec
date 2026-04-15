# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

# Collect all PyQt5 submodules as hidden imports.
# If your app only uses specific Qt modules, you can replace this with
# a targeted list (e.g. ["PyQt5.QtWidgets", "PyQt5.QtCore", "PyQt5.QtGui"])
# to significantly reduce build size.
hiddenimports = collect_submodules("PyQt5")

a = Analysis(
    ["blueprint_app.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("tryxee.ico", "."),
        ("functions.py", "."),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["pyi_rth_tryxee_setcwd.py"],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)
# block_cipher / cipher= removed — deprecated since PyInstaller 6.x

exe = EXE(
    pyz,
    a.scripts,
    [],                        # ← empty: binaries/datas live in COLLECT, not here
    exclude_binaries=True,     # ← required for one-folder mode
    name="Tryxee Automations",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon="tryxee.ico",
)

coll = COLLECT(
    exe,
    a.binaries,   # ← binaries belong here, not in EXE
    a.datas,      # ← datas belong here, not in EXE
    # a.zipfiles removed — deprecated and always empty in PyInstaller 4+
    # a.excludes removed — it's a list of module name strings, not file tuples
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Tryxee Automations",
)
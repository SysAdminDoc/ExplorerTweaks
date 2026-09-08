# -*- mode: python ; coding: utf-8 -*-
"""
ExplorerTweaks PyInstaller Spec File
====================================

Use `build.bat` so PyInstaller, release ZIP, checksums, and signing checks come from one path.
"""

from pathlib import Path
from PyInstaller.utils.hooks import collect_all

customtkinter_datas, customtkinter_binaries, customtkinter_hiddenimports = collect_all("customtkinter")
icon_file = "branding/icon.ico"
if not Path(icon_file).is_file():
    raise FileNotFoundError("Export the approved icon with create_icon.py before building.")

a = Analysis(
    ["explorer_tweaks.py"],
    pathex=[],
    binaries=customtkinter_binaries,
    datas=customtkinter_datas + [("branding", "branding"), ("build/build-provenance.json", ".")],
    hiddenimports=customtkinter_hiddenimports + [
        "customtkinter",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["assets/runtime_hook_mp.py"],
    excludes=[
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",

        "cv2",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ExplorerTweaks",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version="version_info.txt",
    icon=icon_file,
)

# -*- mode: python ; coding: utf-8 -*-
"""
ExplorerTweaks PyInstaller Spec File
====================================

Use `pyinstaller ExplorerTweaks.spec` or `build.bat`.
"""

import os
from PyInstaller.utils.hooks import collect_all

customtkinter_datas, customtkinter_binaries, customtkinter_hiddenimports = collect_all("customtkinter")
icon_file = "icon.ico" if os.path.exists("icon.ico") else None
icon_datas = [("icon.ico", ".")] if icon_file else []

a = Analysis(
    ["explorer_tweaks.py"],
    pathex=[],
    binaries=customtkinter_binaries,
    datas=customtkinter_datas + icon_datas,
    hiddenimports=customtkinter_hiddenimports + [
        "customtkinter",
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
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
    upx=True,
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

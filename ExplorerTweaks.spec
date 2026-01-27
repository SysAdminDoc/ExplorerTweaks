# -*- mode: python ; coding: utf-8 -*-
"""
ExplorerTweaks PyInstaller Spec File
=====================================
This spec file provides fine-grained control over the build process.

Usage:
    pyinstaller ExplorerTweaks.spec

Or use the build.bat script for automatic building.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all customtkinter data
customtkinter_datas, customtkinter_binaries, customtkinter_hiddenimports = collect_all('customtkinter')

block_cipher = None

a = Analysis(
    ['explorer_tweaks.py'],
    pathex=[],
    binaries=customtkinter_binaries,
    datas=customtkinter_datas + [
        ('icon.ico', '.'),  # Include icon in root of bundle
    ],
    hiddenimports=customtkinter_hiddenimports + [
        'customtkinter',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ExplorerTweaks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    uac_admin=False,  # Don't require admin by default
    uac_uiaccess=False,
    version_info={
        'FileVersion': '1.0.0.0',
        'ProductVersion': '1.0.0.0',
        'FileDescription': 'Windows File Explorer Configuration Utility',
        'LegalCopyright': 'Copyright (c) 2025 SysAdminDoc',
        'ProductName': 'ExplorerTweaks',
        'CompanyName': 'SysAdminDoc',
        'OriginalFilename': 'ExplorerTweaks.exe',
    } if sys.platform == 'win32' else None,
)

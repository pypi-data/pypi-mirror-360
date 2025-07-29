# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification file for SimpleTimerBank (Single-File Build).

This spec file configures PyInstaller to build a standalone single-file
executable for the SimpleTimerBank application.
"""

from PyInstaller.utils.hooks import copy_metadata
from pathlib import Path
import sys
import os

# Dynamically find the Python DLL from the base Python installation, not the venv
base_prefix = getattr(sys, "base_prefix", sys.prefix)
python_dll_name = f'python{sys.version_info.major}{sys.version_info.minor}.dll'
python_dll_path = os.path.join(base_prefix, python_dll_name)
if not os.path.exists(python_dll_path):
    raise FileNotFoundError(f"Could not find {python_dll_name} in base path {base_prefix}")

# --- Base Configuration ---
# This section is shared with onedir.spec
APP_NAME = "SimpleTimerBank"
block_cipher = None
a = Analysis(
    ['src/simpletimerbank/main.py'],
    pathex=[],
    binaries=[(python_dll_path, '_internal')],
    datas=[
        ('assets', 'assets'),
        ('DSEG-LICENSE.txt', '.')
    ],
    hiddenimports=[
        'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
        'simpletimerbank.core', 'simpletimerbank.gui'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'pydoc', 'doctest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- Single-File Specific Configuration ---
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
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
    version='version_info.txt' if sys.platform == 'win32' and Path('version_info.txt').exists() else None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
) 
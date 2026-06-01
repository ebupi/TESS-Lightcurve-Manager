# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# Determine path separator based on OS
char_sep = ';' if sys.platform.startswith('win') else ':'

a = Analysis(
    ['../TESS_Araci.py'],
    pathex=[],
    binaries=[],
    datas=[('../tess_icon_v2.png', '.')],
    hiddenimports=['PyQt5.QtWebEngineWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'bokeh', 'sklearn', 'scikit-learn', 'joblib', 
        'tornado', 'nbformat', 'nbconvert', 'jupyter', 'notebook',
        'ipython', 'jedi', 'pygments'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TESS_Lightcurve_Studio',
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
    icon=['../gemini.ico'] if sys.platform.startswith('win') else None,
)

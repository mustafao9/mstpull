# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('locales', 'locales'),
        ('assets', 'assets'),
        ('icon.ico', '.'),
        ('icon.png', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MstPull',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                      # Konsol penceresini kapalı tutar
    disable_windowed_traceback=True,   # Hata durumunda siyah konsol penceresi açılmasını engeller
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',                   # Exe içine gömülen ikon
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MstPull',
)

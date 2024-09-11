# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[('config.py', '.'), ('config_mr.txt', '.'), ('TB_rul.txt', '.'), ('anki_sync_mac.sh', '.'), ('review_time.txt', '.'), ('fupan.py', '.'), ('anki.py', '.'), ('flomo.py', '.')],
    hiddenimports=['requests', 'lxml', 'pytz', 'bs4', 'certifi', 'jaraco.text', 'jaraco.context', 'jaraco.functools', 'more_itertools'],
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
    a.binaries,
    a.datas,
    [],
    name='TbReview',
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
)
app = BUNDLE(
    exe,
    name='TbReview.app',
    icon=None,
    bundle_identifier=None,
)

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['galaxy.py'],
    pathex=[],
    binaries=[],
    datas=[('images', 'images'), ('audio', 'audio')],
    hiddenimports=['kivy.deps.sdl2', 'kivy.deps.glew', 'kivy.deps.gstreamer', 'kivy.core.text.markup'],
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
    name='galaxy',
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

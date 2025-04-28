# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\Users\\juanc\\Documents\\NUVU\\LectorCode\\main.py'],
    pathex=[],
    binaries=[('c:\\Users\\juanc\\Documents\\NUVU\\LectorCode\\temp_dlls\\libiconv.dll', '.'), ('c:\\Users\\juanc\\Documents\\NUVU\\LectorCode\\temp_dlls\\libzbar-64.dll', '.')],
    datas=[('c:\\Users\\juanc\\Documents\\NUVU\\LectorCode\\src\\ui\\ui_files', 'src/ui/ui_files')],
    hiddenimports=[],
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
    name='LectorCode',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LectorCode',
)

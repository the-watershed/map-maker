# map-maker.spec
block_cipher = None

a = Analysis(['map-maker.py'],
             pathex=['C:\\Users\\tejur\\OneDrive\\Documents\\repos\\tools\\map-maker\\map-maker.py'],
             binaries=[],
             datas=[('map1.json', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='map-maker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon='path\\to\\your\\icon.ico',
          asymptote_version=None,
          asymptote_dir=None)
# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None


a = Analysis(['main.py'],
             pathex=[os.getcwd()],
             binaries=[],
             datas=[('Fonts/Verdana.ttf', 'Fonts/Verdana.ttf'),
                    ('Jungle Asset Pack/Charaacter/sprites/*', 'Jungle Asset Pack/Charaacter/sprites'),
                    ('Jungle Asset Pack/Jungle tileset/jungle tileset.png', 'Jungle Asset Pack/Jungle tileset/jungle tileset.png')
             ],
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
          name='Jungle Climb',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
#coll = COLLECT(exe,
#               a.binaries,
#               a.zipfiles,
#               a.datas,
#               strip=False,
#               upx=True,
#               upx_exclude=[],
#               name='Jungle Climb')

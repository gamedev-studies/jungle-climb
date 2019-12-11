from cx_Freeze import setup, Executable

NAME = 'Jungle Climb'
executables = [Executable('main.py', base='Win32GUI', icon='Resources/Jungle Climb Icon.ico', targetName=NAME)]

setup(
    name=NAME,
    silent=True,
    version='1.3',
    description=NAME,
    copyright='Copyright 2019 Elijah Lopez',
    options={'build_exe': {'packages': ['pygame', 'PIL'],
                           'include_files': [
                               ('Jungle Asset Pack/jungle tileset/jungle tileset.png',
                                'Jungle Asset Pack/jungle tileset/jungle tileset.png'),
                               ('Jungle Asset Pack/Character/sprites/', 'Jungle Asset Pack/Character/sprites/'),
                               'Fonts/', 'Audio/']}},
    executables=executables)

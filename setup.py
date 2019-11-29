from cx_Freeze import setup, Executable

executables = [Executable('main.py', base='Win32GUI', icon='Resources/Jungle Climb Icon.ico')]

setup(
    name='Jungle Climb',
    options={'build_exe': {'packages':['pygame', 'PIL'],
                           'include_files':[
                               ('Jungle Asset Pack/jungle tileset/jungle tileset.png', 'Jungle Asset Pack/jungle tileset/jungle tileset.png'),
                               ('Jungle Asset Pack/Character/sprites/', 'Jungle Asset Pack/Character/sprites/'),
                               'Fonts/']}},
    executables = executables)
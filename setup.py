from cx_Freeze import setup, Executable

NAME = 'Jungle Climb'
executables = [Executable('main.py', base='Win32GUI', icon='Resources/Jungle Climb Icon.ico', targetName=NAME)]

setup(
    name=NAME,
    version='1.4',
    description=f'{NAME} Copyright 2019 Elijah Lopez',
    options={'build_exe': {'packages': ['pygame'],
                           'include_files': ['Assets'],
                           'excludes': ['tkinter', 'PySide2', 'PyQt5', 'numpy', 'pillow', 'multiprocessing', 'email', 'json', 'test', 'unittest'],
                           'optimize': 2
                           }},
    executables=executables)

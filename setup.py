import cx_Freeze
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

executables = [cx_Freeze.Executable('main.py')]

cx_Freeze.setup(
    name='Jungle Climb Alpha',
    options={
        'build_exe': {
            'packages': ['pygame'],
            'include_files': [
                'Jungle Asset Pack/jungle tileset/jungle tileset.png',
                'Jungle Asset Pack/Character with outline/sprites',
                os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
            ]
        }
    },
    executables=executables,
    version='1.0.0'
)

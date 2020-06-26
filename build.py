from cx_Freeze import setup, Executable
import subprocess
import sys
from main import VERSION
from datetime import datetime


NAME = 'Jungle Climb'
SETUP_OUTPUT_NAME = 'Jungle Climb Setup'
PACKAGES = ['pygame']
print('Installing dependencies...')
subprocess.check_call('pip install --upgrade -r requirements.txt', stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
installed_packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode('utf-8')
installed_packages = installed_packages.split('\r\n')
EXCLUDES = {pkg.split('==')[0] for pkg in installed_packages if pkg != ''}
EXCLUDES.add('tkinter')
for pkg in PACKAGES:
    EXCLUDES.remove(pkg)

with open('setup_script.iss', 'r+') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith('#define MyAppVersion'):
            lines[i] = f'#define MyAppVersion "{VERSION}"\n'
        elif line.startswith('OutputBaseFilename'):
            lines[i] = f'OutputBaseFilename={SETUP_OUTPUT_NAME}\n'
            break
    f.seek(0)
    f.writelines(lines)
    f.truncate()

copyright_text = f'Copyright 2019 - {datetime.now().year} Elijah Lopez'
executables = [Executable('main.py', base='Win32GUI', icon='resources/Jungle Climb Icon.ico', targetName=NAME)]
setup(name=NAME, version=VERSION, description=f'{NAME} {copyright_text}',
    options={'build_exe': {'packages': PACKAGES,
                           'include_files': ['assets'],
                           'excludes': EXCLUDES,
                           'optimize': 2}},
    executables=executables)

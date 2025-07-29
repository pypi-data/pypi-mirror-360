#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#

import os
import platform
import subprocess
import sys
import zipfile

from aos_prov.commands.download import download_and_save_file
from aos_prov.utils.common import DOWNLOADS_PATH, VIRTUAL_BOX_DOWNLOAD_URL, VBOX_SDK_PATH

if platform.system() == 'Linux':
    sys.path.append('/usr/lib/virtualbox')
    sys.path.append('/usr/lib/virtualbox/sdk/bindings/xpcom/python/')
elif platform.system() == 'Darwin':
    sys.path.append('/Applications/VirtualBox.app/Contents/MacOS')
    sys.path.append('/Applications/VirtualBox.app/Contents/MacOS/sdk/bindings/xpcom/python/')

def install_vbox_sdk():
    download_and_save_file(VIRTUAL_BOX_DOWNLOAD_URL, VBOX_SDK_PATH, True)

    with zipfile.ZipFile(VBOX_SDK_PATH, 'r') as zip_ref:
        zip_ref.extractall(DOWNLOADS_PATH)

    envs = os.environ.copy()
    if platform.system() == 'Windows':
        command = ['python', 'vboxapisetup.py', 'install', '--user']
    elif platform.system() == 'Linux':
        'VBOX_INSTALL_PATH=$(which virtualbox)'
        command = ['python3', 'vboxapisetup.py', 'install', '--user', '--prefix=']
    elif platform.system() == 'Darwin':
        'VBOX_INSTALL_PATH=/Applications/VirtualBox.app/Contents/MacOS'
        command = ['python3', 'vboxapisetup.py', 'install', '--user', '--prefix=']
    else:
        command = 'VBOX_INSTALL_PATH=$(which virtualbox) python3 vboxapisetup.py install --user --prefix='
    return_code = subprocess.run(command, shell=True, env=envs, cwd=str(
        zipfile.Path(DOWNLOADS_PATH / 'sdk' / 'installer')))
    if return_code.returncode == 0:
        return
    else:
        print('Error installing VirtualBox SDK')

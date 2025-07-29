#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#

import random
import string
from pathlib import Path

from rich.console import Console

CONTENT_ENCRYPTION_ALGORITHM = 'aes256_cbc'
DOWNLOADS_PATH = Path.home() / '.aos' / 'downloads'
AOS_DISKS_PATH = DOWNLOADS_PATH

# Multinode images
NODE0_IMAGE_FILENAME = 'aos-vm-node0-genericx86-64.wic.vmdk'
NODE1_IMAGE_FILENAME = 'aos-vm-node1-genericx86-64.wic.vmdk'
# Multinode dynamic images
NODE_MAIN_IMAGE_FILENAME = 'aos-vm-main-genericx86-64.vmdk'
NODE_SECONDARY_IMAGE_FILENAME = 'aos-vm-secondary-genericx86-64.vmdk'

DISK_DOWNLOAD_HOST = 'https://github.com/aosedge/meta-aos-vm/releases/download'
DISK_IMAGE_DOWNLOAD_URL = f'{DISK_DOWNLOAD_HOST}/v5.2.0/aos-vm-image-genericx86-64-5.2.0.tar.xz'
REQUEST_TIMEOUT = 30
MAX_WAIT_SECONDS_DURING_PROVISIONING = 300

console = Console()
error_console = Console(stderr=True, style='red')
ALLOW_PRINT = True


def print_message(formatted_text, end='\n', ljust: int = 0):
    if ALLOW_PRINT:
        if ljust > 0:
            formatted_text = formatted_text.ljust(ljust)
        console.print(formatted_text, end=end)


def print_left(formatted_text, ljust=80):
    print_message(formatted_text, end='', ljust=ljust)


def print_done():
    print_message('[green]DONE')


def print_success(message):
    print_message(f'[green]{str(message)}')  # noqa: WPS237


def print_error(message):
    if ALLOW_PRINT:
        error_console.print(message)


def generate_random_password() -> str:
    """
    Generate random password from letters and digits.

    Returns:
        str: Random string password
    """
    dictionary = string.ascii_letters + string.digits
    password_length = random.randint(10, 15)  # noqa: S311,WPS432
    return ''.join(random.choice(dictionary) for _ in range(password_length))  # noqa: S311

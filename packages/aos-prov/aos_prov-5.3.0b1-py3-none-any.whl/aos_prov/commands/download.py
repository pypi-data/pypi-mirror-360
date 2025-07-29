#
#  Copyright (c) 2018-2025 Renesas Inc.
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#
"""Download and save files command."""
import os
import tarfile
from pathlib import Path

import requests
from aos_prov.utils.common import (
    DOWNLOADS_PATH,
    NODE_MAIN_IMAGE_FILENAME,
    NODE_SECONDARY_IMAGE_FILENAME,
    REQUEST_TIMEOUT,
    print_left,
    print_success,
)
from aos_prov.utils.errors import AosProvError
from rich.progress import Progress

_SAVE_CHUNK = 8192


def _create_downloads_directory():
    Path(DOWNLOADS_PATH).mkdir(parents=True, exist_ok=True)


def download_and_save_multinode(
    download_url: str,
    save_path: Path,
    force_overwrite: bool = False,
) -> None:
    """Download and save multi-node images.

    Args:
         download_url (str): URL to download
         save_path (Path): Save destination url
         force_overwrite (bool): Force to overwrite files

    Raises:
        AosProvError: If files exists and force_overwrite is false.
    """
    _create_downloads_directory()

    node_files = [
        save_path / NODE_MAIN_IMAGE_FILENAME,
        save_path / NODE_SECONDARY_IMAGE_FILENAME,
    ]

    for node_file in node_files:
        if force_overwrite:
            if os.path.exists(node_file):
                os.remove(node_file)
        elif node_file.exists():
            raise AosProvError(f'Destination file {node_file} already exist. Delete it or download with -f key')

    download_file_name = save_path / 'downloaded-multi-node-images.tar.gz'

    with open(download_file_name, 'wb') as save_context:
        response = requests.get(download_url, stream=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            save_context.write(response.content)
            return

        with Progress() as progress:
            task_id = progress.add_task('[cyan]Downloading...', total=int(total_length))
            for received_data in response.iter_content(chunk_size=_SAVE_CHUNK):
                progress.update(task_id, advance=len(received_data))
                save_context.write(received_data)

    print_left('Extracting downloaded files...')

    with tarfile.open(download_file_name) as archive:
        archive.extractall(save_path)  # noqa: S202

    if os.path.exists(download_file_name):
        os.remove(download_file_name)

    print_success('DONE')

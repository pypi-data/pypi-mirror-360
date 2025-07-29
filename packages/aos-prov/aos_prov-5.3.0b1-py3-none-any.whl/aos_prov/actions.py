#
#  Copyright (c) 2018-2025 Renesas Inc.
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#
# pylint: disable=R0913
"""aos-prov supported actions module."""
import time
from typing import Optional

from aos_prov.commands.command_provision import run_provision
from aos_prov.commands.command_vm_multi_node_manage import (
    add_node_to_unit_by_vm_group,
    new_vms,
    remove_node_to_unit_by_node,
    remove_vms_in_group,
    start_vms,
)
from aos_prov.commands.download import download_and_save_multinode
from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.utils.common import DOWNLOADS_PATH, print_message


def provision_unit(unit_address: str, cloud_api: CloudAPI, reconnect_times: int = 1, nodes_count: int = 2) -> None:
    """
    Do a provisioning process for the unit.

    Args:
        unit_address (str): address:port of the unit.
        cloud_api (CloudAPI): instance of CloudAPI with user info.
        reconnect_times (int): Number of connections retries.
        nodes_count (int): Number of nodes in the VM group.
    """
    run_provision(unit_address, cloud_api, reconnect_times, nodes_count=nodes_count)


def create_new_unit(  # noqa: WPS211
    vm_name: str,
    cloud_api: Optional[CloudAPI],
    disk_location: str,
    do_provision=False,
    reconnect_times: int = 1,
    nodes_count=2,
    headless=False,
    check_software=False,
):
    """
    Create a new VirtualBox multi-node Unit.

    Args:
        vm_name (str): Name of the group of units.
        cloud_api (CloudAPI): instance of CloudAPI with user info.
        disk_location (str): Full path to the folder with nodes images.
        do_provision (Boolean): Provision unit after creation or not.
        reconnect_times (int): Number of connections retries.
        nodes_count (int): Count of nodes to create. Supported 1 or 2 nodes.
        headless (bool): Start VM in headless mode if True
        check_software (bool): Check software compatibility if True.

    Returns:
        [provisioning_port, node0_ssh_port, node1_ssh_port]: Forwarded ports.
    """
    provisioning_port, node0_ssh_port, node1_ssh_port = new_vms(vm_name, disk_location, nodes_count)

    if do_provision and cloud_api:
        cloud_api.check_cloud_access()
        if check_software:
            cloud_api.check_supported_software()
        start_vms(f'/AosUnits/{vm_name}', headless=headless)
        time.sleep(10)
        run_provision(
            f'127.0.0.1:{provisioning_port}',
            cloud_api,
            reconnect_times=reconnect_times,
            nodes_count=nodes_count,
        )

    return [provisioning_port, node0_ssh_port, node1_ssh_port]


def add_node_to_unit(
    vm_name: str,
    disk_location: str,
    start=True,
    headless=False,
):
    """
    Add a new node to already presented VirtualBox multi-node Unit.

    Args:
        vm_name (str): Name of the group of units.
        disk_location (str): Full path to the folder with nodes images.
        start (bool): Start VM if True.
        headless (bool): Start VM in headless mode if True.
    """
    add_node_to_unit_by_vm_group(vm_name, disk_location, start, headless)


def remove_node_from_unit(
    vm_name: str,
    node_name: str,
    reboot: bool = True,
):
    """
    Remove a node from already presented VirtualBox multi-node Unit.

    Args:
        vm_name (str): Name of the group of units.
        node_name (str): Name of the node.
        reboot (bool): Flag of rebooting VM Group.
    """
    remove_node_to_unit_by_node(vm_name, node_name, reboot)


def remove_vm_unit(name: str) -> None:
    """Remove all VMs in the group.

    Args:
        name (str): Name of the group for removing without root AosUnits group.
    """
    remove_vms_in_group(name)


def start_vm_unit(name: str, headless=False) -> None:
    """Start all VMs in the group.

    Args:
        name (str): Name of the group to start without root AosUnits group.
        headless (bool): Start VM in headless mode if True.
    """
    start_vms(f'/AosUnits/{name}', check_virtualbox=True, headless=headless)


def download_image(download_url: str, force: bool = False) -> None:
    """
    Download unit image.

    Args:
        download_url (str): URL to download from.
        force (bool): If set downloaded image will overwrite existing one.
    """
    download_and_save_multinode(download_url, DOWNLOADS_PATH, force)
    resolve_download_path = str(DOWNLOADS_PATH.resolve())
    print_message(f'Download finished. You may find Unit images in: [b]{resolve_download_path}[/b]')

#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#

import platform
import socket
import uuid
from pathlib import Path
from random import randint
from shutil import copyfile

from aos_prov.actions import download_image
from aos_prov.commands.vbox_sdk import install_vbox_sdk
from aos_prov.utils.common import DISK_IMAGE_DOWNLOAD_URL, DOWNLOADS_PATH, AOS_DISKS_PATH
from aos_prov.utils.errors import OnBoardingError, AosProvError

try:
    import virtualbox
    from virtualbox.library import (
        StorageBus,
        StorageControllerType,
        IMachine,
        DeviceType,
        AccessMode,
        NATProtocol,
        FirmwareType,
        INATNetwork,
        NetworkAdapterType,
        NetworkAttachmentType
    )
except Exception:
    raise AosProvError('virtualbox library is not installed. Install required libraries with aos-prov[virt]')


def get_virtualbox(install_sdk=True):
    try:
        return virtualbox.VirtualBox()
    except ModuleNotFoundError as error:
        if error.name != 'vboxapi' or not install_sdk:
            raise error

        install_vbox_sdk()
        return virtualbox.VirtualBox()


def __create_storage_controller(machine: IMachine):
    storage_controller = machine.add_storage_controller('AHCI', StorageBus.sata)
    storage_controller.controller_type = StorageControllerType.intel_ahci
    storage_controller.port_count = 1
    storage_controller.use_host_io_cache = True


def __attach_disk(machine: IMachine, location):
    medium = machine.parent.open_medium(
        location,
        DeviceType.hard_disk,
        AccessMode.read_write,
        True
    )
    machine.attach_device('AHCI', 0, 0, DeviceType.hard_disk, medium)


def __check_disk_exist(disk_location: str):
    disk = Path(disk_location)
    if not disk.is_file():
        raise OnBoardingError("Disk file not found")


def new_vm(vm_name: str, disk_location: str):
    print('Creating a new virtual machines...')

    disk_location_path = Path(disk_location)

    if not ((disk_location_path / 'aos-node0.vmdk').exists()) or not ((disk_location_path / 'aos-node1.vmdk').exists()):
        if disk_location_path == AOS_DISKS_PATH:
            print('Local images not found. Downloading...')
            download_image(DISK_IMAGE_DOWNLOAD_URL)
        else:
            raise AosProvError(f'Disk images not found in directory {disk_location}. Can\'t proceed!')

    nodes = [
        {
            'name': 'node0',
            'uuid': str(uuid.uuid4()),
            'disk_name': 'aos-disk-node0.vmdk',
            'disk_location': Path(DOWNLOADS_PATH / 'aos-node0.vmdk')
        },
        {
            'name': 'node1',
            'uuid': str(uuid.uuid4()),
            'disk_name': 'aos-disk-node1.vmdk',
            'disk_location': Path(DOWNLOADS_PATH / 'aos-node1.vmdk')
        }
    ]

    units_network_name = f'aos-network-{vm_name}'
    provisioning_port = create_network(units_network_name)

    for node in nodes:
        create_node_vm(
            node['name'],
            node['uuid'],
            [f'/AosUnits/{vm_name}'],
            node['disk_location'],
            node['disk_name'],
            units_network_name
        )

    return provisioning_port


def create_node_vm(vm_name: str, vm_uuid: str, group: [], original_disk_path: Path, disk_name: str, network_name):
    vbox = virtualbox.VirtualBox()
    vbox.api_version
    machine = vbox.create_machine('', vm_name, group, 'Linux_64', f'UUID={vm_uuid}')
    machine.vram_size = 32
    machine.memory_size = 1024
    machine.cpu_count = 1
    machine.firmware_type = FirmwareType.efi
    machine.bios_settings.ioapic_enabled = platform.system() != 'Windows'
    __create_storage_controller(machine)
    vbox.register_machine(machine)
    destination_image = str((Path(machine.settings_file_path).parent / disk_name).resolve())
    copyfile(original_disk_path.absolute(), destination_image)
    with machine.create_session() as session:
        __attach_disk(session.machine, location=destination_image)
        adapter0 = session.machine.get_network_adapter(0)
        adapter0.attachment_type = NetworkAttachmentType(6)
        adapter0.nat_network = network_name
        session.machine.save_settings()


def create_network(network_name: str) -> int:
    print('Creating network for unit...')
    vbox = virtualbox.VirtualBox()
    network = vbox.create_nat_network(network_name)
    network.i_pv6_enabled = False
    network.need_dhcp_server = True
    network.network = '10.0.0.0/24'
    return forward_provisioning_ports(network)


def start_vms(groups: []):
    print('Starting virtual machines...')
    vbox = virtualbox.VirtualBox()
    machines = vbox.get_machines_by_groups(groups)
    # session = virtualbox.Session()
    for machine in machines:
        vm = machine.launch_vm_process(virtualbox.Session(), "gui", [])
        vm.wait_for_completion(timeout=-1)


def forward_provisioning_ports(network: INATNetwork, forward_to_port=None) -> int:
    if forward_to_port is None:
        forward_to_port = randint(8090, 8999)
        while _is_port_in_use(forward_to_port):
            forward_to_port = randint(8090, 8999)

    print(f'...will forward provisioning port {8089} to {forward_to_port}')
    network.add_port_forward_rule(
        False,
        'provisioningPortForward',
        NATProtocol(1),
        '127.0.0.1',
        forward_to_port,
        '10.0.0.100',
        8089
    )
    return forward_to_port


def _is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

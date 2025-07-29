#
#  Copyright (c) 2018-2025 Renesas Inc.
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#
# pylint: disable=R0912,R0913,R0914,R0915
import os
import platform
import socket
import subprocess
import time
import uuid
from pathlib import Path
from random import randint
from shutil import copyfile

from aos_prov.commands.download import download_and_save_multinode
from aos_prov.utils.common import (
    AOS_DISKS_PATH,
    DISK_IMAGE_DOWNLOAD_URL,
    DOWNLOADS_PATH,
    NODE0_IMAGE_FILENAME,
    NODE1_IMAGE_FILENAME,
    NODE_MAIN_IMAGE_FILENAME,
    NODE_SECONDARY_IMAGE_FILENAME,
    print_done,
    print_error,
    print_left,
    print_message,
    print_success,
)
from aos_prov.utils.errors import AosProvError
from semver import VersionInfo as SemVerInfo

_MIN_PORT = 8090
_MAX_PORT = 8999
_PROVISION_PORT = 8089
_SSH_PORT = 22


def _is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_handler:
        return socket_handler.connect_ex(('localhost', port)) == 0


def _delete_controller(vm_uuid: str, controller_name: str):
    command = [
        'VBoxManage',
        'storagectl',
        vm_uuid,
        f'--name={controller_name}',
        '--controller=',
        '--remove',
    ]
    execute_command(command, catch_error=False)


def _create_storage_controller_ahci(vm_uuid: str, controller_name: str):
    """Create SATA controller for VM.

    Args:
        vm_uuid (str): UUID or Name of VM to attach controller.
         controller_name (str): Name of the controller.
    """
    command = [
        'VBoxManage',
        'storagectl',
        vm_uuid,
        f'--name={controller_name}',
        '--add=sata',
        '--controller=IntelAhci',
        '--portcount=1',
        '--hostiocache=on',
        '--bootable=on',
    ]
    execute_command(command)


def _attach_disk(vm_uuid: str, attach_to_controller_name: str, disk_location: str):
    """Attach a disk file to the controller.

    Args:
         vm_uuid (str): UUID or Name of VM to attach controller.
         attach_to_controller_name (str): Name of the controller where disk will be attached.
         disk_location (str): path to the disk file.
    """
    command = [
        'VBoxManage',
        'storageattach',
        vm_uuid,
        '--storagectl',
        attach_to_controller_name,
        '--port',
        '0',
        '--type',
        'hdd',
        '--medium',
        disk_location,
    ]

    execute_command(command)


def _create_network(network_name: str):
    print_left('Creating a network for the units...')
    command = [
        'VBoxManage',
        'natnetwork',
        'add',
        '--netname',
        network_name,
        '--network',
        '10.0.0.0/24',
        '--enable',
        '--dhcp',
        'on',
    ]
    execute_command(command)
    print_success(f'Network {network_name} has been created')


def _remove_network(network_name: str):
    print_left(f'Removing a network: {network_name} for the units...')
    command = [
        'VBoxManage',
        'natnetwork',
        'remove',
        '--netname',
        network_name,
    ]
    execute_command(command, catch_error=True)
    print_done()


def _find_vm_name(vm_uuid) -> str:
    info_out = request_vm_info(vm_uuid)

    for row in info_out.splitlines():
        param_from_row = row.split('=')
        if param_from_row[0] == 'name':
            return param_from_row[1].replace('"', '')
    return ''


def _find_vm_network(vm_uuid) -> str:
    info_out = request_vm_info(vm_uuid)

    for row in info_out.splitlines():
        param_from_row = row.split('=')
        if param_from_row[0] == 'nat-network1':
            return param_from_row[1].replace('"', '')
    return ''


def _find_vm_macaddress(vm_uuid) -> str:
    info_out = request_vm_info(vm_uuid)

    for row in info_out.splitlines():
        param_from_row = row.split('=')
        if param_from_row[0] == 'macaddress1':
            return param_from_row[1].replace('"', '')
    return ''


def _find_vm_state(vm_uuid) -> str:
    info_out = request_vm_info(vm_uuid)

    for row in info_out.splitlines():
        param_from_row = row.split('=')
        if param_from_row[0] == 'VMState':
            return param_from_row[1].replace('"', '')
    return ''


def _find_vm_ip(vm_uuid, network_name, retry=6) -> str:
    while retry:
        macaddress = _find_vm_macaddress(vm_uuid)
        if not macaddress:
            continue
        print_left(f'Getting IP of {vm_uuid}...')
        info_out = execute_command(
            [
                'VBoxManage',
                'dhcpserver',
                'findlease',
                '--network',
                network_name,
                '--mac-address',
                macaddress,
            ],
            catch_error=True,
        )

        if info_out:
            for row in info_out.splitlines():
                if row.startswith('IP Address:'):
                    param_from_row = row.split(':')
                    vm_ip = param_from_row[1].strip()
                    print_success(vm_ip)
                    return vm_ip
        time.sleep(10)
        print_message('Could not find IP address.')
    return ''


def _find_vm_nvram_file(vm_uuid) -> str:
    info_out = request_vm_info(vm_uuid)

    for row in info_out.splitlines():
        param_from_row = row.split('=')
        if param_from_row[0] == 'NvramFile':
            return param_from_row[1].replace('"', '')
    return ''


def _reset_forward_port_nat_network(network_name: str, forward_name: str):
    print_message(f'Resetting forward ssh port to {forward_name}...')
    command = [
        'VBoxManage',
        'natnetwork',
        'modify',
        '--netname',
        network_name,
        '--port-forward-4',
        'delete',
        forward_name,
    ]
    execute_command(command)


def _check_forward_port_nat_network_exists(network_name: str, forward_name: str) -> bool:
    command = [
        'VBoxManage',
        'natnetwork',
        'list',
        network_name,
    ]

    natnetwork = execute_command(command)
    if natnetwork:
        for row in natnetwork.splitlines():
            if forward_name in row:
                return True
    return False


def _forward_port_for_secondary_vm(vm_name, vm_uuid, network_name, retry=6):
    print_message(f'Trying to forward ssh port to {vm_name}...')
    vm_ip = _find_vm_ip(vm_uuid, network_name, retry=retry)
    if _check_forward_port_nat_network_exists(network_name, f'{vm_name}ssh'):
        _reset_forward_port_nat_network(network_name, f'{vm_name}ssh')
    secondary_ssh_port = _forward_port_nat_network(
        network_name,
        forward_name=f'{vm_name}ssh',
        from_ip=vm_ip,
        from_port=_SSH_PORT,
    )
    print_left(f'Forwarding ssh port to {vm_name}...')
    print_success(secondary_ssh_port)


def _get_count_of_dynamic_node(group):
    vms = execute_command(['VBoxManage', 'list', 'vms'])

    count_of_dynamic_node = 0
    for virtual_machines in vms.splitlines():
        guid = virtual_machines[virtual_machines.find('{') + 1:virtual_machines.find('}')]
        info_out = request_vm_info(guid)

        for row in info_out.splitlines():
            if row.startswith('groups='):
                vm_group = row.replace('"', '').split('=')[1]
                if group == vm_group:
                    count_of_dynamic_node += 1
    return count_of_dynamic_node


def _forward_port_nat_network(network_name: str, forward_name: str, from_ip: str, from_port: int, to_port=None) -> int:
    if to_port is None:
        to_port = randint(_MIN_PORT, _MAX_PORT)  # noqa: S311
        while _is_port_in_use(to_port):
            to_port = randint(_MIN_PORT, _MAX_PORT)  # noqa: S311

    command = [
        'VBoxManage',
        'natnetwork',
        'modify',
        '--netname',
        network_name,
        '--port-forward-4',
        f'{forward_name}:tcp:[]:{to_port}:[{from_ip}]:{from_port}',
    ]

    execute_command(command)
    return to_port


def check_virtual_box():
    print_left('Checking VirtualBox...')

    if platform.machine().lower() not in {'amd64', 'x86_64'}:
        raise AosProvError('Only amd64 architecture is supported.')

    try:
        response = execute_command(['VBoxManage', '--version'], catch_error=False)
    except AosProvError as exc:
        raise AosProvError('VirtualBox is not installed or it is not in the PATH') from exc

    if 'WARNING: The vboxdrv kernel module is not loaded' in response:
        raise AosProvError('VirtualBox kernel modules is not installed.')

    if not response.startswith('7'):
        raise AosProvError('VirtualBox 7 is only supported')

    print_success(response)


def new_vms(vm_name: str, disk_location: str, nodes_count=2, check_virtualbox=True) -> ():
    if check_virtualbox:
        check_virtual_box()
    print_message('Creating a new virtual machines...')

    disk_location_path = Path(disk_location)
    is_image_with_dynamic_nodes = False

    if (disk_location_path / NODE0_IMAGE_FILENAME).exists() and (disk_location_path / NODE1_IMAGE_FILENAME).exists():
        # TODO: remove in case support of old version R4 is not required
        print_message('Found VM image (v4) with supporting static Nodes functionality. Use it as two nodes VM.')

        node0_exists = (disk_location_path / NODE0_IMAGE_FILENAME).exists()
        node1_exists = (disk_location_path / NODE1_IMAGE_FILENAME).exists()
        if not node0_exists or not node1_exists:
            if disk_location_path != AOS_DISKS_PATH:
                raise AosProvError(f'Disk images not found in directory {disk_location}. Cannot proceed!')
            print_message('Local images not found. Downloading...')
            download_and_save_multinode(DISK_IMAGE_DOWNLOAD_URL, DOWNLOADS_PATH, force_overwrite=False)
            print_success('Download finished. You may find Unit images in: ' + str(DOWNLOADS_PATH.resolve()))
        nodes = [
            {
                'name': 'node0',
                'uuid': str(uuid.uuid4()),
                'disk_name': NODE0_IMAGE_FILENAME,
                'disk_location': Path(disk_location_path / NODE0_IMAGE_FILENAME),
            },
        ]

        if nodes_count != 1:
            nodes.append(
                {
                    'name': 'node1',
                    'uuid': str(uuid.uuid4()),
                    'disk_name': NODE1_IMAGE_FILENAME,
                    'disk_location': Path(disk_location_path / NODE1_IMAGE_FILENAME),
                },
            )
    else:
        is_image_with_dynamic_nodes = True
        node_main_exists = (disk_location_path / NODE_MAIN_IMAGE_FILENAME).exists()
        if not node_main_exists:
            if disk_location_path != AOS_DISKS_PATH:
                raise AosProvError(f'Disk images not found in directory {disk_location}. Cannot proceed!')
            print_message('Local images not found. Downloading...')
            download_and_save_multinode(DISK_IMAGE_DOWNLOAD_URL, DOWNLOADS_PATH, force_overwrite=False)
            print_success('Download finished. You may find Unit images in: ' + str(DOWNLOADS_PATH.resolve()))
        nodes = [
            {
                'name': 'main',
                'uuid': str(uuid.uuid4()),
                'disk_name': NODE_MAIN_IMAGE_FILENAME,
                'disk_location': Path(disk_location_path / NODE_MAIN_IMAGE_FILENAME),
            },
        ]

        if nodes_count >= 1:
            if nodes_count > 4:
                print_error(f'Do not supports this count of nodes: {nodes_count}. Proceed with maximum 4 nodes...')
                nodes_count = 4

            for index in range(1, nodes_count, 1):
                nodes.append(
                    {
                        'name': f'secondary-{index}',
                        'uuid': str(uuid.uuid4()),
                        'disk_name': NODE_SECONDARY_IMAGE_FILENAME,
                        'disk_location': Path(disk_location_path / NODE_SECONDARY_IMAGE_FILENAME),
                    },
                )

    units_network_name = f'aos-network-{vm_name}'
    units_vm_group = f'/AosUnits/{vm_name}'
    try:  # noqa: WPS229
        _create_network(units_network_name)
        print_left('Forwarding provisioning port...')
        provisioning_port = _forward_port_nat_network(
            units_network_name,
            forward_name='provisioningPortForward',
            from_ip='10.0.0.100',
            from_port=_PROVISION_PORT,
        )
        print_success(provisioning_port)

        node_main_name = 'main' if is_image_with_dynamic_nodes else 'node0'
        print_left(f'Forwarding ssh port to {node_main_name}...')
        node0_ssh_port = _forward_port_nat_network(
            units_network_name,
            forward_name=f'{node_main_name}ssh',
            from_ip='10.0.0.100',
            from_port=_SSH_PORT,
        )
        print_success(node0_ssh_port)

        node1_ssh_port = None
        if not is_image_with_dynamic_nodes and nodes_count > 1:
            # TODO: remove in case support of old version R4 is not required
            print_left('Forwarding ssh port to node1...')
            node1_ssh_port = _forward_port_nat_network(
                units_network_name,
                forward_name='node1ssh',
                from_ip='10.0.0.101',
                from_port=_SSH_PORT,
            )
            print_success(node1_ssh_port)

        for node in nodes:
            print_left(f'Creating a new VM for {node["name"]}...')
            create_node_vm(
                node['name'],
                node['uuid'],
                units_vm_group,
                node['disk_location'],
                node['disk_name'],
                units_network_name,
            )
            print_done()

        return provisioning_port, node0_ssh_port, node1_ssh_port
    except AosProvError as error:
        print_error('Cannot create VM. Clean up all related resources. Try again.')
        remove_vms_in_group(vm_name)
        raise error


def add_node_to_unit_by_vm_group(
    vm_name: str,
    disk_location: str,
    start=True,
    headless=False,
    check_virtualbox=True,
) -> ():
    if check_virtualbox:
        check_virtual_box()
    print_message(f'Adding a new node to virtual machines {vm_name}...')

    disk_location_path = Path(disk_location)
    if not disk_location_path.exists():
        raise AosProvError(f'Node disk image does not exist: {disk_location_path}')

    detailed_list_vms = _get_detailed_vms_list()

    units_network_name = f'aos-network-{vm_name}'
    units_vm_group = f'/AosUnits/{vm_name}'

    if not detailed_list_vms.get(units_vm_group):
        print_error(f'VM Group: {units_vm_group} is not presented on system.')
        return

    try:
        node_uuid = str(uuid.uuid4())
        vm_count = _get_count_of_dynamic_node(units_vm_group)
        vm_name = f'secondary-{vm_count}'
        print_left(f'Creating a new VM: {vm_name} for {units_vm_group}...')
        create_node_vm(
            vm_name,
            node_uuid,
            units_vm_group,
            disk_location_path,
            os.path.basename(disk_location_path),
            units_network_name,
        )
        print_done()

        if start:
            _start_vm_by_uuid(node_uuid, 'headless' if headless else 'gui')
    except AosProvError as error:
        print_error('Cannot add node to VM. Clean up all related resources. Try again.')
        remove_vms_in_group(vm_name)
        raise error


def create_node_vm(  # noqa: WPS211
    vm_name: str,
    vm_uuid: str,
    group: str,
    original_disk_path: Path,
    disk_name: str,
    network_name,
):
    create_vm_command = [
        'VBoxManage',
        'createvm',
        f'--name={vm_name}',
        '--ostype=Linux_64',
        f'--uuid={vm_uuid}',
        f'--groups={group}',
        '--default',
        '--register',
    ]

    cpu_count = 1
    if platform.system() in {'Windows', 'Darwin'}:
        cpu_count = 4

    set_vm_params = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--memory=1024',
        '--firmware=efi',
        f'--cpus={cpu_count}',
    ]

    set_vm_net = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--nic1=natnetwork',
        f'--nat-network1={network_name}',
    ]

    # Set paravirtualization to KVM
    set_vm_kvm = [
        'VBoxManage',
        'modifyvm',
        vm_uuid,
        '--paravirt-provider=kvm',
    ]

    disable_time_sync = [
        'VBoxManage',
        'setextradata',
        vm_uuid,
        '"VBoxInternal/Devices/VMMDev/0/Config/GetHostTimeDisabled" 1',
    ]

    execute_command(create_vm_command)
    execute_command(set_vm_params)
    execute_command(set_vm_net)
    execute_command(set_vm_kvm)
    execute_command(disable_time_sync)
    _delete_controller(vm_uuid, 'SATA')
    _delete_controller(vm_uuid, 'IDE')
    _create_storage_controller_ahci(vm_uuid, 'SATA')
    enable_flushing = [
        'VBoxManage',
        'setextradata',
        '{' + str(vm_uuid) + '}',
        'VBoxInternal/Devices/ahci/0/LUN#0/Config/IgnoreFlush',
        '0',
    ]
    execute_command(enable_flushing)

    destination_image = str((_find_vm_location(vm_uuid) / disk_name).resolve())
    copyfile(original_disk_path.absolute(), destination_image)

    try:
        _attach_disk(vm_uuid, 'SATA', disk_location=destination_image)
    except AosProvError as error:
        print_error(f'Cannot attach disk {destination_image} to VM. Clean up all related resources. Try again.')
        os.remove(destination_image)
        raise error


def remove_vms_in_group(vm_name: str):
    units_network_name = f'aos-network-{vm_name}'
    vm_group = f'/AosUnits/{vm_name}'

    print_message(f'Removing VMs in Groups: {vm_group} for the units...')

    detailed_list_vms = _get_detailed_vms_list()

    if not detailed_list_vms.get(vm_group):
        print_error(f'VM Group: {vm_group} is not presented on system.')
        return

    for vm_uuid in detailed_list_vms[vm_group]:  # noqa: WPS440
        if _find_vm_state(vm_uuid) == 'running':
            poweroff_vm_command = [
                'VBoxManage',
                'controlvm',
                vm_uuid,
                'poweroff',
            ]
            execute_command(poweroff_vm_command, catch_error=False)
            while True:
                time.sleep(3)
                if _find_vm_state(vm_uuid) == 'poweroff':
                    break

        delete_vm_command = [
            'VBoxManage',
            'unregistervm',
            vm_uuid,
            '--delete',
        ]
        execute_command(delete_vm_command, catch_error=False)
    _remove_network(units_network_name)
    print_message('VMs have been deleted')


def remove_node_to_unit_by_node(vm_name: str, node_name: str, reboot: bool = True):
    if not node_name.startswith('secondary'):
        print_error(f'Node: "{node_name}" cannot be removed. Only secondary nodes are allowed for this operation.')
        return

    vm_group = f'/AosUnits/{vm_name}'

    print_message(f'Removing Node: {node_name} from VM Group: {vm_group}...')

    detailed_list_vms = _get_detailed_vms_list()

    if not detailed_list_vms.get(vm_group):
        print_error(f'VM Group: {vm_group} is not presented on system.')
        return

    is_node_presented = False
    for vm_uuid in detailed_list_vms[vm_group]:  # noqa: WPS440
        if _find_vm_name(vm_uuid) == node_name:
            is_node_presented = True
            if _find_vm_state(vm_uuid) == 'running':
                poweroff_vm_command = [
                    'VBoxManage',
                    'controlvm',
                    vm_uuid,
                    'poweroff',
                ]
                execute_command(poweroff_vm_command, catch_error=False)
                while True:
                    time.sleep(3)
                    if _find_vm_state(vm_uuid) == 'poweroff':
                        break

            delete_vm_command = [
                'VBoxManage',
                'unregistervm',
                vm_uuid,
                '--delete',
            ]
            execute_command(delete_vm_command, catch_error=False)
            print_message(f'Node: {node_name} has been deleted')
    if not is_node_presented:
        print_message(f'Node: {node_name} is not presented into VM Group: {vm_name}.')
        return

    if reboot:
        detailed_list_vms = _get_detailed_vms_list()
        for vm_uuid in detailed_list_vms[vm_group]:  # noqa: WPS440
            resetting_vm_name = _find_vm_name(vm_uuid)
            if _find_vm_state(vm_uuid) == 'running':
                print_message(f'Rebooting: Node: {resetting_vm_name} into VM Group: {vm_name}.')
                reboot_vm_command = [
                    'VBoxManage',
                    'controlvm',
                    vm_uuid,
                    'reset',
                ]
                execute_command(reboot_vm_command, catch_error=False)


def _find_vm_location(vm_uuid) -> Path:
    info_out = request_vm_info(vm_uuid)

    for row in info_out.splitlines():
        param_from_row = row.split('=')
        if param_from_row[0] == 'CfgFile':
            return Path(param_from_row[1].replace('"', '')).parent
    return Path()


def _get_detailed_vms_list() -> dict:
    # find uuids of all VMs into the required Group
    detailed_list_vms_command = [
        'VBoxManage',
        'list',
        'vms',
        '--long',
    ]
    detailed_list_vms_out = execute_command(detailed_list_vms_command, catch_error=True)
    detailed_list_vms = {}
    processed_group_vm = ''
    for output_line in detailed_list_vms_out.splitlines():
        if output_line.startswith('Groups:'):
            # line format is: 'Groups:                      /AosUnits/my-test-vm1'
            if len(output_line.split()) == 2:
                processed_group_vm = output_line.split()[1]
        elif output_line.startswith('UUID:'):
            # line format is: 'UUID:                        49f87eef-838b-43cb-b6eb-604989b15f9f'
            if len(output_line.split()) == 2:
                vm_uuid = output_line.split()[1]
                list_of_uuids = []
                if detailed_list_vms.get(processed_group_vm):
                    list_of_uuids = detailed_list_vms[processed_group_vm]
                if vm_uuid not in list_of_uuids:
                    list_of_uuids.append(vm_uuid)
                    detailed_list_vms[processed_group_vm] = list_of_uuids

    return detailed_list_vms


def start_vms(group: str, check_virtualbox: bool = False, headless=False):
    """Start all VMs in the group.

    Args:
        group (str): Name of the group to start
        check_virtualbox (bool): Check VirtualBox status before execution
        headless (bool): Start VM in headless mode if True

    Raises:
        AosProvError: If no VMs to start found.
    """
    if check_virtualbox:
        check_virtual_box()

    message = f'Starting VMs in group [bold]{group}[/bold]'

    if headless:
        message += ' in headless mode'

    print_message(message)
    vms_to_start = []
    vms = execute_command(['VBoxManage', 'list', 'vms'])

    for virtual_machines in vms.splitlines():
        guid = virtual_machines[virtual_machines.find('{') + 1:virtual_machines.find('}')]
        info_out = request_vm_info(guid)

        for row in info_out.splitlines():
            if row.startswith('groups='):
                vm_group = row.replace('"', '').split('=')[1]
                if group == vm_group:
                    vms_to_start.append(guid)
                    break

    if not vms_to_start:
        raise AosProvError(f'No VMs found in group {group} to start!')

    start_type = 'headless' if headless else 'gui'

    for vm_guid in vms_to_start:
        _start_vm_by_uuid(vm_guid, start_type)


def _check_virtual_box_less_7_1_2() -> (str, bool):  # noqa: WPS114
    response = execute_command(['VBoxManage', '--version'], catch_error=False)
    if len(response.split('r')) > 1:
        version = response.split('r')[0]
    elif len(response.split('-')) > 1:
        version = response.split('-')[0]
    else:
        version = response

    check_result = False
    if version.startswith('6.') or version.startswith('7.') or version.startswith('8.'):
        check_result = SemVerInfo.parse(version) < '7.1.2'

    return version, check_result


def _start_vm_by_uuid(vm_guid, start_type='gui'):
    start_command = ['VBoxManage', 'startvm', vm_guid, f'--type={start_type}']
    print_left(f'Starting VM {vm_guid}...')
    try:
        execute_command(start_command, catch_error=False)
    except AosProvError as exc:
        if 'is already locked by a session' in str(exc):
            print_message('[YELLOW]SKIPPING due to lock')
        else:
            print_message('[RED]ERROR')
            print_error(str(exc))
        raise exc
    print_done()
    version, check_result = _check_virtual_box_less_7_1_2()
    if check_result:
        nvram_file = _find_vm_nvram_file(vm_guid)
        if not nvram_file or not Path(nvram_file).is_file():
            print_message(
                f'VBoxManage {version} < 7.1.2 version is detected. Reboot VM is required for nvram initialization!',
            )
            reboot_vm_command = [
                'VBoxManage',
                'controlvm',
                vm_guid,
                'poweroff',
            ]
            execute_command(reboot_vm_command, catch_error=False)
            print_left(f'Rebooting VM {vm_guid}...')
            while True:
                time.sleep(3)
                if _find_vm_state(vm_guid) == 'poweroff':
                    break

            execute_command(start_command, catch_error=False)
            print_done()

    # port forwarding for secondary nodes with dhcp support
    vm_name = _find_vm_name(vm_guid)
    if vm_name.startswith('secondary'):
        _forward_port_for_secondary_vm(vm_name, vm_guid, _find_vm_network(vm_guid))


def request_vm_info(vm_guid):
    return execute_command(['VBoxManage', 'showvminfo', vm_guid, '--machinereadable'], catch_error=True)


def execute_command(command, catch_error=False) -> str:
    execution_status = subprocess.run(command, shell=False, env=os.environ.copy(), capture_output=True, check=False)
    if execution_status.returncode == 0:
        return execution_status.stdout.decode('utf-8')

    if not catch_error:
        raise AosProvError(execution_status.stderr.decode('utf-8'))

    return execution_status.stdout.decode('utf-8')

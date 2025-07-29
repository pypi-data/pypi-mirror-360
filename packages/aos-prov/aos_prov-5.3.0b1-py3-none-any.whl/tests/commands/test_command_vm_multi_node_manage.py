#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import io
import os.path
import tempfile
import uuid
from pathlib import Path
from subprocess import CompletedProcess

from aos_prov.commands.command_vm_multi_node_manage import (
    _MAX_PORT,
    _MIN_PORT,
    check_virtual_box,
    create_node_vm,
    execute_command,
    new_vms,
    remove_vms_in_group,
    start_vms,
)
from aos_prov.utils.common import (
    NODE0_IMAGE_FILENAME,
    NODE1_IMAGE_FILENAME,
)
from aos_prov.utils.errors import AosProvError
from pytest import raises
from rich.console import Console


def test_execute_command(mocker):
    stdout_message = 'message'
    mocker.patch(
        'subprocess.run',
        return_value=CompletedProcess(None, stdout=stdout_message.encode(), returncode=0),
    )

    assert execute_command('echo') == stdout_message


def test_execute_command_error(mocker):
    stderr_message = 'message'
    mocker.patch(
        'subprocess.run',
        return_value=CompletedProcess(None, stderr=stderr_message.encode(), returncode=1),
    )

    with raises(AosProvError) as exc:
        execute_command('echo', catch_error=False)
    assert stderr_message in str(exc.value)


def test_check_virtual_box(mocker):
    stdout_message = '7.0.12r159484'
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    mocker.patch('platform.machine', return_value='amd64')
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    check_virtual_box()
    assert 'Checking VirtualBox...' in console_patched.file.getvalue()
    assert stdout_message in console_patched.file.getvalue()


def test_check_virtual_box_unsupported_platform(mocker):
    mocker.patch('platform.machine', return_value='armv7')
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    with raises(AosProvError) as exc:
        check_virtual_box()
    assert 'Only amd64 architecture is supported.' in str(exc.value)
    assert 'Checking VirtualBox...' in console_patched.file.getvalue()


def test_check_virtual_box_not_installed(mocker):
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        side_effect=AosProvError(),
    )
    mocker.patch('platform.machine', return_value='amd64')
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    with raises(AosProvError) as exc:
        check_virtual_box()
    assert 'VirtualBox is not installed or it is not in the PATH' in str(exc.value)
    assert 'Checking VirtualBox...' in console_patched.file.getvalue()


def test_check_virtual_box_not_loaded_kernel_monules(mocker):
    stdout_message = 'WARNING: The vboxdrv kernel module is not loaded'
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    mocker.patch('platform.machine', return_value='amd64')
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    with raises(AosProvError) as exc:
        check_virtual_box()
    assert 'VirtualBox kernel modules is not installed.' in str(exc.value)
    assert 'Checking VirtualBox...' in console_patched.file.getvalue()


def test_check_virtual_box_not_7(mocker):
    stdout_message = '6.0.12r159484'
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    mocker.patch('platform.machine', return_value='amd64')
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    with raises(AosProvError) as exc:
        check_virtual_box()
    assert 'VirtualBox 7 is only supported' in str(exc.value)
    assert 'Checking VirtualBox...' in console_patched.file.getvalue()


def test_create_node_vm_multinode(mocker):
    stdout_message = '7.0.12r159484'
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    m_copyfile = mocker.patch('aos_prov.commands.command_vm_multi_node_manage.copyfile')

    with tempfile.TemporaryDirectory() as tmp_directory:
        create_node_vm(
            'vm_name',
            uuid.uuid4(),
            'group',
            Path(tmp_directory),
            'node1',
            'network1',
        )
    assert m_copyfile.call_count == 1


def test_create_node_vm_onenode(mocker):
    stdout_message = '7.0.12r159484'
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    m_copyfile = mocker.patch('aos_prov.commands.command_vm_multi_node_manage.copyfile')

    with tempfile.TemporaryDirectory() as tmp_directory:
        create_node_vm(
            'vm_name',
            uuid.uuid4(),
            'group',
            Path(tmp_directory),
            'node1',
            'network1',
        )
    assert m_copyfile.call_count == 1


def test_remove_vms_in_group(mocker):
    stdout_message = """
Name:                        node0
Encryption:     disabled
Groups:                      /AosUnits/R4
Guest OS:                    Other Linux (64-bit)
UUID:                        6f400be7-5178-4f79-898c-90a86350eec1

Name:                        node1
Encryption:     disabled
Groups:                      /AosUnits/R4
Guest OS:                    Other Linux (64-bit)
UUID:                        156f8a8c-7f5d-4332-a793-f9fe961e966e
    """
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )
    remove_vms_in_group('R4')
    assert 'Removing VMs in Groups: /AosUnits/R4 for the units...' in console_patched.file.getvalue()
    assert 'VMs have been deleted' in console_patched.file.getvalue()


def test_remove_vms_in_group_not_found(mocker):
    stdout_message = """
Name:                        node0
Encryption:     disabled
Groups:                      /AosUnits/R4
Guest OS:                    Other Linux (64-bit)
UUID:                        6f400be7-5178-4f79-898c-90a86350eec1

Name:                        node1
Encryption:     disabled
Groups:                      /AosUnits/R4
Guest OS:                    Other Linux (64-bit)
UUID:                        156f8a8c-7f5d-4332-a793-f9fe961e966e
    """
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )
    error_console_patched = mocker.patch(
        'aos_prov.utils.common.error_console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True, stderr=True),
    )
    remove_vms_in_group('R3')
    assert 'Removing VMs in Groups: /AosUnits/R3 for the units...' in console_patched.file.getvalue()
    assert 'VM Group: /AosUnits/R3 is not presented on system.' in error_console_patched.file.getvalue()


def test_start_vms(mocker):
    mocker.patch('platform.machine', return_value='amd64')
    vm_list = """
"node0" {a87f7c95-adf2-4a6c-ae64-706df2b31f5e}
"node0" {8cfe08c1-32bb-4d7e-8a5c-8e30b687bb30}
"node0" {6f400be7-5178-4f79-898c-90a86350eec1}
"node1" {156f8a8c-7f5d-4332-a793-f9fe961e966e}
"node0" {ccc6ed3a-ddf2-4457-8cdf-0851f27d0e18}
    """
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=vm_list,
    )
    vm_info = """
name="node0"
Encryption:     disabled
groups="/AosUnits/R4"
ostype="Other Linux (64-bit)"
UUID="a87f7c95-adf2-4a6c-ae64-706df2b31f5e"
    """
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.request_vm_info',
        return_value=vm_info,
    )
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )
    start_vms('/AosUnits/R4', False)
    assert 'Starting VMs in group /AosUnits/R4' in console_patched.file.getvalue()
    assert 'Starting VM a87f7c95-adf2-4a6c-ae64-706df2b31f5e...' in console_patched.file.getvalue()
    assert 'DONE' in console_patched.file.getvalue()


def test_start_vms_error(mocker):
    mocker.patch('platform.machine', return_value='amd64')
    vm_list = """
"node0" {a87f7c95-adf2-4a6c-ae64-706df2b31f5e}
"node0" {8cfe08c1-32bb-4d7e-8a5c-8e30b687bb30}
"node0" {6f400be7-5178-4f79-898c-90a86350eec1}
"node1" {156f8a8c-7f5d-4332-a793-f9fe961e966e}
"node0" {ccc6ed3a-ddf2-4457-8cdf-0851f27d0e18}
    """
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=vm_list,
    )
    vm_info = """
name="node0"
Encryption:     disabled
groups="/AosUnits/R4"
ostype="Other Linux (64-bit)"
UUID="a87f7c95-adf2-4a6c-ae64-706df2b31f5e"
    """
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.request_vm_info',
        return_value=vm_info,
    )
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )
    with raises(AosProvError) as exc:
        start_vms('/AosUnits/R3', False)
    assert 'Starting VMs in group /AosUnits/R3' in console_patched.file.getvalue()
    assert 'No VMs found in group /AosUnits/R3 to start!' in str(exc.value)


def test_new_vms_multinode(mocker):
    stdout_message = '100'
    mocker.patch(
        'aos_prov.commands.command_vm_multi_node_manage.execute_command',
        return_value=stdout_message,
    )
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )
    mocker.patch('aos_prov.commands.command_vm_multi_node_manage.copyfile')

    with tempfile.TemporaryDirectory() as tmp_directory:
        node0_tmp_file = open(os.path.join(tmp_directory, NODE0_IMAGE_FILENAME), 'w')
        node0_tmp_file.write('data')
        node0_tmp_file.close()
        node1_tmp_file = open(os.path.join(tmp_directory, NODE1_IMAGE_FILENAME), 'w')
        node1_tmp_file.write('data')
        node1_tmp_file.close()
        provisioning_port, node0_ssh_port, node1_ssh_port = new_vms('vm_name', tmp_directory, 2, False)
        assert provisioning_port in range(_MIN_PORT - 1, _MAX_PORT + 1)
        assert node0_ssh_port in range(_MIN_PORT - 1, _MAX_PORT + 1)
        assert node1_ssh_port in range(_MIN_PORT - 1, _MAX_PORT + 1)
        assert 'Creating a new virtual machines...' in console_patched.file.getvalue()
        assert 'Forwarding provisioning port...' in console_patched.file.getvalue()
        assert 'Forwarding ssh port to node0...' in console_patched.file.getvalue()
        assert 'Forwarding ssh port to node1...' in console_patched.file.getvalue()
        assert 'Creating a new VM for node0...' in console_patched.file.getvalue()
        assert 'DONE' in console_patched.file.getvalue()
        assert 'Creating a new VM for node1...' in console_patched.file.getvalue()
        assert 'DONE' in console_patched.file.getvalue()


def test_new_vms_disks_not_found(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    with tempfile.TemporaryDirectory() as tmp_directory:
        with raises(AosProvError) as exc:
            new_vms(
                'vm_name',
                tmp_directory,
                2,
                False,
            )
        assert 'Creating a new virtual machines...' in console_patched.file.getvalue()
        assert f'Disk images not found in directory {tmp_directory}. Cannot proceed!' in str(exc.value)

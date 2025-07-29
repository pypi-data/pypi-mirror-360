#
#  Copyright (c) 2018-2025 Renesas Inc.
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#
import io
import tempfile

from aos_prov.actions import (
    create_new_unit,
    download_image,
    provision_unit,
    remove_vm_unit,
    start_vm_unit,
)
from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.utils.common import DOWNLOADS_PATH
from aos_prov.utils.user_credentials import UserCredentials
from rich.console import Console
from tests.fixtures import (
    generate_ca_key_and_cert,
    generate_test_key_certificate,
    key_cert_to_pkcs12,
)


def test_provision_unit(mocker):
    run_provision = mocker.patch('aos_prov.actions.run_provision')

    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
        temp_cert.write(pkcs_12_cert)
        temp_cert.seek(0)
        uc = UserCredentials(temp_cert.name)

        cloud_api = CloudAPI(uc)
        provision_unit('unit_address', cloud_api)
        assert run_provision.call_count == 1


def test_create_new_unit(mocker):
    m_cloud_api_check_cloud_access = mocker.patch('aos_prov.actions.CloudAPI.check_cloud_access')
    m_cloud_api_check_supported_software = mocker.patch('aos_prov.actions.CloudAPI.check_supported_software')
    new_vms = mocker.patch('aos_prov.actions.new_vms', return_value=(1, 2, 3))
    start_vms = mocker.patch('aos_prov.actions.start_vms')
    run_provision = mocker.patch('aos_prov.actions.run_provision')
    mocker.patch('time.sleep')

    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
        temp_cert.write(pkcs_12_cert)
        temp_cert.seek(0)
        uc = UserCredentials(temp_cert.name)

        cloud_api = CloudAPI(uc)
        provisioning_port, node0_ssh_port, node1_ssh_port = create_new_unit(
            'vm_name',
            cloud_api,
            'disk_location',
            do_provision=True,
            check_software=True,
        )
        assert m_cloud_api_check_cloud_access.call_count == 1
        assert m_cloud_api_check_supported_software.call_count == 1
        assert new_vms.call_count == 1
        assert start_vms.call_count == 1
        assert run_provision.call_count == 1
        assert provisioning_port == 1
        assert node0_ssh_port == 2
        assert node1_ssh_port == 3


def test_remove_vm_unit(mocker):
    remove_vms_in_group = mocker.patch('aos_prov.actions.remove_vms_in_group')
    remove_vm_unit('vm_unit')
    assert remove_vms_in_group.call_count == 1


def test_start_vm_unit(mocker):
    start_vms = mocker.patch('aos_prov.actions.start_vms')
    start_vm_unit('vm_unit')
    assert start_vms.call_count == 1


def test_download_image(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )
    download_and_save_multinode = mocker.patch('aos_prov.actions.download_and_save_multinode')
    download_image('download_url')
    assert download_and_save_multinode.call_count == 1

    resolve_download_path = str(DOWNLOADS_PATH.resolve())
    console_message = f'Download finished. You may find Unit images in: {resolve_download_path}\n'
    assert console_message == console_patched.file.getvalue()

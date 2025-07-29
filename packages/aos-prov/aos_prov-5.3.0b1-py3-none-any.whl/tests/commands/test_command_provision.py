#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import io
import tempfile

from aos_prov.commands.command_provision import COMMAND_TO_DECRYPT, run_provision
from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.utils.errors import GrpcUnimplemented, UnitError
from aos_prov.utils.unit_certificate import UnitCertificate
from aos_prov.utils.user_credentials import UserCredentials
from pytest import raises
from rich.console import Console
from tests.fixtures import (
    generate_ca_key_and_cert,
    generate_test_key_certificate,
    key_cert_to_pkcs12,
)


def test_provision_unit_v4(mocker):

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_system_info', side_effect=GrpcUnimplemented(),
    )

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_protocol_version', side_effect=GrpcUnimplemented(),
    )

    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    get_system_info = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_system_info', return_value=('system_id', 'model'),
    )
    get_protocol_version = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_protocol_version', return_value=4,
    )
    get_all_node_ids = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_all_node_ids', return_value=['node1', 'node2'],
    )
    get_cert_types = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_cert_types',
        return_value=['online', 'offline', COMMAND_TO_DECRYPT],
    )
    clear = mocker.patch('aos_prov.commands.command_provision.UnitCommunicationV4.clear', return_value=None)
    set_cert_owner = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.set_cert_owner', return_value=None,
    )
    encrypt_disk = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.encrypt_disk', return_value=None,
    )
    uc = UnitCertificate()
    uc.cert_type = 'online'
    uc.node_id = 'node1'
    create_keys = mocker.patch('aos_prov.commands.command_provision.UnitCommunicationV4.create_keys', return_value=uc)
    apply_certificate = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.apply_certificate', return_value=None,
    )
    finish_provisioning = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.finish_provisioning', return_value=None,
    )

    mocker.patch('aos_prov.communication.cloud.cloud_api.CloudAPI.check_unit_is_not_provisioned', return_value=None)
    mocker.patch(
        'aos_prov.communication.cloud.cloud_api.CloudAPI.register_device',
        return_value={
            'system_uid': 'system_id',
            'online_certificate': 'online_certificate_content',
            'offline_certificate': 'offline_certificate_content',
            'additional_certs': [
                {
                    'cert_type': COMMAND_TO_DECRYPT,
                    'node_id': 'node1',
                    'cert': 'cert_content',
                },
            ],
        },
    )
    mocker.patch('aos_prov.communication.cloud.cloud_api.CloudAPI.get_unit_link_by_system_uid', return_value='link')

    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
        temp_cert.write(pkcs_12_cert)
        temp_cert.seek(0)
        uc = UserCredentials(temp_cert.name)

        cloud_api = CloudAPI(uc)
        run_provision('unit_address', cloud_api)

    assert get_system_info.call_count == 1
    assert get_protocol_version.call_count == 1
    assert get_all_node_ids.call_count == 1
    assert get_cert_types.call_count == 2
    assert set_cert_owner.call_count == 5
    assert clear.call_count == 5
    assert encrypt_disk.call_count == 1
    assert create_keys.call_count == 4
    assert apply_certificate.call_count == 4
    assert finish_provisioning.call_count == 1
    assert 'Starting provisioning...\n' in console_patched.file.getvalue()
    assert 'Finished successfully!\n' in console_patched.file.getvalue()
    assert 'You may find your unit on the cloud here: link\n' in console_patched.file.getvalue()


def test_provision_unit_unsupported_protocol(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_system_info', side_effect=GrpcUnimplemented(),
    )

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_protocol_version', side_effect=GrpcUnimplemented(),
    )

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_system_info', side_effect=GrpcUnimplemented(),
    )

    get_protocol_version_v4 = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_protocol_version', side_effect=GrpcUnimplemented(),
    )

    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
        temp_cert.write(pkcs_12_cert)
        temp_cert.seek(0)
        uc = UserCredentials(temp_cert.name)

        cloud_api = CloudAPI(uc)
        with raises(GrpcUnimplemented):
            run_provision('unit_address', cloud_api)

    assert get_protocol_version_v4.call_count == 1
    assert 'Grpc protocol error:' in console_patched.file.getvalue()


def test_provision_unit_connection_error(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_system_info', side_effect=GrpcUnimplemented(),
    )

    get_protocol_version_v5 = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_protocol_version', side_effect=UnitError(),
    )
    mocker.patch('time.sleep')

    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
        temp_cert.write(pkcs_12_cert)
        temp_cert.seek(0)
        uc = UserCredentials(temp_cert.name)

        cloud_api = CloudAPI(uc)
        with raises(UnitError):
            run_provision('unit_address', cloud_api, reconnect_times=2)

    assert get_protocol_version_v5.call_count == 2
    assert 'Connection timeout' in console_patched.file.getvalue()


def test_provision_unit_v4_additional_cert(mocker):
    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_system_info', side_effect=GrpcUnimplemented(),
    )

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_protocol_version', side_effect=GrpcUnimplemented(),
    )

    get_system_info = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_system_info', return_value=('system_id', 'model'),
    )
    get_protocol_version = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_protocol_version', return_value=4,
    )
    get_all_node_ids = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_all_node_ids', return_value=['node1', 'node2'],
    )
    get_cert_types = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.get_cert_types',
        return_value=['online', 'offline', COMMAND_TO_DECRYPT],
    )
    clear = mocker.patch('aos_prov.commands.command_provision.UnitCommunicationV4.clear', return_value=None)
    set_cert_owner = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.set_cert_owner', return_value=None,
    )
    encrypt_disk = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.encrypt_disk', return_value=None,
    )
    uc = UnitCertificate()
    uc.cert_type = 'sm'
    uc.node_id = 'node1'
    create_keys = mocker.patch('aos_prov.commands.command_provision.UnitCommunicationV4.create_keys', return_value=uc)
    apply_certificate = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.apply_certificate', return_value=None,
    )
    finish_provisioning = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV4.finish_provisioning', return_value=None,
    )

    mocker.patch('aos_prov.communication.cloud.cloud_api.CloudAPI.check_unit_is_not_provisioned', return_value=None)
    mocker.patch(
        'aos_prov.communication.cloud.cloud_api.CloudAPI.register_device',
        return_value={
            'system_uid': 'system_id',
            'online_certificate': 'online_certificate_content',
            'offline_certificate': 'offline_certificate_content',
            'additional_certs': [
                {
                    'cert_type': 'sm',
                    'node_id': 'node1',
                    'cert': 'cert_content',
                },
            ],
        },
    )
    mocker.patch('aos_prov.communication.cloud.cloud_api.CloudAPI.get_unit_link_by_system_uid', return_value='link')

    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
        temp_cert.write(pkcs_12_cert)
        temp_cert.seek(0)
        uc = UserCredentials(temp_cert.name)

        cloud_api = CloudAPI(uc)
        run_provision('unit_address', cloud_api)

    assert get_system_info.call_count == 1
    assert get_protocol_version.call_count == 1
    assert get_all_node_ids.call_count == 1
    assert get_cert_types.call_count == 2
    assert set_cert_owner.call_count == 5
    assert clear.call_count == 5
    assert encrypt_disk.call_count == 1
    assert create_keys.call_count == 4
    assert apply_certificate.call_count == 4
    assert finish_provisioning.call_count == 1
    assert 'Starting provisioning...\n' in console_patched.file.getvalue()
    assert 'Finished successfully!\n' in console_patched.file.getvalue()
    assert 'You may find your unit on the cloud here: link\n' in console_patched.file.getvalue()


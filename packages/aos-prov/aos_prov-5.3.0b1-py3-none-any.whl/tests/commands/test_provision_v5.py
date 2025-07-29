#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import io
import tempfile

from aos_prov.commands.provision_v5 import run_provision_v5
from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.utils.config import Config
from aos_prov.utils.errors import UnitError
from aos_prov.utils.unit_certificate import UnitCertificate
from aos_prov.utils.user_credentials import UserCredentials
from pytest import raises
from rich.console import Console
from tests.fixtures import (
    generate_ca_key_and_cert,
    generate_test_key_certificate,
    key_cert_to_pkcs12,
    main_node_info,
    secondary_node_info,
)


def test_provision_unit_v5(mocker):
    config = Config()
    config.reset_secure_data()
    config.protocol_version = 5
    config.system_id = 'system_uid'
    config.set_model('vm-dev-dynamic;1.0')

    console_patched = mocker.patch(
        'aos_prov.utils.common.console',
        new=Console(file=io.StringIO(), width=120, soft_wrap=True),
    )
    get_all_node_ids = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_all_node_ids', return_value=['main', 'secondary'],
    )
    get_is_main_node = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.is_node_main', side_effect=[True, False],
    )

    get_node_info = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_node_info',
        side_effect=[main_node_info(), secondary_node_info()],
    )

    get_cert_types = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.get_cert_types',
        return_value=['online', 'offline', 'sm'],
    )

    start_provisioning = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.start_provisioning', return_value=None,
    )
    uc_online = UnitCertificate()
    uc_online.cert_type = 'online'
    uc_online.node_id = 'main'
    uc_offline = UnitCertificate()
    uc_offline.cert_type = 'offline'
    uc_offline.node_id = 'main'
    uc_sm = UnitCertificate()
    uc_sm.cert_type = 'sm'
    uc_sm.node_id = 'main'
    create_keys = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.create_keys',
        side_effect=[uc_online, uc_offline, uc_sm, uc_online, uc_offline, uc_sm],
    )
    apply_certificate = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.apply_certificate', return_value=None,
    )
    finish_provisioning = mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.finish_provisioning', return_value=None,
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
                    'node_id': 'main',
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
        run_provision_v5(config, 'unit_address', cloud_api)

    assert get_is_main_node.call_count == 2
    assert get_node_info.call_count == 2
    assert get_all_node_ids.call_count == 1
    assert get_cert_types.call_count == 2
    assert start_provisioning.call_count == 2
    assert create_keys.call_count == 6
    assert apply_certificate.call_count == 6
    assert finish_provisioning.call_count == 2
    assert 'Finished successfully!\n' in console_patched.file.getvalue()
    assert 'You may find your unit on the cloud here: link\n' in console_patched.file.getvalue()


def test_provision_unit_v5_check_node_info(mocker):
    config = Config()
    config.reset_secure_data()
    config.protocol_version = 5
    config.system_id = 'system_uid'
    config.set_model('vm-dev-dynamic;1.0')

    mocker.patch(
        'aos_prov.commands.command_provision.UnitCommunicationV5.is_node_main', side_effect=[True, False, True, False],
    )
    mocker.patch('aos_prov.communication.cloud.cloud_api.CloudAPI.check_unit_is_not_provisioned', return_value=None)

    ca_key, ca_cert = generate_ca_key_and_cert()
    key, cert = generate_test_key_certificate(ca_key)
    pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

    with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
        temp_cert.write(pkcs_12_cert)
        temp_cert.seek(0)
        uc = UserCredentials(temp_cert.name)

        cloud_api = CloudAPI(uc)

        mocker.patch(
            'aos_prov.commands.command_provision.UnitCommunicationV5.get_all_node_ids',
            return_value=[' main ', 'secondary'],
        )
        mocker.patch(
            'aos_prov.commands.command_provision.UnitCommunicationV5.get_node_info',
            side_effect=[main_node_info(), secondary_node_info()],
        )
        with raises(UnitError) as exc:
            run_provision_v5(config, 'unit_address', cloud_api)
        assert 'Node ID:  main  - containers trailing ASCII whitespaces' in str(exc.value)


        mocker.patch(
            'aos_prov.commands.command_provision.UnitCommunicationV5.get_all_node_ids',
            return_value=['main', 'secondary'],
        )
        node_with_error_node_type = main_node_info()
        node_with_error_node_type.type = ' type\t '
        mocker.patch(
            'aos_prov.commands.command_provision.UnitCommunicationV5.get_node_info',
            side_effect=[node_with_error_node_type, secondary_node_info()],
        )
        with raises(UnitError) as exc:
            run_provision_v5(config, 'unit_address', cloud_api)
        assert f'Node Type: {node_with_error_node_type.type} - containers trailing ASCII whitespaces' in str(exc.value)

        node_with_error_node_name = secondary_node_info()
        node_with_error_node_name.name = ' \nname '
        mocker.patch(
            'aos_prov.commands.command_provision.UnitCommunicationV5.get_node_info',
            side_effect=[main_node_info(), node_with_error_node_name],
        )
        with raises(UnitError) as exc:
            run_provision_v5(config, 'unit_address', cloud_api)
        assert f'Node Name: {node_with_error_node_name.name} - containers trailing ASCII whitespaces' in str(exc.value)

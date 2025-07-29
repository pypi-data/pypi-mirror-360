#
#  Copyright (c) 2018-2025 Renesas Inc.
#  Copyright (c) 2018-2025 EPAM Systems Inc.
#
# pylint: disable=R0912,R0914,R0915,R1702
"""Provision unit."""

import time

from aos_prov.commands.provision_v5 import run_provision_v5
from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.communication.unit.v4.unit_communication_v4 import UnitCommunicationV4
from aos_prov.communication.unit.v5.unit_communication_v5 import UnitCommunicationV5
from aos_prov.utils.common import generate_random_password, print_message
from aos_prov.utils.config import Config
from aos_prov.utils.errors import GrpcUnimplemented, UnitError

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version


COMMAND_TO_DECRYPT = 'diskencryption'


def run_provision(
    unit_address: str,
    cloud_api: CloudAPI,
    reconnect_times: int = 1,
    nodes_count: int = 2,
):  # noqa: WPS210,WPS213
    """
    Provision Unit. This function will try to provision starting from the newest to the oldest.

    Args:
         unit_address (str): Address of the Unit
         cloud_api (CloudAPI): URL to download
         reconnect_times (int): URL to download
         nodes_count (int): Number of nodes in the VM group.

    Raises:
         GrpcUnimplemented: If provision fails.
         UnitError: If provision fails.
    """
    config = Config()
    unit_communication = UnitCommunicationV5(unit_address)
    model_name = ''
    print_message('Starting provisioning...')
    for retry in range(reconnect_times):
        config.reset_secure_data()

        try:
            config.protocol_version = unit_communication.get_protocol_version()
            config.system_id, model_name = unit_communication.get_system_info()  # noqa: WPS414
            break
        except GrpcUnimplemented:
            print_message('[yellow]Connection error')
            print_message('Protocol version 5 is not supported by unit.')
            try:  # noqa: WPS505
                unit_communication = UnitCommunicationV4(unit_address)
                config.protocol_version = unit_communication.get_protocol_version()
                config.system_id, model_name = unit_communication.get_system_info()  # noqa: WPS414
                break
            except GrpcUnimplemented as gu_exc:
                print_message('Protocol version 4 is not supported by unit.')
                print_message(f'[red]Grpc protocol error: {gu_exc}.')
                raise gu_exc
        except UnitError as unit_exc:
            print_message('[yellow]Connection timeout')
            if retry + 1 < reconnect_times:
                time.sleep(1)
            else:
                raise unit_exc

    if config.system_id is None:
        raise UnitError('Cannot read system_id')

    config.set_model(model_name)
    cloud_api.check_unit_is_not_provisioned(config.system_id)

    if config.protocol_version >= 5:
        run_provision_v5(config, unit_address, cloud_api, nodes_count)
        return
    if config.protocol_version == 4:  # support of multi domains
        unit_communication = UnitCommunicationV4(unit_address)
        config.node_ids = unit_communication.get_all_node_ids()
        for node_id in config.node_ids:
            config.supported_cert_types = unit_communication.get_cert_types(node_id)
            need_disk_encryption = COMMAND_TO_DECRYPT in config.supported_cert_types

            password = generate_random_password()
            config.secure_data['nodes'].update({node_id: password})

            for clear_cert_type in config.supported_cert_types:
                unit_communication.clear(clear_cert_type, node_id)

            for set_cert_type in config.supported_cert_types:
                unit_communication.set_cert_owner(set_cert_type, password, node_id)

            if need_disk_encryption:
                unit_communication.encrypt_disk(password, node_id)
                config.supported_cert_types.remove(COMMAND_TO_DECRYPT)

            for create_cert_type in config.supported_cert_types:
                config.unit_certificates.append(unit_communication.create_keys(create_cert_type, password, node_id))
    else:
        raise UnitError(f'aos-prov does not support {config.protocol_version} protocol of the Unit')

    aos_prov_package_version = version('aos-prov')
    register_payload = {
        'hardware_id': config.system_id,
        'system_uid': config.system_id,
        'model_name': config.model_name,
        'model_version': config.model_version,
        'provisioning_software': f'aos-provisioning:{aos_prov_package_version}',
        'additional_csrs': [],
    }

    for csr_cert in config.unit_certificates:
        if csr_cert.cert_type == 'online':
            register_payload['online_public_csr'] = csr_cert.csr
            if csr_cert.node_id:
                register_payload['online_public_node_id'] = csr_cert.node_id
        elif csr_cert.cert_type == 'offline':
            register_payload['offline_public_csr'] = csr_cert.csr
            if csr_cert.node_id:
                register_payload['offline_public_node_id'] = csr_cert.node_id
        else:
            register_payload['additional_csrs'].append({
                'cert_type': csr_cert.cert_type,
                'csr': csr_cert.csr,
                'node_id': csr_cert.node_id,
            })

    response = cloud_api.register_device(register_payload)
    system_uid = response.get('system_uid')
    additional_certs = response.get('additional_certs', [])
    for cert in config.unit_certificates:
        if cert.cert_type == 'online':
            cert.certificate = response.get('online_certificate')
        elif cert.cert_type == 'offline':
            cert.certificate = response.get('offline_certificate')
        else:
            for additional_cert in additional_certs:
                if additional_cert['cert_type'] == cert.cert_type:
                    if additional_cert.get('node_id'):
                        if additional_cert.get('node_id') == cert.node_id:
                            cert.certificate = additional_cert['cert']
                            break
                    else:
                        cert.certificate = additional_cert['cert']
                        cert.node_id = additional_cert.get('node_id')
                        break

    for apply_cert in config.unit_certificates:
        unit_communication.apply_certificate(apply_cert)

    unit_communication.finish_provisioning()

    print_message('[green]Finished successfully!')
    link = cloud_api.get_unit_link_by_system_uid(system_uid)

    if link:
        print_message(f'You may find your unit on the cloud here: [green]{link}')

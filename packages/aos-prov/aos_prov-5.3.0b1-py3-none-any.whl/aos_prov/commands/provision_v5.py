#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
# pylint: disable=R0912,R0914,R0915,R1702
import json
import time

from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.communication.unit.v5.unit_communication_v5 import UnitCommunicationV5
from aos_prov.utils.common import generate_random_password, print_message
from aos_prov.utils.config import Config
from aos_prov.utils.errors import UnitError

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version


def run_provision_v5(config: Config, unit_address: str, cloud_api: CloudAPI, nodes_count: int = 2):
    unit_communication = UnitCommunicationV5(unit_address)

    while True:
        config.node_ids = unit_communication.get_all_node_ids()
        if len(config.node_ids) >= nodes_count:
            break
        print_message('[yellow]Wait while secondary node will be connected.')
        time.sleep(10)

    main_node = None
    other_nodes = []
    node_infos = []

    for node_id in config.node_ids:
        if unit_communication.is_node_main(node_id):
            main_node = node_id
        else:
            other_nodes.append(node_id)
        node_info = unit_communication.get_node_info(node_id)

        # check node's information on special symbols on start and finish of field
        if node_id.strip() != node_id:
            raise UnitError(f'Node ID: {node_id} - containers trailing ASCII whitespaces')
        if node_info.type.strip() != node_info.type:
            raise UnitError(f'Node Type: {node_info.type} - containers trailing ASCII whitespaces')
        if node_info.name.strip() != node_info.name:
            raise UnitError(f'Node Name: {node_info.name} - containers trailing ASCII whitespaces')

        attrs = {}
        for attr in node_info.attrs:
            attrs[attr.name] = attr.value
        node_info_dict = {
            'id': node_info.id,
            'type': node_info.type,
            'name': node_info.name,
            'cpus': [
                {
                    'modelName': cpu.model_name,
                    'totalNumCores': cpu.num_cores,
                    'totalNumThreads': cpu.num_threads,
                    'arch': cpu.arch,
                    'archFamily': cpu.arch_family,
                } for cpu in node_info.cpus],  # noqa: WPS319
            'maxDmips': node_info.max_dmips,
            'totalRam': node_info.total_ram,
            'osType': node_info.os_type,
            'attrs': attrs,
            'partitions': [
                {
                    'name': partition.name,
                    'types': list(partition.types),
                    'totalSize': partition.total_size,
                } for partition in node_info.partitions],  # noqa: WPS319
            'status': node_info.status,
            'errorInfo': {
                'aosCode': node_info.error.aos_code if node_info.error else 0,
                'exitCode': node_info.error.exit_code if node_info.error else 0,
                'message': node_info.error.message if node_info.error else '',
            },
        }
        node_infos.append(node_info_dict)

    password = generate_random_password()
    config.add_node_password(main_node, password)
    unit_communication.start_provisioning(main_node, password)
    config.supported_cert_types = unit_communication.get_cert_types(main_node)

    for cert_type in config.supported_cert_types:
        config.add_node_certificates(main_node, unit_communication.create_keys(cert_type, password, main_node))

    for node_id in other_nodes:
        password = generate_random_password()
        config.add_node_password(node_id, password)
        unit_communication.start_provisioning(node_id, password)
        config.supported_cert_types = unit_communication.get_cert_types(node_id)

        for cert_type in config.supported_cert_types:
            config.add_node_certificates(node_id, unit_communication.create_keys(cert_type, password, node_id))

    aos_prov_package_version = version('aos-prov')
    register_payload = {
        'hardware_id': config.system_id,
        'system_uid': config.system_id,
        'model_name': config.model_name,
        'model_version': config.model_version,
        'provisioning_software': f'aos-provisioning:{aos_prov_package_version}',
        'additional_csrs': [],
        'nodes': node_infos,
        'secure_data': json.dumps(config.secure_data, ensure_ascii=False),
    }

    for _, node_csrs in config.node_certificates.items():
        for csr_cert in node_csrs:
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

    for _, certs in config.node_certificates.items():
        for cert in certs:
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

    for _, apply_certs in config.node_certificates.items():
        for cert in apply_certs:
            unit_communication.apply_certificate(cert)

    for node_id in other_nodes:
        unit_communication.finish_provisioning(node_id, config.node_password[node_id])

    unit_communication.finish_provisioning(main_node, config.node_password[main_node])

    print_message('[green]Finished successfully!')
    link = cloud_api.get_unit_link_by_system_uid(system_uid)

    if link:
        print_message(f'You may find your unit on the cloud here: [green]{link}')

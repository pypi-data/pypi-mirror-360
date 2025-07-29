#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import uuid
from datetime import datetime, timedelta
from unittest import mock

from aos_prov.communication.unit.v5.generated.iamanager_pb2 import (
    CPUInfo,
    NodeAttribute,
    NodeInfo,
    PartitionInfo,
)
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    serialize_key_and_certificates,
)
from cryptography.x509.oid import NameOID


def generate_ca_key_and_cert():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    attributes = [
        x509.NameAttribute(NameOID.COUNTRY_NAME, u'UA'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u'Kyiv'),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u'Novus Ordo Seclorum'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'Epam'),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, u'support@aoscloud.io'),
        x509.NameAttribute(NameOID.COMMON_NAME, u'TEST Fusion Root CA'),
    ]

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name(attributes))
    builder = builder.issuer_name(x509.Name(attributes))
    builder = builder.not_valid_before(datetime.today() - timedelta(days=1))
    builder = builder.not_valid_after(datetime.today() + timedelta(days=100))
    builder = builder.serial_number(int(uuid.uuid4()))
    builder = builder.public_key(private_key.public_key())
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    )

    certificate = builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
        backend=default_backend()
    )

    return private_key, certificate


def generate_test_key_certificate(ca_key, domain=u"developer.test.local"):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, domain),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=10)
    ).sign(ca_key, hashes.SHA256())

    return private_key, cert


def key_cert_to_pem(private_key, cert, ca_cert):
    private_key_pem_bytes = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    return private_key_pem_bytes, b''.join([cert.public_bytes(Encoding.PEM), ca_cert.public_bytes(Encoding.PEM)])


def key_cert_to_pkcs12(private_key, cert, ca_cert):
    return serialize_key_and_certificates(
        name=b'TEST friendly name',
        key=private_key,
        cert=cert,
        cas=[ca_cert],
        encryption_algorithm=NoEncryption(),
    )


def mock_response(
        status=200,
        content=b'CONTENT',
        json_data=None,
        raise_for_status=None,
        content_length=True,
):
    """
    since we typically test a bunch of different
    requests calls for a service, we are going to do
    a lot of mock responses, so its usually a good idea
    to have a helper function that builds these things
    """
    mock_resp = mock.Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content
    mock_resp.headers = {
        'content-length': len(content) if content_length else None,
    }
    mock_resp.iter_content = mock.Mock(
        return_value=[content]
    )
    # add json data if provided
    if json_data:
        mock_resp.json.return_value = json_data
    return mock_resp


def _get_node_info():
    node_info = NodeInfo()

    node_info.id = 'b0b2fb353a394b93a22764e3b6a20a88'
    node_info.type = 'vm-dev-dynamic-1.0-main'
    node_info.name = 'main'
    node_info.status = 'unprovisioned'
    node_info.total_ram = 1008234496
    cpu_info = CPUInfo()
    cpu_info.model_name = 'Intel(R) Core(TM) i7-10610U CPU @ 1.80GHz'
    cpu_info.num_cores = 1
    cpu_info.num_threads = 1
    cpu_info.arch = '6'
    node_info.cpus.append(cpu_info)
    attr_main = NodeAttribute()
    attr_main.name = 'MainNode'
    attr_main.value = ''
    node_info.attrs.append(attr_main)
    partition_workdirs = PartitionInfo()
    partition_workdirs.name = 'workdirs'
    partition_workdirs.types.append('services')
    partition_workdirs.types.append('layers')
    partition_workdirs.types.append('generic')
    partition_workdirs.mount_point = '/var/aos/workdirs'
    node_info.partitions.append(partition_workdirs)

    return node_info

def main_node_info():
    node_info = _get_node_info()
    attr_main = NodeAttribute()
    attr_main.name = 'MainNode'
    attr_main.value = ''
    node_info.attrs.append(attr_main)

    return node_info

def secondary_node_info():
    node_info = _get_node_info()
    attr_main = NodeAttribute()
    attr_main.name = 'secondary'
    attr_main.value = ''
    node_info.attrs.append(attr_main)

    return node_info

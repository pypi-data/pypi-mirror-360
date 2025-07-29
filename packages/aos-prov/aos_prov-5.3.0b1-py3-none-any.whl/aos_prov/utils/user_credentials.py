#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import os
import tempfile
from pathlib import Path
from typing import Optional

from aos_prov.utils.errors import UserCredentialsError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives._serialization import (  # noqa: WPS436
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from cryptography.x509.oid import NameOID


def _extract_cloud_domain_from_cert(cert_bytes: bytes) -> str:
    """Get the Cloud domain name from user certificate.

    Args:
        cert_bytes: certificate content in bytes

    Returns:
        cloud domain from user certificate
    """
    _, certificate, _ = load_key_and_certificates(cert_bytes, None)
    return certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value


def _pkcs12_to_pem(pkcs12_bytes: bytes):
    private_key, certificate, additional_certificates = load_key_and_certificates(
        pkcs12_bytes,
        ''.encode('utf8'),
        default_backend(),
    )

    cert_bytes = bytearray(certificate.public_bytes(Encoding.PEM))
    for add_cert in additional_certificates:  # noqa: WPS519
        cert_bytes += add_cert.public_bytes(Encoding.PEM)
    key_bytes = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    cert_bytes = bytes(cert_bytes)
    return cert_bytes, key_bytes


def _create_temp_file(data_write: bytes):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)  # pylint: disable=R1732
    tmp_file.write(data_write)
    tmp_file.close()
    return tmp_file.name


class TempCredentials:
    def __init__(
        self,
        certificate: Optional[bytes],
        key: Optional[bytes],
        cert_file_name: Optional[str],
        key_file_name: Optional[str],
    ):
        self._key_file_name = key_file_name
        self._cert_file_name = cert_file_name

        self._key = None
        self._certificate = None

        if certificate and key:
            self._key = key
            self._certificate = certificate

    def __enter__(self):  # noqa: D105
        if not self._key_file_name:
            self._key_file_name = _create_temp_file(self._key)
        if not self._cert_file_name:
            self._cert_file_name = _create_temp_file(self._certificate)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: D105
        if self._key:
            os.unlink(self._key_file_name)
            self._key_file_name = None
        if self._certificate:
            os.unlink(self._cert_file_name)
            self._cert_file_name = None

    @property
    def key_file_name(self):
        return self._key_file_name

    @property
    def cert_file_name(self):
        return self._cert_file_name


class UserCredentials:

    def __init__(self, pkcs12: str):
        self._cloud_url = None
        if Path(pkcs12).exists():
            with open(pkcs12, 'rb') as pkcs12_file:
                pkcs12_file_content = pkcs12_file.read()
                cert_bytes, key_bytes = _pkcs12_to_pem(pkcs12_file_content)
                self._user_credentials = TempCredentials(
                    certificate=cert_bytes, key=key_bytes, cert_file_name=None, key_file_name=None,
                )
                self._cloud_url = _extract_cloud_domain_from_cert(pkcs12_file_content)
        else:
            raise UserCredentialsError(f'PKCS12 key: {pkcs12} not found.')

    @property
    def cloud_url(self):
        return self._cloud_url

    @property
    def user_credentials(self):
        return self._user_credentials

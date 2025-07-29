#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import tempfile
import unittest

from aos_prov.utils.errors import UserCredentialsError
from aos_prov.utils.user_credentials import TempCredentials, UserCredentials
from cryptography.hazmat.primitives._serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from tests.fixtures import (
    generate_ca_key_and_cert,
    generate_test_key_certificate,
    key_cert_to_pkcs12,
)


class TestTempCredentials(unittest.TestCase):
    def test_context_management(self):
        ca_key, ca_cert = generate_ca_key_and_cert()
        key, cert = generate_test_key_certificate(ca_key)

        cert_pem_bytes = cert.public_bytes(encoding=Encoding.PEM)

        private_key_pem_bytes = key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )
        with TempCredentials(cert_pem_bytes, private_key_pem_bytes, None, None) as temp_creds:
            self.assertIsNotNone(temp_creds.cert_file_name)
            self.assertIsNotNone(temp_creds.key_file_name)


class TestUserCredentials(unittest.TestCase):
    def test_create_with_pkcs12(self):
        ca_key, ca_cert = generate_ca_key_and_cert()
        key, cert = generate_test_key_certificate(ca_key)
        pkcs_12_cert = key_cert_to_pkcs12(key, cert, ca_cert)

        with tempfile.NamedTemporaryFile(delete=True) as temp_cert:
            temp_cert.write(pkcs_12_cert)
            temp_cert.seek(0)
            uc = UserCredentials(temp_cert.name)

        uc.cert_type = 'type1'
        self.assertEqual(uc.cert_type, 'type1')

        uc.certificate = 'some cert 1'
        self.assertEqual(uc.certificate, 'some cert 1')

        uc.csr = 'csr'
        self.assertEqual(uc.csr, 'csr')

        self.assertEqual(uc.cloud_url, 'developer.test.local')
        self.assertIsNotNone(uc.user_credentials)


    def test_file_not_found(self):
        with self.assertRaises(UserCredentialsError) as exc:
            UserCredentials('fake_pkcs12')

        self.assertEqual(str(exc.exception), 'PKCS12 key: fake_pkcs12 not found.')

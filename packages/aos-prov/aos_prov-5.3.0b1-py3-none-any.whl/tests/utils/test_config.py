#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import unittest

from aos_prov.utils.config import Config


class TestConfig(unittest.TestCase):
    def test_config_can_be_created(self):
        c = Config()
        self.assertIsInstance(c, Config)

    def test_setters_and_getters(self):
        c = Config()
        c.system_id = 'some system id'
        self.assertEqual(c.system_id, 'some system id')

        c.protocol_version = 5
        self.assertEqual(c.protocol_version, 5)

        c.node_ids = ['dom0', 'dom1']
        self.assertEqual(c.node_ids, ['dom0', 'dom1'])

        c.supported_cert_types = ['um', 'sm']
        self.assertEqual(c.supported_cert_types, ['um', 'sm'])

        c.set_model('model;1.0.0')
        self.assertEqual(c.model_name, 'model')
        self.assertEqual(c.model_version, '1.0.0')

        c.set_model('model')
        self.assertEqual(c.model_name, 'model')
        self.assertEqual(c.model_version, 'Unknown')

        c.unit_certificates = ['online', 'offline']
        self.assertEqual(c.unit_certificates, ['online', 'offline'])


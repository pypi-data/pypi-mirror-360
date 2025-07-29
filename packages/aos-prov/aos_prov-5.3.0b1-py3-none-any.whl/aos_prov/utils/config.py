#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#

from aos_prov.utils.unit_certificate import UnitCertificate


class Config:  # noqa: WPS214
    """Contains a provisioning procedure configuration."""

    def __init__(self):
        self._system_id = None
        self._model_name = None
        self._model_version = None
        self._user_claim = None
        self._supported_cert_types = None
        self._protocol_version = None
        self._node_ids = None
        self._unit_nodes = []
        self._node_password = {}
        self._node_certificates = {}
        self._unit_certificates = []
        self._secure_data = None

    def reset_secure_data(self):
        self._secure_data = {
            'version': '2.0.0',
            'nodes': {},
        }

    @property
    def secure_data(self) -> dict:
        return self._secure_data

    @property
    def system_id(self) -> str:
        return self._system_id

    @system_id.setter
    def system_id(self, sys_id):
        self._system_id = sys_id

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def supported_cert_types(self) -> [str]:
        return self._supported_cert_types

    @supported_cert_types.setter
    def supported_cert_types(self, cert_types):
        self._supported_cert_types = cert_types

    @property
    def protocol_version(self) -> int:
        return self._protocol_version

    @protocol_version.setter
    def protocol_version(self, protocol_version):
        self._protocol_version = protocol_version

    @property
    def node_ids(self) -> [str]:
        return self._node_ids

    @node_ids.setter
    def node_ids(self, node_ids):
        self._node_ids = node_ids

    @property
    def unit_nodes(self) -> [dict]:
        return self._unit_nodes

    @unit_nodes.setter
    def unit_nodes(self, unit_nodes):
        self._unit_nodes = unit_nodes

    @property
    def unit_certificates(self) -> [UnitCertificate]:
        return self._unit_certificates

    @unit_certificates.setter
    def unit_certificates(self, unit_certs):
        self._unit_certificates = unit_certs

    @property
    def node_password(self) -> dict:
        return self._node_password

    def add_node_password(self, node, password) -> None:
        self._node_password[node] = password
        self._secure_data['nodes'].update({node: password})

    @property
    def node_certificates(self) -> dict:
        return self._node_certificates

    def add_node_certificates(self, node, certificates) -> None:
        if self._node_certificates.get(node) is None:
            self._node_certificates[node] = []

        self._node_certificates[node].append(certificates)

    def set_model(self, model_string):
        """Parse model name and version received from the Unit.

        Args:
            model_string: model info returned by Unit.
        """
        model_chunks = model_string.strip().split(';')
        self._model_name = model_chunks[0].strip()
        if len(model_chunks) > 1:
            self._model_version = model_chunks[1].strip()
        else:
            self._model_version = 'Unknown'

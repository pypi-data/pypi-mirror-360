#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#

"""Unit certificate object."""


class UnitCertificate:
    """Unit certificate object."""

    def __init__(self):
        self._cert_type = None
        self._csr = None
        self._node_id = None
        self._certificate = None

    @property
    def cert_type(self) -> str:
        return self._cert_type

    @cert_type.setter
    def cert_type(self, cert_type):
        self._cert_type = cert_type

    @property
    def csr(self) -> str:
        return self._csr

    @csr.setter
    def csr(self, csr_value):
        self._csr = csr_value

    @property
    def node_id(self) -> str:
        return self._node_id

    @node_id.setter
    def node_id(self, node_id):
        self._node_id = node_id

    @property
    def certificate(self) -> str:
        return self._certificate

    @certificate.setter
    def certificate(self, cert):
        self._certificate = cert

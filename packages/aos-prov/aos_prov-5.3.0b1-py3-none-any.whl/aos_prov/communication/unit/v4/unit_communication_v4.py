#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
from contextlib import contextmanager

import grpc
from aos_prov.communication.unit.v4.generated import iamanager_pb2 as iam_manager
from aos_prov.communication.unit.v4.generated import (
    iamanager_pb2_grpc as iam_manager_grpc,
)
from aos_prov.utils.common import print_done, print_left, print_success
from aos_prov.utils.errors import GrpcUnimplemented, UnitError
from aos_prov.utils.unit_certificate import UnitCertificate
from google.protobuf import empty_pb2

UNIT_DEFAULT_PORT = 8089
_MAX_PORT = 65535


class UnitCommunicationV4:
    def __init__(self, address: str = 'localhost:8089'):
        self._need_set_users = False

        if not address:
            address = 'localhost:8089'

        parts = address.split(':')
        if len(parts) == 2:
            try:
                port = int(parts[1])
                if port not in range(1, _MAX_PORT):
                    raise UnitError('Unit port is invalid')
            except ValueError as exc:
                raise UnitError('Unit port is invalid') from exc
        else:
            address = address + ':' + str(UNIT_DEFAULT_PORT)
        self._unit_address = address

    @property
    def need_set_users(self):
        return self._need_set_users

    @need_set_users.setter
    def need_set_users(self, set_users):
        self._need_set_users = set_users

    @contextmanager
    def unit_certificate_stub(self, catch_inactive=False, wait_for_close=False):
        try:
            with grpc.insecure_channel(self._unit_address) as channel:
                stub = iam_manager_grpc.IAMCertificateServiceStub(channel)
                if wait_for_close:
                    def _stop_wait(state):  # noqa: WPS430
                        if state is grpc.ChannelConnectivity.SHUTDOWN:
                            channel.unsubscribe(_stop_wait)
                            return
                    channel.subscribe(_stop_wait, try_to_connect=False)
                yield stub

        except grpc.RpcError as exc:
            e_code = exc.code()
            e_detail = exc.details()
            if catch_inactive and not (e_code == grpc.StatusCode.UNAVAILABLE.value and e_detail == 'Socket closed'):
                return
            if wait_for_close and (e_code == grpc.StatusCode.UNKNOWN.value and e_detail == 'Stream removed'):
                return
            raise UnitError(f'FAILED! Error occurred: \n{e_code}: {e_detail}') from exc

    @contextmanager
    def unit_identify_stub(self):
        try:
            with grpc.insecure_channel(self._unit_address) as channel:
                stub = iam_manager_grpc.IAMPublicIdentityServiceStub(channel)
                yield stub

        except grpc.RpcError as exc:
            e_code = exc.code()
            e_detail = exc.details()
            if e_code.value == grpc.StatusCode.UNIMPLEMENTED.value:
                raise GrpcUnimplemented(f'Provisioning protocol 4 is not supported: \n{e_code}: {e_detail}') from exc
            raise UnitError(f'FAILED! Error occurred: \n{e_code}: {e_detail}') from exc

    @contextmanager
    def unit_provisioning_stub(self, catch_inactive=False, wait_for_close=False):
        try:
            with grpc.insecure_channel(self._unit_address) as channel:
                stub = iam_manager_grpc.IAMProvisioningServiceStub(channel)
                if wait_for_close:
                    def _stop_wait(state):  # noqa: WPS430
                        if state is grpc.ChannelConnectivity.SHUTDOWN:
                            channel.unsubscribe(_stop_wait)
                            return
                    channel.subscribe(_stop_wait, try_to_connect=False)
                yield stub

        except grpc.RpcError as exc:
            e_code = exc.code()
            e_detail = exc.details()
            if catch_inactive and not (e_code == grpc.StatusCode.UNAVAILABLE.value and e_detail == 'Socket closed'):
                return
            if wait_for_close and (e_code == grpc.StatusCode.UNKNOWN.value and e_detail == 'Stream removed'):
                return
            raise UnitError(f'FAILED! Error occurred: \n{e_code}: {e_detail}') from exc

    @contextmanager
    def unit_public_stub(self):
        try:
            with grpc.insecure_channel(self._unit_address) as channel:
                stub = iam_manager_grpc.IAMPublicServiceStub(channel)
                yield stub

        except grpc.RpcError as exc:
            e_code = exc.code()
            e_detail = exc.details()
            if e_code.value == grpc.StatusCode.UNIMPLEMENTED.value:
                raise GrpcUnimplemented(f'Provisioning protocol 4 is not supported: \n{e_code}: {e_detail}') from exc
            raise UnitError(f'FAILED! Error occurred: \n{e_code}: {e_detail}') from exc

    def get_protocol_version(self) -> int:
        with self.unit_public_stub() as stub:
            print_left('Communicating with unit using provisioning protocol version 4...')
            response = stub.GetAPIVersion(empty_pb2.Empty())
            print_done()
            return int(response.version)

    def get_system_info(self) -> (str, str):
        with self.unit_identify_stub() as stub:
            print_left('Getting System Info...')
            response = stub.GetSystemInfo(empty_pb2.Empty())
            print_done()
            print_left('System ID:')
            print_success(response.system_id)
            print_left('Model name:')
            print_success(response.board_model)
            return response.system_id, response.board_model

    def clear(self, certificate_type: str, node_id: str = '') -> None:
        with self.unit_provisioning_stub() as stub:
            print_left(f'Clearing certificate: {certificate_type} on Node ID: {node_id}...')
            response = stub.Clear(iam_manager.ClearRequest(type=certificate_type, node_id=node_id))
            print_done()
            return response

    def set_cert_owner(self, certificate_type: str, password: str, node_id: str = '') -> None:
        with self.unit_provisioning_stub() as stub:
            print_left(f'Setting owner for: {certificate_type} on Node ID: {node_id}...')
            response = stub.SetOwner(
                iam_manager.SetOwnerRequest(type=certificate_type, password=password, node_id=node_id),
            )
            print_done()
            return response

    def get_all_node_ids(self) -> [str]:
        with self.unit_provisioning_stub() as stub:
            print_left('Getting Node IDs...')
            response = stub.GetAllNodeIDs(empty_pb2.Empty())
            print_success(response.ids)
            return response.ids

    def get_cert_types(self, node_id: str = '') -> [str]:
        with self.unit_provisioning_stub() as stub:
            print_left(f'Getting certificate types to renew on node {node_id}...')
            response = stub.GetCertTypes(iam_manager.GetCertTypesRequest(node_id=node_id))
            print_success(response.types)
            return response.types

    def create_keys(self, cert_type: str, password: str, node_id: str = '') -> UnitCertificate:
        with self.unit_certificate_stub() as stub:
            print_left(f'Generating key type: {cert_type} on Node: {node_id}...')
            response = stub.CreateKey(iam_manager.CreateKeyRequest(type=cert_type, password=password, node_id=node_id))
            user_creds = UnitCertificate()
            user_creds.cert_type = response.type
            user_creds.node_id = response.node_id
            user_creds.csr = response.csr
            print_done()
            return user_creds

    def apply_certificate(self, unit_cert: UnitCertificate):
        with self.unit_certificate_stub() as stub:
            node_id = ''
            if unit_cert.node_id:
                node_id = str(unit_cert.node_id)
            print_left(f'Applying certificate type: {unit_cert.cert_type} Node ID: {node_id}...')
            stub.ApplyCert(iam_manager.ApplyCertRequest(
                type=unit_cert.cert_type,
                cert=unit_cert.certificate,
                node_id=node_id,
            ))
            print_done()

    def encrypt_disk(self, password: str, node_id: str = ''):
        print_left(f'Starting disk encryption on node {node_id}...')
        with self.unit_provisioning_stub(wait_for_close=False) as stub:
            stub.EncryptDisk(iam_manager.EncryptDiskRequest(password=password, node_id=node_id))
            print_done()

    def finish_provisioning(self):
        with self.unit_provisioning_stub(True) as stub:
            print_left('Finishing provisioning...')
            stub.FinishProvisioning(empty_pb2.Empty())
            print_done()

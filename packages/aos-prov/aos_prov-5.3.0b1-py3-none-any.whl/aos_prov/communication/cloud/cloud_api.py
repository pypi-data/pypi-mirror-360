#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import sys
import time
from http import HTTPStatus
from urllib.parse import urlencode

import requests
from aos_keys.check_version import DOCS_URL
from aos_prov.utils.common import (
    REQUEST_TIMEOUT,
    print_error,
    print_left,
    print_message,
    print_success,
)
from aos_prov.utils.errors import CloudAccessError, DeviceRegisterError
from aos_prov.utils.user_credentials import UserCredentials
from packaging.version import Version
from requests.exceptions import InvalidJSONError

if sys.version_info > (3, 9):
    from importlib import resources as pkg_resources  # noqa: WPS433, WPS440
else:
    import importlib_resources as pkg_resources  # noqa: WPS433, WPS440

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

DEFAULT_REGISTER_HOST = 'aoscloud.io'
DEFAULT_REGISTER_PORT = 10000


class CloudAPI:
    FILES_DIR = 'aos_prov'
    ROOT_CA_CERT_FILENAME = 'files/1rootCA.crt'
    REGISTER_URI_TPL = 'https://{}:{}/api/v11/units/provisioning/'
    SUPPORTED_SOFTWARE_URI_TPL = 'https://{}:{}/api/v11/units/provisioning/supported-software/'
    USER_ME_URI_TPL = 'https://{}:{}/api/v11/users/me/'
    UNIT_STATUS_URL = 'https://{}:{}/api/v11/units/?{}'
    FIND_UNIT_TPL = 'https://{}:{}/api/v11/units/?{}'
    LINK_TO_THE_UNIT_ON_CLOUD_TPL = 'https://{}/oem/units/{}'

    def __init__(
        self,
        user_credentials: UserCredentials,
        cloud_api_port: int = DEFAULT_REGISTER_PORT,
        retry_count: int = 1,
        retry_delay: float = 1.0,
    ):
        self._cloud_api_host = user_credentials.cloud_url
        self._cloud_api_port = cloud_api_port if cloud_api_port else DEFAULT_REGISTER_PORT
        self._user_credentials = user_credentials
        self._retry_count = retry_count
        self._retry_delay = retry_delay

    def check_cloud_access(self):
        def _check():  # noqa: WPS430
            print_left('Checking of access to the AosEdge...')
            url = self.USER_ME_URI_TPL.format(self._cloud_api_host, self._cloud_api_port)
            server_certificate = pkg_resources.files(self.FILES_DIR) / self.ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    resp = requests.get(
                        url,
                        verify=server_certificate_path,
                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name),
                        timeout=REQUEST_TIMEOUT,
                    )

                if resp.status_code != HTTPStatus.OK:
                    print_message('[red]Received not HTTP 200 response. ' + str(resp.text))
                    raise CloudAccessError('You do not have access to the cloud!')

                user_info = resp.json()
                if user_info['role'] != 'oem':
                    print_message(f'[red]invalid user role: {resp.text}')
                    raise CloudAccessError('You should use OEM account!')

            print_success('DONE')
            print_left('Operation will be executed on domain:')
            print_success(self._cloud_api_host)
            print_left('OEM:')
            print_success(user_info['oem']['title'])
            print_left('user:')
            print_success(user_info['username'])

        return self._do_with_retry(_check, CloudAccessError, 'Failed to connect to the cloud')

    def check_supported_software(self):
        def _check():  # noqa: WPS430
            installed_version = Version(version('aos-prov'))
            print_left(f'Checking of current software version: {installed_version} with the cloud...')
            url = self.SUPPORTED_SOFTWARE_URI_TPL.format(self._cloud_api_host, self._cloud_api_port)
            server_certificate = pkg_resources.files(self.FILES_DIR) / self.ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    resp = requests.get(
                        url,
                        verify=server_certificate_path,
                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name),
                        timeout=REQUEST_TIMEOUT,
                    )

                if resp.status_code != HTTPStatus.OK:
                    print_message('[red]Received not HTTP 200 response. ' + str(resp.text))
                    raise CloudAccessError('You do not have access to the cloud!')

                supported_software = resp.json()
                if not supported_software.get('software'):
                    print_message(f'[red]invalid response: {resp.text}')
                    raise CloudAccessError('There is no software key into response!')

                supported = False
                for software in supported_software['software']:
                    if software.get('name') == 'aos-provisioning' and software.get('min_version'):
                        if installed_version > Version(software['min_version']):
                            print_success('DONE')
                            supported = True
                        else:
                            print_message(
                                f'[red]Current software version {installed_version} is not supported by Cloud. '
                                f'Minimum required version is {software["min_version"]}',
                            )
                        break

                if not supported:
                    print_message(f'Perform updating/installing package according to AosEdge documentation: {DOCS_URL}')
                    raise CloudAccessError('Current software is not supported by Cloud!')

        return self._do_with_retry(_check, CloudAccessError, 'Failed to check supported software')

    def register_device(self, payload):
        def _register():  # noqa: WPS430
            print_left('Registering the unit ...')
            end_point = self.REGISTER_URI_TPL.format(self._cloud_api_host, self._cloud_api_port)

            server_certificate = pkg_resources.files(self.FILES_DIR) / self.ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    ret = requests.post(
                        end_point,
                        json=payload,
                        verify=server_certificate_path,
                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name),
                        timeout=REQUEST_TIMEOUT,
                    )

                    if ret.status_code == HTTPStatus.BAD_REQUEST:
                        print_error(f'Registration error: {ret.text}')
                    ret.raise_for_status()
                    print_success('DONE')

                    return ret.json()

        return self._do_with_retry(_register, DeviceRegisterError, 'Failed to register unit')

    def check_unit_is_not_provisioned(self, system_uid):
        def _check():  # noqa: WPS430
            print_left("Getting unit's status on the cloud ...")
            end_point = self.UNIT_STATUS_URL.format(
                self._cloud_api_host,
                self._cloud_api_port,
                urlencode({'system_uid': system_uid}),
            )
            server_certificate = pkg_resources.files(self.FILES_DIR) / self.ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    response = requests.get(
                        end_point,
                        verify=server_certificate_path,
                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name),
                        timeout=REQUEST_TIMEOUT,
                    )

            response_json = response.json()
            if response_json.get('items') is None or response_json.get('total') is None:
                raise DeviceRegisterError('Invalid answer from the cloud. Please update current library')

            if response_json.get('total') == 0:
                # There is no such unit on the cloud
                print_success('DONE')
                return

            status = response_json.get('items', [{}])[0].get('status')
            if status is None:
                print_success('DONE')
                return

            if status != 'new':
                raise DeviceRegisterError(f'Unit is in status "{status}". Please do deprovisioning first.')

        return self._do_with_retry(_check, DeviceRegisterError, 'Failed to check unit status')

    def get_unit_link_by_system_uid(self, system_uid):
        def _get_link():  # noqa: WPS430
            end_point = self.FIND_UNIT_TPL.format(
                self._cloud_api_host,
                self._cloud_api_port,
                urlencode({'system_uid': system_uid}),
            )
            server_certificate = pkg_resources.files(self.FILES_DIR) / self.ROOT_CA_CERT_FILENAME
            with pkg_resources.as_file(server_certificate) as server_certificate_path:
                with self._user_credentials.user_credentials as temp_creds:
                    response = requests.get(
                        end_point,
                        verify=server_certificate_path,
                        cert=(temp_creds.cert_file_name, temp_creds.key_file_name),
                        timeout=REQUEST_TIMEOUT,
                    )
            unit_id = response.json()['items'][0]['id']
            unit_domain = self._cloud_api_host
            if not unit_domain.startswith('oem.'):
                unit_domain = f'oem.{unit_domain}'
            return self.LINK_TO_THE_UNIT_ON_CLOUD_TPL.format(unit_domain, unit_id)

        try:
            return self._do_with_retry(_get_link, Exception, 'Failed to get unit link')
        except Exception:
            return None

    def _do_with_retry(self, operation, error_class, error_message):
        """Do Helper method to implement retry logic.

        Args:
            operation: Callable that performs the actual operation
            error_class: Exception class to raise on final failure
            error_message: Base error message to use in exception

        Returns:
            Result of the operation if successful

        Raises:
            error_class: If operation fails after all retries
        """
        last_exc = None
        for attempt in range(self._retry_count):
            try:
                return operation()
            except (
                requests.exceptions.RequestException,
                ValueError,
                OSError,
                InvalidJSONError,
                CloudAccessError,
                DeviceRegisterError,
            ) as exc:
                last_exc = exc
                if attempt < self._retry_count - 1:
                    # Only print retry message if we're going to retry
                    cur_attempt = attempt + 1
                    print_message(f'[yellow]Attempt {cur_attempt} failed, retrying in {self._retry_delay} seconds...')
                    time.sleep(self._retry_delay)
        raise error_class(f'{error_message}: {str(last_exc)}') from last_exc  # noqa: WPS237

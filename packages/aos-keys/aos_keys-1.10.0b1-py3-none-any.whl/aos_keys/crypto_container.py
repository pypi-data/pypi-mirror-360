#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import os
import ssl
import typing
from pathlib import Path

import requests
from aos_keys.common import AosKeysError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12  # noqa: WPS458
from cryptography.x509.oid import NameOID
from requests.adapters import HTTPAdapter

PRIVATE_KEY_ABSENT_ERROR = AosKeysError(
    'Key container does not have a private key',
    help_text='Container with key and certificates does not contain all items. Recreate key for the user.',
)

CERTIFICATE_ABSENT_ERROR = AosKeysError(
    'Key container does not have all needed certificates',
    help_text='Container with key and certificates does not contain all items. Recreate key for the user.',
)


class MTLSAdapter(HTTPAdapter):

    def __init__(self, *args, **kwargs):
        self._ssl_context = None
        crypto_instance = kwargs.pop('aos_crypto_container', None)
        if crypto_instance:
            self._ssl_context = crypto_instance.create_ssl_context()
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self._ssl_context:
            kwargs['ssl_context'] = self._ssl_context
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        if self._ssl_context:
            kwargs['ssl_context'] = self._ssl_context
        return super().proxy_manager_for(*args, **kwargs)


class AosCryptoContainer:

    def __init__(self, file_path: typing.Union[str, os.PathLike]):
        self._p12_filename: typing.Optional[str] = None
        self._pem_filename: typing.Optional[str] = None
        self._p12_bytes: typing.Optional[bytes] = None
        self._pem_bytes: typing.Optional[bytes] = None
        self._key_and_certificates: typing.Optional[pkcs12.PKCS12KeyAndCertificates] = None

        self.base_filename = file_path
        self.load()

    @property
    def base_filename(self):
        return str(Path(self._p12_filename).with_suffix(''))

    @base_filename.setter
    def base_filename(self, filename: typing.Union[str, os.PathLike]):
        # Remove ext from filename
        filename_no_ext = Path(filename).with_suffix('')
        self._p12_filename = str(filename)
        self._pem_filename = str(Path(filename_no_ext).with_suffix('.pem'))
        if self._pem_filename == self._p12_filename:
            self._pem_filename += '.pem'

    def load(self):
        if not os.path.exists(self._p12_filename):
            return

        # Load key and certificates
        with open(self._p12_filename, 'rb') as p12_handle:
            self._p12_bytes = p12_handle.read()
        self._key_and_certificates = pkcs12.load_pkcs12(self._p12_bytes, None)

        if not self._key_and_certificates.key:
            raise PRIVATE_KEY_ABSENT_ERROR

        if not (self._key_and_certificates.cert and self._key_and_certificates.additional_certs):
            raise CERTIFICATE_ABSENT_ERROR

        certificate = self._key_and_certificates.cert.certificate
        org_list = certificate.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        if org_list:
            self._cert_domain = org_list[0].value
        else:
            self._cert_domain = 'aoscloud.io'

        self._create_pem()
        self._check_pem()

    def create_ssl_context(self):
        ssl_ctx = ssl.create_default_context()
        if os.path.exists(self._pem_filename):
            ssl_ctx.load_cert_chain(self._pem_filename, password=None)
        return ssl_ctx

    def create_requests_session(self):
        https_session = requests.session()
        https_session.mount('https://', MTLSAdapter(aos_crypto_container=self))
        return https_session

    def _create_pem(self, force_recreate: bool = False):
        if os.path.exists(self._pem_filename) and not force_recreate:
            return

        with open(self._pem_filename, 'wb') as pem_handle:
            pem_handle.write(self._dump_to_pem())

    def _dump_to_pem(self) -> bytes:
        pem_list = [
            self._key_and_certificates.key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ),
            self._key_and_certificates.cert.certificate.public_bytes(serialization.Encoding.PEM),
        ]
        for cert in self._key_and_certificates.additional_certs:
            pem_list.append(
                cert.certificate.public_bytes(serialization.Encoding.PEM),
            )
        return b''.join(pem_list)

    def _check_pem(self):
        with open(self._pem_filename, 'rb') as pem_handle:
            self._pem_bytes = pem_handle.read()

        if self._pem_bytes != self._dump_to_pem():
            # Need to recreate PEM
            self._create_pem(force_recreate=True)

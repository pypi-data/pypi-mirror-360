#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
# pylint: disable=R1732,C0209,W0238
import os
import tempfile
from os.path import exists, isabs, join
from pathlib import Path

from aos_signer.service_config.service_configuration import ServiceConfiguration
from aos_signer.signer.errors import SignerConfigError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives._serialization import (  # noqa: WPS436
    Encoding,
    NoEncryption,
    PrivateFormat,
)
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
)
from cryptography.x509 import load_pem_x509_certificate


def _create_temp_file(data_write: bytes):
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.write(data_write)
    tmp_file.close()
    return tmp_file.name


class TempCredentials:
    def __init__(self, certificate: bytes, key: bytes):
        self._key = key
        self._certificate = certificate
        self._key_file_name = None
        self._cert_file_name = None

    def __enter__(self):  # noqa: D105
        self._key_file_name = _create_temp_file(self._key)
        self._cert_file_name = _create_temp_file(self._certificate)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: D105
        os.unlink(self._key_file_name)
        os.unlink(self._cert_file_name)

    @property
    def key_file_name(self):
        return self._key_file_name

    @property
    def cert_file_name(self):
        return self._cert_file_name


class UserCredentials:

    DEFAULT_USER_CREDENTIALS_FOLDER = str(Path.home() / '.aos' / 'security')

    def __init__(self, config: ServiceConfiguration, config_path: Path):
        self._config = config
        self._sign_key_path = None
        self._sign_cert_path = None
        self._upload_key_path = None
        self._upload_cert_path = None

        self._sign_p12_path = None
        self._upload_p12_path = None
        self._temp_files = []

        self._sign_key = None
        self._sign_cert = None

        self._pkcs_credentials = None

        self._config_path = config_path.parent

    @property
    def sign_key(self):
        return self._sign_key

    @property
    def sign_certificate(self):
        return self._sign_cert

    @property
    def upload_key_path(self):
        return self._upload_key_path

    @property
    def upload_cert_path(self):
        return self._upload_cert_path

    @property
    def pkcs_credentials(self):
        return self._pkcs_credentials

    @property
    def upload_p12_path(self):
        return self._upload_p12_path

    def find_sign_key_and_cert(self):
        if self._config.build.sign_pkcs12 is not None:
            self._sign_p12_path = self._find_user_cred_file(self._config.build.sign_pkcs12, 'publish->sign_pkcs12')

            with open(self._sign_p12_path, 'rb') as pkcs12_file:
                self._sign_cert, self._sign_key = UserCredentials.pkcs12_to_pem(pkcs12_file.read())  # noqa: WPS414

        else:
            self._sign_key_path = self._find_user_cred_file(self._config.build.sign_key, 'build->sign_key')
            self._sign_cert_path = self._find_user_cred_file(
                self._config.build.sign_certificate,
                'build->sign_certificate',
            )

            with open(self._sign_key_path, 'rb') as key_file:
                self._sign_key = key_file.read()

            with open(self._sign_cert_path, 'rb') as cert_file:
                self._sign_cert = cert_file.read()

    def find_upload_key_and_cert(self):
        if self._config.publish.tls_pkcs12 is not None:
            self._upload_p12_path = self._find_user_cred_file(self._config.publish.tls_pkcs12, 'publish->tls_pkcs12')

            with open(self._upload_p12_path, 'rb') as pkcs12_file:
                cert_bytes, key_bytes = UserCredentials.pkcs12_to_pem(pkcs12_file.read())
                self._pkcs_credentials = TempCredentials(cert_bytes, key_bytes)
        else:
            if self._config.publish.tls_key is not None:
                self._upload_key_path = self._find_user_cred_file(self._config.publish.tls_key, 'publish->tls_key')
            else:
                self._upload_key_path = self._find_user_cred_file(self._config.build.sign_key, 'build->sign_key')

            if self._config.publish.tls_certificate is not None:
                self._upload_cert_path = self._find_user_cred_file(
                    self._config.publish.tls_certificate,
                    'publish -> sign_certificate',
                )
            else:
                self._upload_cert_path = self._find_user_cred_file(
                    self._config.build.sign_certificate,
                    'build -> sign_key',
                )

    @classmethod
    def pkcs12_to_pem(cls, pkcs12_bytes: bytes):
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

    @classmethod
    def get_issuer(cls, certificate_data: bytes):
        certificate = load_pem_x509_certificate(certificate_data)
        return certificate.issuer.rfc4514_string()

    @classmethod
    def get_certificate_serial_number_hex(cls, certificate_data: bytes) -> str:
        certificate = load_pem_x509_certificate(certificate_data)

        serial = f'{certificate.serial_number:X}'
        if len(serial) % 2:
            return '0' + serial
        return serial

    def _find_user_cred_file(self, config_file_name: str, config_entry: str) -> str:
        """Search for file by absolute path, in `meta` folder or in default keys folder.

        Args:
            config_file_name (str): Filename or absolute file path.
            config_entry (str): Place in config to show error to user.

        Raises:
            SignerConfigError: If received absolute path and file not found or received relative path and file not
                               found nor in meta neither in aos folders.

        Returns:
            str: Path to existing file
        """
        path = config_file_name
        if isabs(path):
            if not exists(path):
                raise SignerConfigError(f'{config_entry} is set to absolute path but file not found.')
            return path

        for search_dir in (self._config_path, self.DEFAULT_USER_CREDENTIALS_FOLDER):
            path = join(search_dir, config_file_name)
            if exists(path):
                return path
        raise SignerConfigError(
            f'Configured {config_entry} file is set to {config_file_name},'
            f' but file not found neither in {self._config_path}'
            f' nor in {self.DEFAULT_USER_CREDENTIALS_FOLDER} directory.',
        )

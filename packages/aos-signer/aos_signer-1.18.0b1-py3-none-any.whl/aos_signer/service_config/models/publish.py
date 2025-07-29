#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
# pylint: disable=R0913

from jsonschema import ValidationError
from semver import VersionInfo as SemVerInfo

from .config_chapter import ConfigChapter


class Publish(ConfigChapter):

    def __init__(self, url, service_uid, tls_key, tls_certificate, tls_pkcs12, version):  # noqa: WPS211
        self._url = url
        self._service_uid = service_uid
        self._tls_key = tls_key
        self._tls_certificate = tls_certificate
        self._tls_pkcs12 = tls_pkcs12
        self._version = version

    @classmethod
    def from_yaml(cls, input_dict):
        publish = Publish(
            input_dict.get('url'),
            input_dict.get('service_uid'),
            input_dict.get('tls_key'),
            input_dict.get('tls_certificate'),
            input_dict.get('tls_pkcs12'),
            input_dict.get('version'),
        )
        ConfigChapter.validate(input_dict, validation_file='publish_schema.json')

        if not publish.tls_pkcs12 and (not publish.tls_key or not publish.tls_certificate):
            raise ValidationError('TLS certificate should be specified with tls_pkcs12 entry, '
                                  'or with tls_key and tls_certificate values.')  # noqa: WPS319, WPS318

        if not publish.version:
            raise ValidationError('publish.version is required field. Use SemVer approach!')

        if not SemVerInfo.is_valid(publish.version):
            raise ValidationError('publish.version is not valid. Use SemVer approach!')
        return publish

    @property
    def url(self):
        return self._url

    @property
    def service_uid(self):
        return self._service_uid

    @property
    def tls_key(self):
        return self._tls_key

    @property
    def tls_certificate(self):
        return self._tls_certificate

    @property
    def tls_pkcs12(self):
        return self._tls_pkcs12

    @property
    def version(self):
        return self._version

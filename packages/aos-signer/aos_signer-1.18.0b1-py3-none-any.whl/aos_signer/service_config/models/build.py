#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
# pylint: disable=R0913

from jsonschema import ValidationError

from .config_chapter import ConfigChapter


class Build(ConfigChapter):

    def __init__(  # noqa: WPS211
        self,
        os,
        arch,
        sign_key,
        sign_certificate,
        sign_pkcs12,
        remove_non_regular_files,
        symlinks,
        source_folder,
        package_folder,
    ):
        self._os = os
        self._arch = arch
        self._sign_key = sign_key
        self._sign_certificate = sign_certificate
        self._remove_non_regular_files = remove_non_regular_files
        self._symlinks = symlinks
        self._sign_pkcs12 = sign_pkcs12
        self._source_folder = source_folder
        self._package_folder = package_folder

    @classmethod
    def from_yaml(cls, input_dict):
        builder = Build(
            os=input_dict.get('os'),
            arch=input_dict.get('arch'),
            sign_key=input_dict.get('sign_key'),
            sign_certificate=input_dict.get('sign_certificate'),
            sign_pkcs12=input_dict.get('sign_pkcs12'),
            remove_non_regular_files=input_dict.get('remove_non_regular_files'),
            symlinks=input_dict.get('symlinks', 'copy'),
            source_folder=input_dict.get('source_folder', 'src'),
            package_folder=input_dict.get('package_folder', '.'),
        )
        ConfigChapter.validate(input_dict, validation_file='build_schema.json')

        if not builder.sign_pkcs12 and (not builder.sign_key or not builder.sign_certificate):
            raise ValidationError('Sign certificate should be specified with sign_pkcs12 entry, '
                                  'or with sign_key and sign_certificate values.')  # noqa: WPS319, WPS318

        return builder

    @property
    def os(self):
        return self._os

    @property
    def arch(self):
        return self._arch

    @property
    def sign_key(self):
        return self._sign_key

    @property
    def sign_certificate(self):
        return self._sign_certificate

    @property
    def sign_pkcs12(self):
        return self._sign_pkcs12

    @property
    def remove_non_regular_files(self) -> bool:
        return self._remove_non_regular_files

    @property
    def symlinks(self) -> bool:
        return self._symlinks

    @property
    def source_folder(self) -> str:
        return self._source_folder

    @property
    def package_folder(self) -> str:
        return self._package_folder

#
#  Copyright (c) 2018-2023 Renesas Inc.
#  Copyright (c) 2018-2023 EPAM Systems Inc.
#

import json
import os
import sys

import jsonschema
from aos_signer.signer.errors import SignerConfigError
from jsonschema.exceptions import ValidationError
from ruamel.yaml import YAML, parser, scanner
from semver import VersionInfo as SemVerInfo

from ..signer.common import print_message
from .models.build import Build
from .models.configuration import Configuration
from .models.publish import Publish
from .models.publisher import Publisher

if sys.version_info > (3, 9):
    from importlib import resources as pkg_resources  # noqa: WPS433, WPS440
else:
    import importlib_resources as pkg_resources  # noqa: WPS433, WPS440

CONFIG_NOT_FOUND_HELP = [  # noqa: WPS407
    "if you have configured service, run aos-signer tool from the parent directory of 'meta' dir",
    "If you are configuring service for the first time, run 'aos-signer init' first",
]


class ServiceConfiguration:

    DEFAULT_META_FOLDER = 'meta'
    DEFAULT_CONFIG_FILE_NAME = 'config.yaml'

    def __init__(self, file_path=None):
        self._config_path = file_path

        if file_path is None:
            file_path = os.path.join(self.DEFAULT_META_FOLDER, self.DEFAULT_CONFIG_FILE_NAME)

        if not os.path.isfile(file_path):
            raise SignerConfigError(f'Config file {file_path} not found. Exiting...', CONFIG_NOT_FOUND_HELP)

        yaml = YAML()
        print_message('[bright_black]Starting CONFIG VALIDATION process...')
        print_message('Validating config...           ', end='')

        with open(file_path, 'r', encoding='utf-8') as meta_file:
            try:
                schema = pkg_resources.files('aos_signer') / 'files/root_schema.json'
                loaded = yaml.load(meta_file)
                with pkg_resources.as_file(schema) as schema_path:
                    with open(schema_path, 'r', encoding='utf-8') as file_handler:
                        schema_content = json.loads(file_handler.read())
                        jsonschema.validate(loaded, schema=schema_content)
                self._publisher = Publisher.from_yaml(loaded.get('publisher'))
                self._publish = Publish.from_yaml(loaded.get('publish'))
                self._build = Build.from_yaml(loaded.get('build'))
                self._configuration = Configuration.from_yaml(loaded.get('configuration'))
                if not self._configuration.is_resource_limits:
                    if not SemVerInfo.parse(self._publish.version).prerelease:
                        publish_version = self._publish.version
                        raise ValidationError(
                            f'Cannot ignore resource limits due to version: {publish_version} is not pre-release',
                        )

                print_message('[green]VALID')
            except (parser.ParserError, scanner.ScannerError, jsonschema.exceptions.ValidationError) as exc:
                print_message('[red]ERROR')
                raise SignerConfigError(str(exc)) from exc

    @property
    def publisher(self):
        return self._publisher

    @property
    def publish(self):
        return self._publish

    @property
    def build(self):
        return self._build

    @property
    def configuration(self):
        return self._configuration

    @property
    def config_path(self):
        return self._config_path

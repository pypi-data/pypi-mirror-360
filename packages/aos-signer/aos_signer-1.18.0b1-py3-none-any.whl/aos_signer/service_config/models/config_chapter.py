#
#  Copyright (c) 2018-2023 Renesas Inc.
#  Copyright (c) 2018-2023 EPAM Systems Inc.
#
import json
import sys
from abc import ABC, abstractmethod

import jsonschema

if sys.version_info > (3, 9):
    from importlib import resources as pkg_resources  # noqa: WPS433, WPS440
else:
    import importlib_resources as pkg_resources  # noqa: WPS433, WPS440


class ConfigChapter(ABC):

    @classmethod
    @abstractmethod
    def from_yaml(cls, input_dict):
        """Create a ConfigChapter from yaml.

        Args:
            input_dict: Input YAML.
        """

    @classmethod
    def validate(cls, received_chapter, validation_schema=None, validation_file=None):
        if validation_schema is not None:
            jsonschema.validate(received_chapter, schema=validation_schema)

        if validation_file is not None:
            schema = pkg_resources.files('aos_signer') / ('files/' + validation_file)
            with pkg_resources.as_file(schema) as schema_path:
                with open(schema_path, 'r', encoding='utf-8') as file_handler:
                    schema_loaded = json.loads(file_handler.read())
                    jsonschema.validate(received_chapter, schema=schema_loaded)

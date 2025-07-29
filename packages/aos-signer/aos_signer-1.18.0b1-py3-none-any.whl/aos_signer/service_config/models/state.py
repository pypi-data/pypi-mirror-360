import os

from .config_chapter import ConfigChapter
from ...signer.errors import SignerConfigError


class State(ConfigChapter):

    def __init__(self, required, filename):
        self._state_required = required
        self._state_filename = filename

    @staticmethod
    def from_yaml(input_dict):
        if input_dict is None:
            return

        state_chapter = State(input_dict.get('required'), input_dict.get('filename'))
        if state_chapter.validate(input_dict, validation_file='state_schema.json'):

            if state_chapter._state_required:
                if not state_chapter._state_filename:
                    raise SignerConfigError('configuration.state.required is set to True,'
                                            'but no configuration.state.filename is not set')

                if not os.path.exists(os.path.join('.src', state_chapter._state_filename)):
                    raise SignerConfigError('configuration.state.filename is set,'
                                            'but file not found')

            return state_chapter

    def state_filename(self):
        return self._state_filename

    def state_required(self):
        return self._state_required

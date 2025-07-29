#
#  Copyright (c) 2018-2019 Renesas Inc.
#  Copyright (c) 2018-2019 EPAM Systems Inc.
#

from typing import Iterable

from aos_signer.signer.common import print_error


def _print_help_with_spaces(text):
    print_error(f'  {text}')


class SignerError(Exception):

    def __init__(self, message, help_text=None):
        """Exception with help text with recommended user actions.

        Args:
            message: Exception message.
            help_text: Help text to print after error.
        """
        super().__init__(message)
        self.help_text = help_text

    def print_message(self):
        """Print exception with help text if existed."""
        print_error(f'ERROR: {self}')

        if not self.help_text:
            return

        if isinstance(self.help_text, str) or not isinstance(self.help_text, Iterable):
            _print_help_with_spaces(self.help_text)
            return

        for row in self.help_text:
            _print_help_with_spaces(row)


class SignerConfigError(SignerError):
    def __init__(self, message, help_text=None):
        super().__init__(message)
        self.help_text = help_text


class NoAccessError(SignerError):
    def __init__(self, message, help_text=None):
        super().__init__(message)
        self.help_text = help_text

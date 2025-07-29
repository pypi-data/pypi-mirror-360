#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#
"""Common defaults and settings."""

import logging
import sys
from contextlib import contextmanager

from rich.console import Console

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
console = Console()
error_console = Console(stderr=True, style='red')

if sys.version_info > (3, 9):
    from importlib import resources as pkg_resources  # noqa: WPS433, WPS440
else:
    import importlib_resources as pkg_resources  # noqa: WPS433, WPS440


FILES_DIR = 'aos_signer'
ROOT_CA_CERT_FILENAME = 'files/1rootCA.crt'
ALLOW_PRINT = True
REQUEST_TIMEOUT = 30


def print_message(formatted_text, end='\n'):
    if ALLOW_PRINT:
        console.print(formatted_text, end=end)


def print_error(message):
    if ALLOW_PRINT:
        error_console.print(message)


@contextmanager
def ca_certificate():
    """
    Aos root certificate to verify server certificate.

    Yields:
        server_certificate_path: Path to certificate file.
    """
    server_certificate = pkg_resources.files(FILES_DIR) / ROOT_CA_CERT_FILENAME
    with pkg_resources.as_file(server_certificate) as server_certificate_path:
        yield server_certificate_path

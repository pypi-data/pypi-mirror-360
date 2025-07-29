#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
import sys
from pathlib import Path

from aos_signer.service_config.service_configuration import ServiceConfiguration
from aos_signer.signer.bootstrapper import run_bootstrap
from aos_signer.signer.common import print_message
from aos_signer.signer.errors import SignerError
from aos_signer.signer.signer import Signer
from aos_signer.signer.uploader import run_upload


def bootstrap_service_folder(working_directory=None):
    """Create service folder structure and config.yaml.

    Args:
        working_directory: Working directory for generation initial files
    """
    print_message('[green]Starting INIT process...')
    run_bootstrap(working_directory)


def validate_service_config(config_path: Path):
    """Validate config.yaml.

    Args:
         config_path: Path to config file.
    """
    print_message('[bright_black]Starting CONFIG VALIDATION process...')
    ServiceConfiguration(Path(config_path))
    print_message('[green]Config is valid')


def upload_service(config_path: Path):
    """Upload service.

    Args:
        config_path: Path to config file.

    Raises:
        SignerError: If upload failed.
    """
    print_message('[bright_black]Starting SERVICE UPLOAD process...')
    try:
        run_upload(Path(config_path))
    except OSError as exc:
        raise SignerError(str(sys.exc_info()[1])) from exc


def sign_service(config_path: Path):
    """Sign service.

    Args:
        config_path: Path to config file.

    Raises:
        SignerError: If sign process failed.
    """
    print_message('[bright_black]Starting SERVICE SIGNING process...')
    config = ServiceConfiguration(config_path)
    try:
        signer = Signer(
            config=config,
            config_path=Path(config_path),
        )
        signer.process()
    except OSError as exc:
        raise SignerError(str(sys.exc_info()[1])) from exc

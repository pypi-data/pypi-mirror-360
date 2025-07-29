#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#
# pylint: disable=W1401

import os
import sys

from aos_signer.signer.common import FILES_DIR, print_message
from aos_signer.signer.errors import NoAccessError

if sys.version_info > (3, 9):
    from importlib import resources as pkg_resources  # noqa: WPS433, WPS440
else:
    import importlib_resources as pkg_resources  # noqa: WPS433, WPS440

_meta_folder_name = 'meta'
_src_folder_name = 'src'
_config_file_name = 'config.yaml'


def run_bootstrap(working_directory=None):
    meta_folder_name = os.path.join(working_directory, _meta_folder_name) if working_directory else _meta_folder_name
    src_folder_name = os.path.join(working_directory, _src_folder_name) if working_directory else _src_folder_name
    _create_folder_if_not_exist(meta_folder_name)
    _create_folder_if_not_exist(src_folder_name)
    _init_conf_file(meta_folder_name)
    print_message('[green]DONE[/green]')
    _print_epilog()


def _create_folder_if_not_exist(folder_name):
    try:
        if os.path.isdir(folder_name):
            print_message(f'Directory [cyan]\[{folder_name}][/cyan] exists... [yellow]Skipping[/yellow]')  # noqa: W605
        else:
            os.mkdir(folder_name)
            print_message(f'Directory [cyan]\[{folder_name}][/cyan] created.')  # noqa: W605
    except PermissionError as exc:
        raise NoAccessError from exc


def _init_conf_file(meta_folder_name):
    conf_file_path = os.path.join(meta_folder_name, _config_file_name)
    if os.path.isfile(conf_file_path):
        print_message(f'Configuration file [cyan]{_config_file_name}[/cyan] exists... [yellow]Skipping[/yellow]')
    else:
        with open(conf_file_path, 'x', encoding='utf-8') as cfp:
            config = pkg_resources.files(FILES_DIR) / f'files/{_config_file_name}'
            with pkg_resources.as_file(config) as config_path:
                cfp.write(config_path.read_text(encoding='utf-8'))
        print_message(f'Config file  [cyan]{meta_folder_name}/{_config_file_name}[/cyan] created')


def _print_epilog():
    print_message('---------------------------')
    print_message('[dim]Further steps:')
    print_message('Copy your service files with desired folders to [cyan]\[src][/cyan] folder.')  # noqa: W605
    print_message('Update [cyan]meta/config.yaml[/cyan] with desired values.')
    print_message('Run [bright blue]aos-signer sign[/] to sign service and'
                  " '[bright blue]aos-signer upload[/]' to upload signed service to the cloud.")  # noqa: WPS318,WPS319

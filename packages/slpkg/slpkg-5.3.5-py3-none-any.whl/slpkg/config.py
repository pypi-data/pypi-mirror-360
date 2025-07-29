#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os


try:
    from dialog import Dialog

    DIALOG_AVAILABLE = True
except ModuleNotFoundError:
    DIALOG_AVAILABLE = False

import platform
from pathlib import Path
from typing import Any, Union

import tomlkit
from tomlkit import exceptions

from slpkg.toml_errors import TomlErrors


class Config:  # pylint: disable=[R0902, R0903]
    """Loads and holds configurations."""

    def __init__(self) -> None:  # pylint: disable=[R0915]
        # Initialize variables for error handling and architecture detection
        # (toml_errors does not seem to be used in Config, so you might consider
        # moving or removing it if not necessary here)
        self.toml_errors = TomlErrors()  # Assuming slpkg.toml_errors exists
        self.cpu_arch: str = platform.machine()
        self.os_arch: str = platform.architecture()[0]

        # Program name.
        self.prog_name: str = 'slpkg'

        # Slpkg utility paths.
        self.tmp_path: Path = Path('/tmp')
        self.tmp_slpkg: Path = Path(self.tmp_path, self.prog_name)
        self.build_path: Path = Path(self.tmp_path, self.prog_name, 'build')
        self.etc_path: Path = Path('/etc', self.prog_name)
        self.lib_path: Path = Path('/var/lib', self.prog_name)
        self.log_path: Path = Path('/var/log/', self.prog_name)
        self.log_packages: Path = Path('/var', 'log', 'packages')

        # Slpkg log files.
        self.deps_log_file: Path = Path(self.log_path, 'deps.log')
        self.slpkg_log_file: Path = Path(self.log_path, 'slpkg.log')
        self.upgrade_log_file: Path = Path(self.log_path, 'upgrade.log')
        self.error_log_file: Path = Path(self.log_path, 'error.log')

        # Answer yes always is False except user changes via argparse module.
        self.answer_yes: bool = False

        # Default configurations for slpkg.toml.
        # These are "fallback" values if not found in the TOML file or not set by argparse.
        self.file_list_suffix: str = '.pkgs'
        self.package_type = [".tgz", ".txz"]
        self.installpkg: str = 'upgradepkg --install-new'
        self.reinstall: str = 'upgradepkg --reinstall'
        self.removepkg: str = 'removepkg'
        self.kernel_version: bool = True
        self.bootloader_command: str = ''
        self.colors: bool = True
        self.makeflags: str = '-j4'
        self.gpg_verification: bool = False
        self.checksum_md5: bool = True
        self.dialog: bool = False
        self.terminal_selector: bool = True
        self.view_missing_deps: bool = False
        self.package_method: bool = False
        self.downgrade_packages: bool = False
        self.delete_sources: bool = False
        self.downloader: str = 'wget'
        self.wget_options: str = '-c -q --progress=bar:force:noscroll --show-progress'
        self.curl_options: str = ''
        self.aria2_options: str = '-c'
        self.lftp_get_options: str = '-c get -e'
        self.lftp_mirror_options: str = '-c mirror --parallel=100 --only-newer --delete'
        self.git_clone: str = 'git clone --depth 1'
        self.download_only_path: Union[Path, str] = Path(self.tmp_slpkg, '')
        self.ask_question: bool = True
        self.parallel_downloads: bool = False
        self.maximum_parallel: int = 5
        self.progress_bar: bool = False
        self.progress_spinner: str = 'spinner'
        self.spinner_color: str = 'green'
        self.process_log: bool = True
        self.urllib_retries: bool = False
        self.urllib_redirect: bool = False
        self.urllib_timeout: float = 3.0
        self.proxy_address: str = ''
        self.proxy_username: str = ''
        self.proxy_password: str = ''

        # Load configurations from the TOML file (before potential argparse override)
        self._load_config()
        # Apply static checks/adjustments based on loaded settings
        self._set_colors()  # Will apply colors based on self.colors (from TOML or default)
        self._create_paths()

    def _load_config(self) -> None:  # pylint: disable=[R0915]
        # This map corresponds TOML keys (uppercase)
        # to the corresponding class attributes (lowercase)
        toml_to_attr_map = {
            'FILE_LIST_SUFFIX': 'file_list_suffix',
            'PACKAGE_TYPE': 'package_type',
            'INSTALLPKG': 'installpkg',
            'REINSTALL': 'reinstall',
            'REMOVEPKG': 'removepkg',
            'KERNEL_VERSION': 'kernel_version',
            'BOOTLOADER_COMMAND': 'bootloader_command',
            'COLORS': 'colors',
            'MAKEFLAGS': 'makeflags',
            'GPG_VERIFICATION': 'gpg_verification',
            'CHECKSUM_MD5': 'checksum_md5',
            'DIALOG': 'dialog',
            'TERMINAL_SELECTOR': 'terminal_selector',
            'VIEW_MISSING_DEPS': 'view_missing_deps',
            'PACKAGE_METHOD': 'package_method',
            'DOWNGRADE_PACKAGES': 'downgrade_packages',
            'DELETE_SOURCES': 'delete_sources',
            'DOWNLOADER': 'downloader',
            'WGET_OPTIONS': 'wget_options',
            'CURL_OPTIONS': 'curl_options',
            'ARIA2_OPTIONS': 'aria2_options',
            'LFTP_GET_OPTIONS': 'lftp_get_options',
            'LFTP_MIRROR_OPTIONS': 'lftp_mirror_options',
            'GIT_CLONE': 'git_clone',
            'DOWNLOAD_ONLY_PATH': 'download_only_path',
            'ASK_QUESTION': 'ask_question',
            'PARALLEL_DOWNLOADS': 'parallel_downloads',
            'MAXIMUM_PARALLEL': 'maximum_parallel',
            'PROGRESS_BAR': 'progress_bar',
            'PROGRESS_SPINNER': 'progress_spinner',
            'SPINNER_COLOR': 'spinner_color',
            'PROCESS_LOG': 'process_log',
            'URLLIB_RETRIES': 'urllib_retries',
            'URLLIB_REDIRECT': 'urllib_redirect',
            'URLLIB_TIMEOUT': 'urllib_timeout',
            'PROXY_ADDRESS': 'proxy_address',
            'PROXY_USERNAME': 'proxy_username',
            'PROXY_PASSWORD': 'proxy_password',
        }

        # Type map for validation
        config_types = {
            'FILE_LIST_SUFFIX': (str,),
            'PACKAGE_TYPE': (list,),
            'INSTALLPKG': (str,),
            'REINSTALL': (str,),
            'REMOVEPKG': (str,),
            'KERNEL_VERSION': (bool,),
            'BOOTLOADER_COMMAND': (str,),
            'COLORS': (bool,),
            'MAKEFLAGS': (str,),
            'GPG_VERIFICATION': (bool,),
            'CHECKSUM_MD5': (bool,),
            'DIALOG': (bool,),
            'TERMINAL_SELECTOR': (bool,),
            'VIEW_MISSING_DEPS': (bool,),
            'PACKAGE_METHOD': (bool,),
            'DOWNGRADE_PACKAGES': (bool,),
            'DELETE_SOURCES': (bool,),
            'DOWNLOADER': (str,),
            'WGET_OPTIONS': (str,),
            'CURL_OPTIONS': (str,),
            'ARIA2_OPTIONS': (str,),
            'LFTP_GET_OPTIONS': (str,),
            'LFTP_MIRROR_OPTIONS': (str,),
            'GIT_CLONE': (str,),
            'DOWNLOAD_ONLY_PATH': (str, Path),
            'ASK_QUESTION': (bool,),
            'PARALLEL_DOWNLOADS': (bool,),
            'MAXIMUM_PARALLEL': (int,),
            'PROGRESS_BAR': (bool,),
            'PROGRESS_SPINNER': (str,),
            'SPINNER_COLOR': (str,),
            'PROCESS_LOG': (bool,),
            'URLLIB_RETRIES': (bool,),
            'URLLIB_REDIRECT': (bool,),
            'URLLIB_TIMEOUT': (int, float),
            'PROXY_ADDRESS': (str,),
            'PROXY_USERNAME': (str,),
            'PROXY_PASSWORD': (str,),
        }

        config_path_file: Path = Path(self.etc_path, f'{self.prog_name}.toml')
        conf: dict[str, dict[str, Any]] = {}
        toml_setting_name: str = ''
        try:
            if config_path_file.exists():
                with open(config_path_file, 'r', encoding='utf-8') as file:
                    conf = tomlkit.parse(file.read())

            if conf and 'CONFIGS' in conf:
                self.config = conf['CONFIGS']  # Store settings from TOML

                error_type = False
                for toml_key, attr_name in toml_to_attr_map.items():
                    if toml_key in self.config:  # Check if key exists in TOML
                        value = self.config[toml_key]
                        expected_type = config_types[toml_key]

                        # Special handling for DOWNLOAD_ONLY_PATH
                        if toml_key == 'DOWNLOAD_ONLY_PATH' and isinstance(value, str):
                            value = Path(value)

                        # Type checking (if it's a Union (e.g., (str, Path)), check all types)
                        if isinstance(expected_type, tuple):  # If it's a Union (e.g., (str, Path))
                            if not any(isinstance(value, t) for t in expected_type):
                                error_type = True
                                toml_setting_name = toml_key
                                break
                            if not isinstance(value, expected_type):
                                toml_setting_name = toml_key
                                error_type = True
                                break

                        # If no type error, assign the value to the class attribute
                        setattr(self, attr_name, value)
                    else:
                        print(f"{self.prog_name}: Error: Setting '{toml_key}' in configurations does not exist.\n"
                              f"If you have upgraded '{self.prog_name}' maybe you need to run:\n"
                              f"\n{'':>4}$ slpkg_new-configs\n"
                              "\nThe default configurations are used.\n")
                        break

                if error_type:  # If a type error was found, print a message
                    print(f"{self.prog_name}: Error: Setting '{toml_setting_name}' in configurations contain wrong type.\n"
                          f"Default configurations are used.\n")

        except (KeyError, exceptions.TOMLKitError) as e:
            self.toml_errors.raise_toml_error_message(str(e), config_path_file)
            print('The default configurations are used.\n')

        # If the dialog module is not available, disable dialog
        if not DIALOG_AVAILABLE:
            self.dialog = False

    def update_from_args(self, args: Any) -> None:
        """
        Updates configuration settings based on parsed argparse arguments.
        This method should be called from main.py after arguments are parsed.
        """
        if hasattr(args, 'option_color') and args.option_color:
            self.colors = args.option_color in ['on', 'ON']
            self._set_colors()  # Reapply color settings if changed

        if hasattr(args, 'option_dialog') and args.option_dialog:
            self.dialog = args.option_dialog  # Assume argparse passes a boolean value directly
            if not DIALOG_AVAILABLE:  # Ensure it respects DIALOG_AVAILABLE
                self.dialog = False

        if hasattr(args, 'option_parallel') and args.option_parallel:
            self.parallel_downloads = args.option_parallel  # Assume argparse passes a boolean value directly

        if hasattr(args, 'option_progress_bar') and args.option_progress_bar:
            self.progress_bar = args.option_progress_bar  # Assume argparse passes a boolean value directly

        if hasattr(args, 'option_yes') and args.option_yes:
            self.answer_yes = args.option_yes  # Assume argparse passes a boolean value directly

    def _set_colors(self) -> None:
        # Reset color codes
        self.back_white: str = ''
        self.bold: str = ''
        self.black: str = ''
        self.red: str = ''
        self.green: str = ''
        self.yellow: str = ''
        self.cyan: str = ''
        self.grey: str = ''
        self.endc: str = ''

        # Apply colors only if self.colors is True
        if getattr(self, 'colors', True):  # Use getattr for safety, though it should exist
            self.back_white = '\x1b[47m'
            self.bold = '\x1b[1m'
            self.black = '\x1b[30m'
            self.red = '\x1b[91m'
            self.green = '\x1b[32m'
            self.yellow = '\x1b[93m'
            self.cyan = '\x1b[96m'
            self.grey = '\x1b[38;5;247m'
            self.endc = '\x1b[0m'

    def _create_paths(self) -> None:
        if not os.geteuid() == 0:
            home_path: str = os.path.expanduser('~')
            home_log: Path = Path(home_path, '.local', 'share', self.prog_name)
            home_log.mkdir(parents=True, exist_ok=True)
            self.error_log_file = Path(home_log, 'error.log')

        paths = [
            self.lib_path,
            self.etc_path,
            self.build_path,
            self.tmp_slpkg,
            self.log_path,
            getattr(self, 'download_only_path', Path(self.tmp_slpkg, '')),
        ]
        for path in paths:
            if not path.is_dir():
                path.mkdir(parents=True, exist_ok=True)

    def is_64bit(self) -> bool:
        """Determines the CPU and the OS architecture.

        Returns:
            TYPE: Bool.
        """
        if self.cpu_arch in {'x86_64', 'amd64', 'aarch64', 'arm64', 'ia64'} and self.os_arch == '64bit':
            return True
        return False


# Creating a unique instance of the Config class.
# This instance will be loaded by any module that imports 'config'.
# It contains default settings and settings from TOML (if config.toml exists in /etc/slpkg).
config_load = Config()

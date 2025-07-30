#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any

from slpkg.binaries.required import Required
from slpkg.checksum import Md5sum
from slpkg.choose_dependencies import ChooseDependencies
from slpkg.choose_packages import Choose
from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.downloader import Downloader
from slpkg.gpg_verify import GPGVerify
from slpkg.multi_process import MultiProcess
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess
from slpkg.views.views import View


class Packages:  # pylint: disable=[R0902]
    """Download and install packages with dependencies."""

    def __init__(self, repository: str, data: dict[str, dict[str, str]], packages: list[str], options: dict[str, bool], mode: str) -> None:  # pylint: disable=[R0913, R0917]
        self.repository = repository
        self.data = data
        self.packages = packages
        self.options = options
        self.mode = mode

        self.tmp_slpkg = config_load.tmp_slpkg
        self.gpg_verification = config_load.gpg_verification
        self.slpkg_log_file = config_load.slpkg_log_file
        self.installpkg = config_load.installpkg
        self.reinstall = config_load.reinstall
        self.delete_sources = config_load.delete_sources
        self.deps_log_file = config_load.deps_log_file
        self.dialog = config_load.dialog
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.endc = config_load.endc

        self.utils = Utilities()
        self.dialogbox = DialogBox()
        self.multi_proc = MultiProcess(options)
        self.view = View(options, repository, data)
        self.view_process = ViewProcess()
        self.check_md5 = Md5sum(options)
        self.download = Downloader(options)
        self.upgrade = Upgrade(repository, data)
        self.gpg = GPGVerify()
        self.choose_packages = Choose(options, repository)
        self.choose_package_dependencies = ChooseDependencies(repository, data, options, mode)

        self.dependencies: list[str] = []
        self.install_order: list[str] = []
        self.binary_packages: list[str] = []
        self.skipped_packages: list[str] = []
        self.progress_message: str = 'Installing'

        self.option_for_reinstall: bool = options.get('option_reinstall', False)

        self.option_for_skip_installed: bool = options.get('option_skip_installed', False)

        self.packages = self.utils.apply_package_pattern(data, packages)

    def execute(self) -> None:
        """Call methods in order."""
        self.creating_dependencies_list()
        if self.dependencies:
            self.view_process.message('Resolving dependencies')
        self.dependencies = self.choose_package_dependencies.choose(self.dependencies, self.view_process)
        self.add_dependencies_to_install_order()
        self.clean_the_main_slackbuilds()
        self.add_main_packages_to_install_order()
        self.check_for_skipped()

        self.view.install_upgrade_packages(self.packages, self.dependencies, self.mode)
        self.view.missing_dependencies(self.install_order)

        self.view.question()

        start: float = time.time()
        self.view.skipping_packages(self.skipped_packages)
        self.creating_the_package_urls_list()
        self.checksum_binary_packages()
        self.set_progress_message()
        self.install_packages()
        elapsed_time: float = time.time() - start

        self.utils.finished_time(elapsed_time)

    def creating_dependencies_list(self) -> None:
        """Create the full list of dependencies."""
        for package in self.packages:
            dependencies: tuple[str, ...] = Required(self.data, package, self.options).resolve()

            for dependency in dependencies:
                self.dependencies.append(dependency)

        self.dependencies = list(OrderedDict.fromkeys(self.dependencies))

    def add_dependencies_to_install_order(self) -> None:
        """Add dependencies in order to install."""
        self.install_order.extend(self.dependencies)

    def clean_the_main_slackbuilds(self) -> None:
        """Remove packages that already listed in dependencies."""
        for dependency in self.dependencies:
            if dependency in self.packages:
                self.packages.remove(dependency)

    def add_main_packages_to_install_order(self) -> None:
        """Add main packages in order to install."""
        self.install_order.extend(self.packages)

    def check_for_skipped(self) -> None:
        """Skip packages by user."""
        if self.option_for_skip_installed:
            for name in self.install_order:
                installed: str = self.utils.is_package_installed(name)
                if installed:
                    self.skipped_packages.append(name)

        # Remove packages from skipped packages.
        self.install_order = [pkg for pkg in self.install_order if pkg not in self.skipped_packages]

    def creating_the_package_urls_list(self) -> None:
        """Prepare package urls for downloading."""
        packages: dict[str, tuple[list[str], Path]] = {}
        asc_files: list[Path] = []
        if self.install_order:
            self.view_process.message('Prepare sources for downloading')
            for pkg in self.install_order:
                package: str = self.data[pkg]['package']
                mirror: str = self.data[pkg]['mirror']
                location: str = self.data[pkg]['location']
                url: list[str] = [f'{mirror}{location}/{package}']
                asc_url: list[str] = [f'{url}.asc']
                asc_file: Path = Path(self.tmp_slpkg, f'{package}.asc')

                packages[pkg] = (url, self.tmp_slpkg)
                if self.gpg_verification:
                    packages[f'{pkg}.asc'] = (asc_url, self.tmp_slpkg)
                    asc_files.append(asc_file)

                self.binary_packages.append(package)

            self.view_process.done()
            self.download_the_binary_packages(packages)
            if self.gpg_verification:
                self.gpg.verify(asc_files)

    def download_the_binary_packages(self, packages: dict[str, tuple[list[str], Path]]) -> None:
        """Download the packages.

        Args:
            packages (dict[str, tuple[list[str], Path]]): Packages for downloading.
        """
        if packages:
            print(f'Started to download total ({len(packages)}) packages:\n')
            self.download.download(packages)
            print()

    def checksum_binary_packages(self) -> None:
        """Checksum packages."""
        for package in self.binary_packages:
            name: str = self.utils.split_package(Path(package).stem)['name']
            pkg_checksum: str = self.data[name]['checksum']
            self.check_md5.md5sum(self.tmp_slpkg, package, pkg_checksum)

    def install_packages(self) -> None:
        """Install the packages."""
        # Remove old slpkg.log file.
        if self.slpkg_log_file.is_file():
            self.slpkg_log_file.unlink()

        if self.binary_packages:
            print(f'Started the processing of ({len(self.binary_packages)}) packages:\n')

            for package in self.binary_packages:
                command: str = f'{self.installpkg} {self.tmp_slpkg}/{package}'
                if self.option_for_reinstall:
                    command = f'{self.reinstall} {self.tmp_slpkg}/{package}'

                self.multi_proc.process_and_log(command, package, self.progress_message)
                name: str = self.utils.split_package(package)['name']
                self.write_deps_log(name)

                if self.delete_sources:
                    self.utils.remove_file_if_exists(self.tmp_slpkg, package)

    def write_deps_log(self, name: str) -> None:
        """Create log file with installed packages and dependencies.

        Args:
            name (str): Package name.
        """
        if self.utils.is_package_installed(name):
            deps_logs: dict[str, Any] = {}
            deps: dict[str, list[str]] = {}
            installed_requires: list[str] = []
            requires: tuple[str, ...] = Required(self.data, name, self.options).resolve()

            for require in requires:
                if self.utils.is_package_installed(require):
                    installed_requires.append(require)

            deps[name] = installed_requires
            if self.deps_log_file.is_file():
                deps_logs = self.utils.read_json_file(self.deps_log_file)
                deps_logs.update(deps)  # type: ignore
            self.deps_log_file.write_text(json.dumps(deps_logs, indent=4), encoding='utf-8')

    def set_progress_message(self) -> None:
        """Set message for upgrade method."""
        if self.mode == 'upgrade' or self.option_for_reinstall:
            self.progress_message = 'Upgrading'

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import shutil
import tempfile
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any

from slpkg.checksum import Md5sum
from slpkg.choose_dependencies import ChooseDependencies
from slpkg.choose_packages import Choose
from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.downloader import Downloader
from slpkg.gpg_verify import GPGVerify
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.sbos.dependencies import Requires
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess
from slpkg.views.views import View


class Slackbuilds:  # pylint: disable=[R0902,R0904]
    """Download, build and install the SlackBuilds."""

    def __init__(self, repository: str, data: dict[str, dict[str, str]], slackbuilds: list[str], options: dict[str, bool], mode: str) -> None:  # pylint: disable=[R0913, R0917]
        self.repository = repository
        self.data = data
        self.options = options
        self.mode = mode

        self.build_path = config_load.build_path
        self.is_64bit = config_load.is_64bit()
        self.gpg_verification = config_load.gpg_verification
        self.slpkg_log_file = config_load.slpkg_log_file
        self.delete_sources = config_load.delete_sources
        self.progress_bar = config_load.progress_bar
        self.installpkg = config_load.installpkg
        self.reinstall = config_load.reinstall
        self.deps_log_file = config_load.deps_log_file
        self.tmp_slpkg = config_load.tmp_slpkg
        self.tmp_path = config_load.tmp_path
        self.prog_name = config_load.prog_name
        self.makeflags = config_load.makeflags
        self.dialog = config_load.dialog
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.red = config_load.red
        self.endc = config_load.endc

        self.repos = Repositories()
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

        self.output_env: Path = Path()
        self.sources: dict[str, tuple[list[str], Path]] = {}
        self.build_order: list[str] = []
        self.dependencies: list[str] = []
        self.skipped_packages: list[str] = []
        self.asc_files: list[Path] = []
        self.repo_data: list[str] = []
        self.count_sources: int = 0
        self.progress_message: str = 'Installing'

        self.option_for_reinstall: bool = options.get('option_reinstall', False)
        self.option_for_skip_installed: bool = options.get('option_skip_installed', False)
        self.slackbuilds: list[str] = self.utils.apply_package_pattern(data, slackbuilds)

        self.repo_tag: str = self.repos.repositories[repository]['repo_tag']
        self.tar_suffix: str = self.repos.repositories[repository]['tar_suffix']

    def execute(self) -> None:
        """Call the methods in order."""
        self.creating_dependencies_list()
        if self.dependencies:
            self.view_process.message('Resolving dependencies')
        self.dependencies = self.choose_package_dependencies.choose(self.dependencies, self.view_process)
        self.add_dependencies_to_install_order()
        self.clean_the_main_slackbuilds()
        self.add_main_packages_to_install_order()
        self.check_for_skipped()
        self.view_slackbuilds_before_build()
        self.view.missing_dependencies(self.build_order)

        self.view.question()

        start: float = time.time()
        self.view.skipping_packages(self.skipped_packages)
        self.prepare_slackbuilds_for_build()
        self.download_the_sources()
        self.set_progress_message()
        self.build_and_install_the_slackbuilds()
        elapsed_time: float = time.time() - start

        self.utils.finished_time(elapsed_time)

    def creating_dependencies_list(self) -> None:
        """Create the package dependencies list."""
        for slackbuild in self.slackbuilds:
            dependencies: tuple[str, ...] = Requires(self.data, slackbuild, self.options).resolve()

            for dependency in dependencies:
                self.dependencies.append(dependency)

        self.dependencies = list(OrderedDict.fromkeys(self.dependencies))

    def add_dependencies_to_install_order(self) -> None:
        """Add the dependency list in order for install."""
        self.build_order.extend(self.dependencies)

    def clean_the_main_slackbuilds(self) -> None:
        """Remove main packages if they already added as dependency."""
        for dep in self.dependencies:
            if dep in self.slackbuilds:
                self.slackbuilds.remove(dep)

    def add_main_packages_to_install_order(self) -> None:
        """Add the main packages to order for install."""
        self.build_order.extend(self.slackbuilds)

    def check_for_skipped(self) -> None:
        """Check packages for skipped."""
        if self.option_for_skip_installed:
            for name in self.build_order:
                installed: str = self.utils.is_package_installed(name)
                if installed:
                    self.skipped_packages.append(name)

        # Remove packages from skipped packages.
        self.build_order = [pkg for pkg in self.build_order if pkg not in self.skipped_packages]

    def view_slackbuilds_before_build(self) -> None:
        """View packages before build."""
        if self.mode == 'build':
            self.view.build_packages(self.slackbuilds, self.dependencies)
        else:
            self.view.install_upgrade_packages(self.slackbuilds, self.dependencies, self.mode)

    def prepare_slackbuilds_for_build(self) -> None:
        """Prepare slackbuilds for build."""
        if self.build_order:
            self.view_process.message('Prepare sources for downloading')
            for sbo in self.build_order:
                build_path: Path = Path(self.build_path, sbo)

                # self.utils.remove_folder_if_exists(build_path)
                location = self.data[sbo]['location']
                self.repo_data = [self.repository, self.data[sbo]['location']]
                slackbuild: Path = Path(self.build_path, sbo, f'{sbo}.SlackBuild')

                # Copy slackbuilds to the build folder.
                repo_package: Path = Path(self.repos.repositories[self.repository]['path'], location, sbo)

                shutil.copytree(repo_package, build_path, dirs_exist_ok=True)

                os.chmod(slackbuild, 0o775)

                if self.is_64bit and self.data[sbo].get('download64'):
                    sources: list[str] = list(self.data[sbo]['download64'])
                else:
                    sources = list(self.data[sbo]['download'])

                self.count_sources += len(sources)

                if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
                    asc_file: Path = Path(self.repos.repositories_path, self.repos.sbo_repo_name,
                                          location, f'{sbo}{self.tar_suffix}.asc')
                    self.asc_files.append(asc_file)

                self.sources[sbo] = (sources, Path(self.build_path, sbo))

            self.view_process.done()

    def download_the_sources(self) -> None:
        """Download the sources."""
        if self.sources:
            print(f'Started to download total ({self.count_sources}) sources:\n')
            self.download.download(self.sources, self.repo_data)
            print()

            self.checksum_downloaded_sources()

    def checksum_downloaded_sources(self) -> None:
        """Checksum the sources."""
        for sbo in self.build_order:
            path: Path = Path(self.build_path, sbo)

            if self.is_64bit and self.data[sbo].get('download64'):
                checksums: str = self.data[sbo]['md5sum64']
                sources: str = self.data[sbo]['download64']
            else:
                checksums = self.data[sbo]['md5sum']
                sources = self.data[sbo]['download']

            for source, checksum in zip(sources, checksums):
                self.check_md5.md5sum(path, source, checksum)

    def build_and_install_the_slackbuilds(self) -> None:
        """Build or install the slackbuilds."""
        if self.slpkg_log_file.is_file():  # Remove old slpkg.log file.
            self.slpkg_log_file.unlink()

        if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
            self.gpg.verify(self.asc_files)

        if self.build_order:
            print(f'Started the processing of ({len(self.build_order)}) packages:\n')

            for sbo in self.build_order:
                self.patch_slackbuild_tag(sbo)
                self.build_the_script(self.build_path, sbo)

                if self.mode in ('install', 'upgrade'):
                    self.install_package(sbo)

                if self.delete_sources:
                    sbo_build_folder: Path = Path(self.build_path, sbo)
                    self.utils.remove_folder_if_exists(sbo_build_folder)

                self.move_package_and_delete_folder()

    def patch_slackbuild_tag(self, sbo: str) -> None:
        """Patch the slackbuild tag.

        Args:
            sbo (str): Slackbuild name.
        """
        sbo_script: Path = Path(self.build_path, sbo, f'{sbo}.SlackBuild')
        if sbo_script.is_file() and self.repo_tag:
            lines: list[str] = self.utils.read_text_file(sbo_script)

            with open(sbo_script, 'w', encoding='utf-8') as script:
                for line in lines:
                    if line.startswith('TAG=$'):
                        line = f'TAG=${{TAG:-{self.repo_tag}}}\n'
                    script.write(line)

    def install_package(self, name: str) -> None:
        """Install the slackbuild.

        Args:
            name (str): Slackbuild name.
        """
        package: str = [f.name for f in self.output_env.iterdir() if f.is_file()][0]

        command: str = f'{self.installpkg} {self.output_env}/{package}'
        if self.option_for_reinstall:
            command = f'{self.reinstall} {self.output_env}/{package}'

        self.multi_proc.process_and_log(command, package, self.progress_message)
        self.write_deps_log(name)

    def move_package_and_delete_folder(self) -> None:
        """Move binary package to /tmp folder and delete temporary folder."""
        package_name: str = [f.name for f in self.output_env.iterdir() if f.is_file()][0]
        binary_path_file: Path = Path(self.output_env, package_name)

        # Remove binary package file from /tmp folder if exist before move the new one.
        self.utils.remove_file_if_exists(self.tmp_path, package_name)

        # Move the new binary package file to /tmp folder.
        if binary_path_file.is_file():
            shutil.move(binary_path_file, self.tmp_path)
            if not self.progress_bar:
                message: str = f'| Moved: {package_name} to the {self.tmp_path} folder.'
                length_message: int = len(message) - 1
                print(f"\n+{'=' * length_message}")
                print(message)
                print(f"+{'=' * length_message}\n")

        # Delete the temporary empty folder.
        self.utils.remove_folder_if_exists(Path(self.output_env))

    def write_deps_log(self, name: str) -> None:
        """Create a log file with Slackbuild dependencies.

        Args:
            name (str): Slackbuild name.
        """
        if self.utils.is_package_installed(name):
            deps_logs: dict[str, Any] = {}
            deps: dict[str, list[str]] = {}
            installed_requires: list[str] = []
            requires: tuple[str, ...] = Requires(self.data, name, self.options).resolve()

            for require in requires:
                if self.utils.is_package_installed(require):
                    installed_requires.append(require)

            # Write deps to deps.log file.
            deps[name] = installed_requires
            if self.deps_log_file.is_file():
                deps_logs = self.utils.read_json_file(self.deps_log_file)
                deps_logs.update(deps)  # type: ignore
            self.deps_log_file.write_text(json.dumps(deps_logs, indent=4), encoding='utf-8')

    def build_the_script(self, path: Path, name: str) -> None:
        """Build the slackbuild script.

        Args:
            path (Path): Path to build the script.
            name (str): Slackbuild name.
        """
        self.set_makeflags()
        self.output_env = Path(tempfile.mkdtemp(dir=self.tmp_slpkg, prefix=f'{self.prog_name}.'))
        os.environ['OUTPUT'] = str(self.output_env)
        folder: Path = Path(path, name)
        filename: str = f'{name}.SlackBuild'
        command: str = f'{folder}/./{filename}'
        self.utils.change_owner_privileges(folder)
        progress_message: str = 'Building'
        self.multi_proc.process_and_log(command, filename, progress_message)

    def set_progress_message(self) -> None:
        """Set progress message for upgrade."""
        if self.mode == 'upgrade' or self.option_for_reinstall:
            self.progress_message = 'Upgrading'

    def set_makeflags(self) -> None:
        """Set makeflags."""
        os.environ['MAKEFLAGS'] = f'-j {self.makeflags}'

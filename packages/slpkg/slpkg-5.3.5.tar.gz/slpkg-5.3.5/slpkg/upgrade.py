#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import platform
import shutil
from pathlib import Path
from typing import Any, Generator, Optional, Union, cast

from packaging.version import InvalidVersion, parse

from slpkg.config import config_load
from slpkg.load_data import LoadData
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities


class Upgrade:  # pylint: disable=[R0902]
    """Upgrade the installed packages."""

    def __init__(self, repository: Optional[str], data: Optional[Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]]]) -> None:
        self.repository = cast(str, repository)  # Informs mypy that it will NOT be None.
        self.data = cast(Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]], data)

        self.log_packages = config_load.log_packages
        self.upgrade_log_file = config_load.upgrade_log_file
        self.kernel_version = config_load.kernel_version
        self.package_method = config_load.package_method
        self.downgrade_packages = config_load.downgrade_packages
        self.grey = config_load.grey
        self.yellow = config_load.yellow
        self.red = config_load.red
        self.green = config_load.green
        self.endc = config_load.endc

        self.utils = Utilities()
        self.repos = Repositories()
        self.load_data = LoadData()

        self.id: int = 0
        self.log_id: int = 0
        self.sum_upgrade: int = 0
        self.sum_removed: int = 0
        self.sum_added: int = 0
        self.installed_packages: list[Path] = []

        self.kernel_ver: str = platform.uname()[2]
        self.columns, self.rows = shutil.get_terminal_size()

    def load_installed_packages(self, repository: str) -> None:
        """Load installed packages.

        Args:
            repository (str): Repository name.
        """
        if repository == self.repos.slack_repo_name:
            extra_repo: dict[str, dict[str, str]] = {}

            extra_data_file: Path = Path(self.repos.repositories[self.repos.slack_extra_repo_name]['path'],
                                         self.repos.data_json)

            if self.repos.repositories[self.repos.slack_extra_repo_name]['enable'] and extra_data_file.is_file():
                extra_repo = self.load_data.load(self.repos.slack_extra_repo_name, message=False)

            installed: dict[str, str] = self.utils.all_installed()

            for name, package in installed.items():
                tag: str = self.utils.split_package(package)['tag']
                if not tag:  # Add only Slackware original packages that have not package tag.
                    if extra_repo.get(name):  # Avoid installed packages from extra repository.
                        extra_package: str = extra_repo[name]['package']
                        if extra_package[:-4] != package:
                            self.installed_packages.append(Path(package))
                    else:
                        self.installed_packages.append(Path(package))
        else:
            repo_tag: str = self.repos.repositories[repository]['repo_tag']
            self.installed_packages = list(self.log_packages.glob(f'*{repo_tag}'))

    def packages(self) -> Generator[str, str, str]:
        """Return the upgradeable packages."""
        # Delete log file before starts.
        if self.upgrade_log_file.is_file():
            self.upgrade_log_file.unlink()

        self.load_installed_packages(self.repository)

        for inst in self.installed_packages:
            name: str = self.utils.split_package(inst.name)['name']
            if self.is_package_upgradeable(inst.name):
                yield name

            if self.repository in self.repos.remove_packages:
                if name not in self.data.keys():
                    yield f'{name}_Removed.'

        if self.repository in self.repos.new_packages:
            all_installed: dict[str, str] = self.utils.all_installed()
            for name in self.data.keys():
                if name not in all_installed:
                    # if not self.utils.is_package_installed(name):
                    yield f'{name}_Added.'
        return ""

    def is_package_upgradeable(self, installed: str) -> bool:  # pylint: disable=[R0911]
        """Return True for upgradeable packages.

        Args:
            installed (str): Installed package.

        Returns:
            bool: True if the package is upgradeable.
        """
        inst_name: str = self.utils.split_package(installed)['name']

        if self.data.get(inst_name):
            repo_version: str = self.data[inst_name]['version']  # type: ignore
            repo_build: str = self.data[inst_name]['build']  # type: ignore

            inst_version: str = self.utils.split_package(installed)['version']
            if self.kernel_version and inst_version.endswith(f'_{self.kernel_ver}'):
                inst_version = inst_version.replace(f'_{self.kernel_ver}', '')
                installed = installed.replace(f'_{self.kernel_ver}', '')

            inst_build: str = self.utils.split_package(installed)['build']

            if self.package_method:
                repo_package: str = self.data[inst_name]['package'][:-4]  # type: ignore
                if installed != repo_package:
                    return True

            else:
                try:
                    if parse(repo_version) > parse(inst_version):
                        return True

                    if parse(repo_version) == parse(inst_version) and int(repo_build) > int(inst_build):
                        return True

                    if self.downgrade_packages and (parse(repo_version) < parse(inst_version)):
                        return True
                except InvalidVersion as err:
                    if repo_version > inst_version:  # Try to compare the strings.
                        return True
                    if repo_version == inst_version and int(repo_build) > int(inst_build):
                        return True
                    self._write_log_file(installed, inst_name, err)

        return False

    def _write_log_file(self, installed: str, name: str, err: InvalidVersion) -> None:
        """Write a log file for invalid versions.

        Args:
            installed (str): Installed package.
            name (str): Package name.
            err (InvalidVersion): InvalidVersion error.
        """
        self.log_id += 1
        log: dict[Any, Any] = {}
        if self.upgrade_log_file.is_file():
            log = self.utils.read_json_file(self.upgrade_log_file)

        log[self.log_id] = {
            'installed': installed,
            'repo package': self.data[name]['package'],
            'repo name': self.repository,
            'error': str(err)
        }
        self.upgrade_log_file.write_text(json.dumps(log, indent=4), encoding='utf-8')

    def check_packages(self) -> None:
        """Check only which packages are upgradeable."""
        repo_data: dict[str, dict[str, dict[str, str]]] = {}
        found_packages: dict[int, dict[str, str]] = {}

        if self.repository == '*':
            repo_data = self.data  # type: ignore
        else:
            repo_data[self.repository] = self.data  # type: ignore

        for repo, data in repo_data.items():
            self.load_installed_packages(repo)

            for installed in sorted(self.installed_packages):
                name: str = self.utils.split_package(installed.name)['name']

                if data.get(name):
                    self.data = data

                    if self.is_package_upgradeable(installed.name):
                        self.id += 1
                        self.sum_upgrade += 1

                        inst_version: str = self.utils.split_package(installed.name)['version']
                        inst_build: str = self.utils.split_package(installed.name)['build']
                        repo_version: str = data[name]['version']
                        repo_build: str = data[name]['build']

                        found_packages[self.id] = {
                            'name': name,
                            'inst_version': inst_version,
                            'inst_build': inst_build,
                            'repo_version': repo_version,
                            'repo_build': repo_build,
                            'repo': repo,
                            'type': 'upgrade'
                        }

                if repo in self.repos.remove_packages:
                    tag: str = self.utils.split_package(installed.name)['tag']
                    if not tag and name not in data.keys():
                        self.id += 1
                        self.sum_removed += 1
                        inst_version = self.utils.split_package(installed.name)['version']
                        inst_build = self.utils.split_package(installed.name)['build']

                        found_packages[self.id] = {
                            'name': name,
                            'inst_version': inst_version,
                            'inst_build': inst_build,
                            'repo_version': '',
                            'repo_build': '',
                            'repo': repo,
                            'type': 'remove'
                        }

            if repo in self.repos.new_packages:
                for name in data.keys():
                    if not self.utils.is_package_installed(name):
                        self.id += 1
                        self.sum_added += 1
                        repo_version = data[name]['version']
                        repo_build = data[name]['build']

                        found_packages[self.id] = {
                            'name': name,
                            'inst_version': '',
                            'inst_build': '',
                            'repo_version': repo_version,
                            'repo_build': repo_build,
                            'repo': self.repos.slack_repo_name,
                            'type': 'add'
                        }
        self._results(found_packages)

    def _results(self, found_packages: dict[int, dict[str, str]]) -> None:
        """Print the results of checking.

        Args:
            found_packages (dict[str, Any]): Data of packages.

        Raises:
            SystemExit: Exit code 0.
        """
        if found_packages:
            print()

            name_alignment: int = 18
            if self.columns > 80:
                name_alignment = (self.columns - 80) + 18

            title: str = (f"{'packages':<{name_alignment}} {'Repository':<15} {'Build':<6} {'Installed':<15} "
                          f"{'Build':<5} {'Repo':>15}")
            print(len(title) * '=')
            print(title)
            print(len(title) * '=')

            for data in found_packages.values():
                name: str = data['name']
                repo_version: str = data['repo_version']
                repo_build: str = data['repo_build']
                inst_version: str = data['inst_version']
                inst_build: str = data['inst_build']
                repo: str = data['repo']
                mode: str = data['type']

                if len(name) > name_alignment:
                    name = f'{name[:name_alignment - 4]}...'
                if len(inst_version) > 15:
                    inst_version = f"{inst_version[:11]}..."
                if len(repo_version) > 15:
                    repo_version = f"{repo_version[:11]}..."

                color: str = self.yellow
                if mode == 'remove':
                    color = self.red
                if mode == 'add':
                    color = self.green

                print(f"{color}{name:<{name_alignment}}{self.endc} {repo_version:<15} "
                      f"{repo_build:<6} {inst_version:<15} "
                      f"{inst_build:<5} {repo:>15}")

            print(len(title) * '=')
            print(f'{self.grey}Total packages: {self.sum_upgrade} upgraded, '
                  f'{self.sum_removed} removed and {self.sum_added} added.{self.endc}\n')
        else:
            print('\nEverything is up-to-date!\n')
        raise SystemExit(0)

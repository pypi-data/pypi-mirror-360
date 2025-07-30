#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
import shutil
from typing import Any, Optional, Union

from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.terminal_selector import TerminalSelector
from slpkg.utilities import Utilities


class Choose:  # pylint: disable=[R0902]
    """
    Choose packages with dialog or with terminal selector.
    """

    def __init__(self, options: dict[str, bool], repository: Optional[str] = '') -> None:
        self.repository = repository
        self.options = options

        self.dialog = config_load.dialog
        self.bold = config_load.bold
        self.green = config_load.green
        self.red = config_load.red
        self.endc = config_load.endc

        self.utils = Utilities()
        self.dialogbox = DialogBox()

        self.choices: list[tuple[Any, ...]] = []
        self.height: int = 10
        self.width: int = 70
        self.list_height: int = 0
        self.ordered: bool = True
        self.columns, self.rows = shutil.get_terminal_size()
        self.match_packages: list[str] = []

        self.option_for_select_packages: bool = options.get('option_select', False)

    def packages(self, data: dict[str, dict[str, str]], packages: list[str], method: str, ordered: bool = True) -> list[str]:
        """Call methods to choosing packages via dialog tool.

        Args:
            data (dict[str, dict[str, str]]): Repository data.
            packages (list[str]): List of packages.
            method (str): Type of method.
            ordered (bool, optional): Set True for ordered.

        Returns:
            list[str]: Name of packages.

        Raises:
            SystemExit: Exit code 0.
        """
        title: str = f' Choose packages you want to {method} '
        is_upgrade = False

        if ordered:
            packages = sorted(packages)

        if method in ('remove', 'list_installed'):
            self.choose_from_installed(packages)
        elif method == 'upgrade':
            title = f' Choose packages you want to {method} or add '
            is_upgrade = True
            self.choose_for_upgraded(data, packages)
        else:
            self.choose_for_others(data, packages)

        if not self.choices:
            return packages

        if self.dialog:
            text: str = f'There are {len(self.choices)} packages:'
            code, packages = self.dialogbox.checklist(text, title, self.height, self.width,
                                                      self.list_height, self.choices)
            if code == 'cancel' or not packages:
                os.system('clear')
                raise SystemExit(0)

            os.system('clear')
        else:
            initial_selection: Union[str, None] = 'all'

            if self.option_for_select_packages:
                initial_selection = None

            terminal_selector = TerminalSelector(self.match_packages, title, data, is_upgrade, initial_selection=initial_selection)
            packages = terminal_selector.select()

        return packages

    def choose_from_installed(self, packages: list[str]) -> None:
        """Choose installed packages for remove or find.

        Args:
            packages (list[str]): Name of packages.
        """
        for name, package in self.utils.all_installed().items():
            version: str = self.utils.split_package(package)['version']

            for pkg in sorted(packages):
                if pkg in name or pkg == '*':
                    self.match_packages.append(name)
                    self.choices.extend([(name, version, False, f'Package: {package}')])

    def choose_for_upgraded(self, data: dict[str, dict[str, str]], packages: list[str]) -> None:
        """Choose packages that they will going to upgrade.

        Args:
            data (dict[str, dict[str, str]]): Data of repository.
            packages (list[str]): Name of packages.
        """
        for package in packages:

            inst_package: str = self.utils.is_package_installed(package)
            inst_package_version: str = self.utils.split_package(inst_package)['version']
            inst_package_build: str = self.utils.split_package(inst_package)['build']

            repo_ver: str = data[package]['version']
            repo_build_tag: str = data[package]['build']

            if not inst_package:
                new_package: str = data[package]['package']
                self.match_packages.append(package)
                self.choices.extend(
                    [(package, ' <- \\Z1Add\\Zn New Package ', True,
                      f'Add new package -> {new_package} Build: {repo_build_tag}')])
            else:
                self.match_packages.append(package)
                self.choices.extend(
                    [(package, f' {inst_package_version} -> \\Z3\\Zb{repo_ver}\\Zn ', True,
                      f'Installed: {package}-{inst_package_version} Build: {inst_package_build} -> '
                      f'Available: {repo_ver} Build: {repo_build_tag}')])

    def choose_for_others(self, data: dict[str, dict[str, Any]], packages: list[str]) -> None:
        """Choose packages for others methods like install, tracking etc.

        Args:
            data (dict[str, dict[str, Any]]): Repository data.
            packages (list[str]): Name of packages.
        """
        if self.repository == '*':
            for pkg in sorted(packages):
                for repo_name, repo_data in data.items():
                    for package in repo_data.keys():
                        if pkg in package or pkg == '*':
                            version: str = repo_data[package]['version']
                            self.match_packages.append(package)
                            self.choices.extend([(package, version, False, f'Package: {package}-{version} '
                                                                           f'> {repo_name}')])

        else:
            for pkg in sorted(packages):
                for package in data.keys():
                    if pkg in package or pkg == '*':
                        version = data[package]['version']
                        self.match_packages.append(package)
                        self.choices.extend([(package, version, False, f'Package: {package}-{version} '
                                                                       f'> {self.repository}')])

#!/usr/bin/python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import json
import os
import time
from typing import Any

from slpkg.choose_packages import Choose
from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.multi_process import MultiProcess
from slpkg.terminal_selector import TerminalSelector
from slpkg.utilities import Utilities
from slpkg.views.views import View


class RemovePackages:  # pylint: disable=[R0902]
    """Remove installed packages with dependencies."""

    def __init__(self, packages: list[str], options: dict[str, bool]) -> None:
        self.packages = packages

        self.slpkg_log_file = config_load.slpkg_log_file
        self.deps_log_file = config_load.deps_log_file
        self.removepkg = config_load.removepkg
        self.dialog = config_load.dialog
        self.ask_question = config_load.ask_question
        self.red = config_load.red
        self.grey = config_load.grey
        self.endc = config_load.endc
        self.answer_yes = config_load.answer_yes

        self.dialogbox = DialogBox()
        self.utils = Utilities()
        self.multi_proc = MultiProcess(options)
        self.view = View(options=options)
        self.choose_packages = Choose(options)

        self.deps_log: dict[str, Any] = {}
        self.packages_for_remove: list[str] = []
        self.dependencies: list[str] = []
        self.found_dependent_packages: dict[str, str] = {}

        self.option_for_resolve_off: bool = options.get('option_resolve_off', False)

    def remove(self, upgrade: bool = False) -> None:
        """Remove packages.

        Args:
            upgrade (bool, optional): Is packages comes from upgrade method.
        """
        if not self.option_for_resolve_off:
            self.deps_log = self.utils.read_json_file(self.deps_log_file)

        if upgrade:
            self.packages = self.choose_packages_for_remove(self.packages, upgrade)

        if self.packages:
            self.add_packages_for_remove()
            self.remove_doubles_dependencies()
            self.dependencies = self.choose_packages_for_remove(self.dependencies)
            self.add_installed_dependencies_to_remove()

            self.view.remove_packages(self.packages, self.dependencies)
            self.find_dependent()

            answer: str = 'y'
            if upgrade:
                answer = self.remove_question()
            else:
                self.view.question()

            if answer in ['y', 'Y']:
                start: float = time.time()
                self.remove_packages()
                elapsed_time: float = time.time() - start
                self.utils.finished_time(elapsed_time)

    def add_packages_for_remove(self) -> None:
        """Add packages for remove."""
        for package in self.packages:
            installed: str = self.utils.is_package_installed(package)
            if installed:
                self.packages_for_remove.append(installed)

            if self.deps_log.get(package):
                dependencies: list[str] = self.deps_log[package]
                for dep in dependencies:
                    if self.utils.is_package_installed(dep) and dep not in self.packages:
                        self.dependencies.append(dep)

    def find_dependent(self) -> None:
        """Find packages that depend on other packages."""
        for package in self.packages_for_remove:
            name: str = self.utils.split_package(package)['name']
            for pkg, deps in self.deps_log.items():
                if name in deps and pkg not in self.packages + self.dependencies:
                    version: str = ''
                    installed: str = self.utils.is_package_installed(pkg)
                    if installed:
                        version = self.utils.split_package(installed)['version']
                    self.found_dependent_packages[pkg] = version

        if self.found_dependent_packages:
            dependent_packages: list[str] = list(set(self.found_dependent_packages))
            print(f'\n{self.red}Warning: {self.endc}found extra ({len(dependent_packages)}) dependent packages:')
            for pkg, ver in self.found_dependent_packages.items():
                print(f"{'':>2}{pkg} {self.grey}{ver}{self.endc}")
            print('')

    def remove_doubles_dependencies(self) -> None:
        """Remove doubles packages."""
        self.dependencies = list(set(self.dependencies))

    def add_installed_dependencies_to_remove(self) -> None:
        """Add dependencies for remove."""
        for dep in self.dependencies:
            installed: str = self.utils.is_package_installed(dep)
            if installed:
                self.packages_for_remove.append(installed)

    def remove_packages(self) -> None:
        """Remove packages."""
        # Remove old slpkg.log file.
        if self.slpkg_log_file.is_file():
            self.slpkg_log_file.unlink()

        print(f'Started of removing total ({len(self.packages_for_remove)}) packages:\n')
        for package in self.packages_for_remove:
            command: str = f'{self.removepkg} {package}'
            progress_message: str = 'Removing'

            self.multi_proc.process_and_log(command, package, progress_message)
            name: str = self.utils.split_package(package)['name']
            if name in self.deps_log.keys():
                self.deps_log.pop(name)

        self.deps_log_file.write_text(json.dumps(self.deps_log, indent=4), encoding='utf-8')

    def choose_packages_for_remove(self, packages: list[str], upgrade: bool = False) -> list[str]:
        """Choose packages via dialog utility.

        Args:
            packages (list[str]): Description
            upgrade (bool, optional): Description

        Returns:
            list[str]: List of package names.
        """
        if packages:
            height: int = 10
            width: int = 70
            list_height: int = 0
            choices: list[Any] = []
            title: str = ' Choose dependencies you want to remove '
            text: str = f'There are {len(choices)} dependencies:'
            if upgrade:
                title = ' Choose packages you want to remove '
                text = f'There are {len(choices)} packages:'

            for package in packages:
                installed_package: str = self.utils.is_package_installed(package)
                installed_version: str = self.utils.split_package(installed_package)['version']
                choices.extend([(package, installed_version, True, f'Package: {installed_package}')])

            if self.dialog:
                code, packages = self.dialogbox.checklist(text, title, height, width, list_height,  # pylint: disable=[W0612]
                                                          choices)
                os.system('clear')
            else:
                terminal_selector = TerminalSelector(self.dependencies, title, data={}, is_upgrade=False, initial_selection='all')
                packages = terminal_selector.select()
        return packages

    def remove_question(self) -> str:
        """Question about remove packages for upgrade method.

        Returns:
            str: Answer yes or no.
        """
        answer: str = 'n'
        if self.ask_question:
            try:
                if self.answer_yes:
                    answer = 'y'
                else:
                    answer = input('\nDo you want to remove these packages? [y/N] ')
            except (KeyboardInterrupt, EOFError) as err:
                print('\nOperation canceled by the user.')
                raise SystemExit(1) from err
        return answer

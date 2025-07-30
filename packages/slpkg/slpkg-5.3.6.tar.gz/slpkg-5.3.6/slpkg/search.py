#!/usr/bin/python3
# -*- coding: utf-8 -*-


from typing import Any, Union

from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess


class SearchPackage:  # pylint: disable=[R0902]
    """Search packages from the repositories."""

    def __init__(self, options: dict[str, bool], packages: list[str], data: Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]], repository: str) -> None:
        self.packages = packages
        self.data = data
        self.repository = repository

        self.grey = config_load.grey
        self.green = config_load.green
        self.endc = config_load.endc

        self.utils = Utilities()
        self.repos = Repositories()
        self.view_process = ViewProcess()

        self.matching: int = 0
        self.data_dict: dict[int, dict[str, str]] = {}
        self.repo_data: Union[dict[str, str], dict[str, dict[str, str]], Any] = {}
        self.all_data: Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]] = {}

        self.option_for_no_case: bool = options.get('option_no_case', False)
        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)
        self.option_for_pkg_description: bool = options.get('option_pkg_description', False)

    def search(self) -> None:
        """Choose between all and one repository."""
        self.view_process.message('Please wait for the results')
        if self.repository == '*':
            self.search_to_all_repositories()
        else:
            self.repo_data = self.data
            self.search_for_the_packages(self.repository)

        self.view_process.done()
        print()
        self.summary_of_searching()

    def search_to_all_repositories(self) -> None:
        """Search package name to all enabled repositories."""
        self.all_data = self.data
        for name, repo in self.all_data.items():
            self.repo_data = repo
            self.search_for_the_packages(name)

    def search_for_the_packages(self, repo: str) -> None:
        """Search for packages and save in a dictionary.

        Args:
            repo (str): repository name.
        """
        for package in self.packages:
            for name, data_pkg in sorted(self.repo_data.items()):

                if package in name or package == '*' or self.is_not_case_sensitive(package, name):
                    self.matching += 1
                    installed: str = ''
                    is_installed: str = self.utils.is_package_installed(name)

                    if self.repository == '*':
                        if is_installed == self.all_data[repo][name]['package'][:-4]:  # type: ignore
                            installed = '[installed]'
                    elif is_installed == self.data[name]['package'][:-4]:  # type: ignore
                        installed = '[installed]'

                    if isinstance(data_pkg, dict):
                        self.data_dict[self.matching] = {
                            'repository': repo,
                            'name': name,
                            'version': data_pkg['version'],
                            'installed': installed
                        }

    def summary_of_searching(self) -> None:
        """Print the result."""
        try:
            repo_length: int = max(len(repo['repository']) for repo in self.data_dict.values())
        except ValueError:
            repo_length = 1

        try:
            name_length: int = max(len(name['name']) + len(name['installed']) for name in self.data_dict.values())
        except ValueError:
            name_length = 1

        if self.matching:
            version: str = ''
            repository: str = ''
            desc: str = ''
            for item in self.data_dict.values():
                name: str = item['name']
                package_name: str = f"{name} {item['installed']}"

                if self.option_for_pkg_version:
                    version = item['version']
                if self.repository == '*':
                    repository = f"{item['repository']:<{repo_length}} : "
                if self.option_for_pkg_description and self.repository != '*':
                    desc: str = self.data[name]['description']  # type: ignore
                    package_name = f"{name}: {item['installed']}"

                print(f"{repository}{package_name:<{name_length}} {version}")
                if desc:
                    print(f"  {self.green}{desc}{self.endc}")

            print(f'\n{self.grey}Total found {self.matching} packages.{self.endc}')
        else:
            print('\nDoes not match any package.\n')

    def is_not_case_sensitive(self, package: str, name: str) -> bool:
        """Check for case-sensitive.

        Args:
            package (str): Package file.
            name (str): Package name.

        Returns:
            bool: True or False.
        """
        if self.option_for_no_case:
            return package.lower() in name.lower()
        return False

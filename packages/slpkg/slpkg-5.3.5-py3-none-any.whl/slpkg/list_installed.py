#!/usr/bin/python3
# -*- coding: utf-8 -*-


from pathlib import Path

from slpkg.config import config_load
from slpkg.utilities import Utilities


class ListInstalled:  # pylint: disable=[R0902]
    """Find the installed packages."""

    def __init__(self, options: dict[str, bool], packages: list[str]) -> None:
        self.packages = packages

        self.grey = config_load.grey
        self.green = config_load.green
        self.endc = config_load.endc
        self.log_packages = config_load.log_packages

        self.utils = Utilities()
        self.matching: list[str] = []
        self.total_size: int = 0

        self.option_for_no_case: bool = options.get('option_no_case', False)
        self.option_for_pkg_description: bool = options.get('option_pkg_description', False)

    def installed(self) -> None:
        """Find the packages."""
        self.view_title()
        for package in self.packages:
            for name in self.utils.all_installed().values():

                if package in name or package == '*' or self.is_not_case_sensitive(package, name):
                    self.matching.append(name)
        self.view_matched_packages()

    @staticmethod
    def view_title() -> None:
        """Print the title."""
        print('The list below shows the installed packages:\n')

    def view_matched_packages(self) -> None:
        """Print the matching packages."""
        if self.matching:
            for package in self.matching:
                name: str = self.utils.split_package(package)['name']
                pkg_size: int = self.utils.count_file_size(name)
                size: str = self.utils.convert_file_sizes(pkg_size)
                self.total_size += pkg_size
                print(f'{package} ({size})')

                if self.option_for_pkg_description:
                    pkg_file: Path = Path(self.log_packages, package)
                    pkg_txt_list: list[str] = self.utils.read_text_file(pkg_file)
                    for line in pkg_txt_list:
                        if line.startswith(f'{name}: {name}'):
                            print(f'{self.green}{line[(len(name) * 2) + 2:]}{self.endc}', end='')
                            break

            self.view_summary()
        else:
            print('\nDoes not match any package.\n')

    def view_summary(self) -> None:
        """Print the summary."""
        print(f'\n{self.grey}Total found {len(self.matching)} packages with '
              f'{self.utils.convert_file_sizes(self.total_size)} size.{self.endc}')

    def is_not_case_sensitive(self, package: str, name: str) -> bool:
        """Check for case-sensitive.

        Args:
            package (str): Package file.
            name (str): Name of package.

        Returns:
            bool: True or False.
        """
        if self.option_for_no_case:
            return package.lower() in name.lower()
        return False

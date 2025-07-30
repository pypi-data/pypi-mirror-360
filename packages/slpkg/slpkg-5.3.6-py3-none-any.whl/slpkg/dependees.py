#!/usr/bin/python3
# -*- coding: utf-8 -*-


from typing import Generator

from slpkg.config import config_load
from slpkg.utilities import Utilities


class Dependees:  # pylint: disable=[R0902]
    """Prints the packages that depend on."""

    def __init__(self, data: dict[str, dict[str, str]], packages: list[str], options: dict[str, bool]) -> None:
        self.data = data
        self.packages = packages
        self.options = options

        self.bold = config_load.bold
        self.grey = config_load.grey
        self.endc = config_load.endc

        self.utils = Utilities()

        self.option_for_full_reverse: bool = options.get('option_full_reverse', False)
        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)

    def find(self) -> None:
        """Call the methods."""
        print('The list below shows the packages that dependees on:\n')
        self.packages = self.utils.apply_package_pattern(self.data, self.packages)

        for package in self.packages:
            dependees: dict[str, str] = dict(self.find_requires(package))
            self.view_the_main_package(package)
            self.view_no_dependees(dependees)
            self.view_dependees(dependees)
            self.view_summary_of_dependees(dependees, package)

    def set_the_package_version(self, package: str) -> str:
        """Set the version of the package.

        Args:
            package (str): Package name.
        """
        package_version = ''
        if self.data.get(package):
            package_version = self.data[package]['version']
        return package_version

    def find_requires(self, package: str) -> Generator[tuple[str, str], None, None]:
        """Find requires that package dependees.

        Args:
            package (str): Package name.

        Yields:
            Generator: List of names with requires.
        """
        for name, data in self.data.items():
            if package in data['requires']:
                yield name, data['requires']

    @staticmethod
    def view_no_dependees(dependees: dict[str, str]) -> None:
        """Print for no dependees.

        Args:
            dependees (dict[str, str]): Packages data.
        """
        if not dependees:
            print(f"{'':>1}No dependees")

    def view_the_main_package(self, package: str) -> None:
        """Print the main package.

        Args:
            package (str): Package name.
        """
        if self.option_for_pkg_version:
            pkgv: str = self.set_the_package_version(package)
            package = f'{package} {pkgv}'
        print(f'{self.bold}{package}:{self.endc}')

    def view_dependency_line(self, dependency: str) -> None:
        """Print the dependency line.

        Args:
            dependency (str): Name of dependency.
        """
        str_dependency: str = f"{'':>2}{dependency}"
        if self.option_for_full_reverse:
            str_dependency = f"{'':>2}{dependency}:"
        print(str_dependency)

    def view_dependees(self, dependees: dict[str, str]) -> None:
        """View packages that depend on.

        Args:
            dependees (dict): Packages data.
        """
        name_length: int = 0
        if dependees:
            name_length = max(len(name) for name in dependees.keys())
        for name, requires in dependees.items():
            dependency: str = name
            if self.option_for_pkg_version:
                pkgv: str = self.set_the_package_version(name)
                dependency = f'{name:<{name_length}} {pkgv}'

            self.view_dependency_line(dependency)

            if self.option_for_full_reverse:
                self.view_full_reverse(requires)

    def view_full_reverse(self, requires: str) -> None:
        """Print all packages.

        Args:
            requires (str): Package requires.
        """
        requires_version: list[str] = []
        if self.option_for_pkg_version:
            for req in requires:
                pkgv: str = self.set_the_package_version(req)
                if pkgv:
                    requires_version.append(f'{req}-{pkgv}')
            print(f"{'':>4}{', '.join(requires_version)}")
        else:
            print(f"{'':>4}{', '.join(requires)}")

    def view_summary_of_dependees(self, dependees: dict[str, str], package: str) -> None:
        """Print the summary.

        Args:
            dependees (dict[str, str]): Packages data.
            package (str): Package name.
        """
        print(f'\n{self.grey}{len(dependees)} dependees for {package}{self.endc}\n')

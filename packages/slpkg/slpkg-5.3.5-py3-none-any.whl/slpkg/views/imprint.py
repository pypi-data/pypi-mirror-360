#!/usr/bin/python3
# -*- coding: utf-8 -*-


import shutil
from dataclasses import dataclass

from slpkg.config import config_load


@dataclass
class PackageData:
    """
    Represents the package with its characteristics.

    Attributes:
        package (str): The name of the package.
        version (str): The package version.
        size (str): The size of the package (e.g., "10MB").
        color (str): A color code for displaying the package.
        repo (str): The repository where the package is located.
    """
    package: str
    version: str
    size: str
    color: str
    repo: str


class Imprint:  # pylint: disable=[R0902]
    """Managing the ASCII characters."""

    def __init__(self) -> None:  # pylint: disable=[R0915]
        self.bold = config_load.bold
        self.cyan = config_load.cyan
        self.endc = config_load.endc

        self.columns, self.rows = shutil.get_terminal_size()
        self.package_alignment: int = self.columns - 56
        self.version_alignment: int = 31
        self.size_alignment: int = 9
        self.repo_alignment: int = 14

        self.package_alignment = max(self.package_alignment, 1)

        self.bullet: str = '-'
        self.done: str = 'Done'
        self.failed: str = 'Failed'
        self.skipped: str = 'Skipped'

    def package_status(self, mode: str) -> None:
        """Print the package status."""
        print('=' * (self.columns - 1))
        print(f"{self.bold}{'Package':<{self.package_alignment}} {'Version':<{self.version_alignment}}{'Size':<{self.size_alignment}}{'Repository':>{self.repo_alignment}}{self.endc}")
        print('=' * (self.columns - 1))
        print(f'{self.bold}{mode}{self.endc}')

    def package_line(self, pkg: PackageData) -> None:
        """Draw the package line.

        Args:
            pkg (DrawPackage): Class of package characteristic.

        """
        if len(pkg.version) >= (self.version_alignment - 5):
            pkg.version = f'{pkg.version[:self.version_alignment - 5]}...'
        if len(pkg.package) >= (self.package_alignment - 4):
            pkg.package = f'{pkg.package[:self.package_alignment - 4]}...'

        print(f"{'':>1}{pkg.color}{pkg.package:<{self.package_alignment}}{self.endc}"
              f"{pkg.version:<{self.version_alignment}}{self.endc}{pkg.size:<{self.size_alignment}}"
              f"{pkg.repo:>{self.repo_alignment}}")

    def dependency_status(self, mode: str) -> None:
        """Draw the dependency line."""
        print(f"{self.bold}{mode} dependencies:{self.endc}")

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from slpkg.config import config_load
from slpkg.utilities import Utilities


class Check:
    """Some checks before proceed."""

    def __init__(self) -> None:
        self.red = config_load.red
        self.endc = config_load.endc
        self.utils = Utilities()

    def is_package_exists(self, packages: list[str], data: dict[str, dict[str, str]]) -> None:
        """Check if the package exist if not prints a message.

        Args:
            packages (list[str]): List of packages.
            data (dict[str, dict[str, str]]): Repository data.
        """
        not_packages: list[str] = []

        for pkg in packages:
            if not data.get(pkg) and pkg != '*':
                not_packages.append(pkg)

        if not_packages:
            print(f"{self.red}Error{self.endc}: Unable to find a match: {', '.join(not_packages)}")
            sys.exit(1)

    def is_package_installed(self, packages: list[str]) -> None:
        """Check for installed packages and prints message if not.

        Args:
            packages (list[str]): List of packages.
        """
        not_found: list[str] = []

        for pkg in packages:
            if not self.utils.is_package_installed(pkg):
                not_found.append(pkg)

        if not_found:
            print(f"{self.red}Error{self.endc}: Unable to find a match: {', '.join(not_found)}")
            sys.exit(1)

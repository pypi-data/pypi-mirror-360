#!/usr/bin/python3
# -*- coding: utf-8 -*-


from slpkg.config import config_load


class Version:  # pylint: disable=[R0903]
    """Print the version."""

    def __init__(self) -> None:
        self.version = '5.3.6'
        self.license = 'GNU General Public License v3 (GPLv3)'
        self.homepage = 'https://dslackw.gitlab.io/slpkg'
        self.arch = config_load.cpu_arch

    def view(self) -> None:
        """Print the version."""
        print(f'Version: {self.version} ({self.arch})\n'
              f'License: {self.license}\n'
              f'Homepage: {self.homepage}')

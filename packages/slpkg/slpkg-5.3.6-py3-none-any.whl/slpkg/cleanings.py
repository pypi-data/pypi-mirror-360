#!/usr/bin/python3
# -*- coding: utf-8 -*-


from slpkg.config import config_load
from slpkg.utilities import Utilities
from slpkg.views.views import View


class Cleanings:  # pylint: disable=[R0903,R0902]
    """Cleans the logs from packages."""

    def __init__(self) -> None:
        self.tmp_slpkg = config_load.tmp_slpkg
        self.build_path = config_load.build_path
        self.prog_name = config_load.prog_name
        self.bold = config_load.bold
        self.red = config_load.red
        self.endc = config_load.endc

        self.view = View()
        self.utils = Utilities()

    def tmp(self) -> None:
        """Delete files and folders in /tmp/slpkg/ folder."""
        print('Deleting of local data:\n')

        for file in self.tmp_slpkg.rglob('*'):
            print(f'{self.red}{self.endc} {file}')

        print(f"\n{self.prog_name}: {self.bold}{self.red}WARNING{self.endc}: All the files and "
              f"folders will delete!")

        self.view.question()

        self.utils.remove_folder_if_exists(self.tmp_slpkg)
        self.utils.create_directory(self.build_path)
        print('Successfully cleared!\n')

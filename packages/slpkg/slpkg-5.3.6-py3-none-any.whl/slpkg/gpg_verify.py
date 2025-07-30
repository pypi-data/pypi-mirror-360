#!/usr/bin/python3
# -*- coding: utf-8 -*-


import subprocess
from pathlib import Path

from slpkg.config import config_load
from slpkg.views.view_process import ViewProcess
from slpkg.views.views import View


class GPGVerify:  # pylint: disable=[R0903]
    """GPG verify files."""

    def __init__(self) -> None:
        self.gpg_verification = config_load.gpg_verification
        self.red = config_load.red
        self.endc = config_load.endc

        self.view = View()
        self.view_process = ViewProcess()

    def verify(self, asc_files: list[Path]) -> None:
        """Verify files with gpg tool.

        Args:
            asc_files (list[Path]): List of files.
        """
        if self.gpg_verification:
            output: dict[str, int] = {}
            gpg_command: str = 'gpg --verify'
            self.view_process.message('Verify files with GPG')

            for file in asc_files:
                with subprocess.Popen(f'{gpg_command} {file}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True) as process:
                    process.wait()

                    output[file.name] = process.returncode

            all_zero = all(value == 0 for value in output.values())
            if all_zero:
                self.view_process.done()
            else:
                self.view_process.failed()
                for filename, code in output.items():
                    if code != 0:
                        print(f"{self.red}Error{self.endc} {code}: {filename}")
                print()
                self.view.question()

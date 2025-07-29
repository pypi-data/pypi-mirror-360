#!/usr/bin/python3
# -*- coding: utf-8 -*-


import shutil
import subprocess
from datetime import datetime
from io import TextIOWrapper
from multiprocessing import Process
from typing import Optional

from slpkg.config import config_load
from slpkg.error_messages import Errors
from slpkg.progress_bar import ProgressBar
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint


class MultiProcess:  # pylint: disable=[R0902]
    """Create parallel process between progress bar and process."""

    def __init__(self, options: Optional[dict[str, bool]] = None) -> None:
        self.colors = config_load.colors
        self.progress_bar = config_load.progress_bar
        self.package_type = config_load.package_type
        self.log_packages = config_load.log_packages
        self.process_log = config_load.process_log
        self.slpkg_log_file = config_load.slpkg_log_file
        self.red = config_load.red
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.endc = config_load.endc

        self.utils = Utilities()
        self.progress = ProgressBar()
        self.imp = Imprint()
        self.errors = Errors()

        self.columns, self.rows = shutil.get_terminal_size()
        self.timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.head_message: str = f'Timestamp: {self.timestamp}'
        self.bottom_message: str = 'EOF - End of log file'

        if options is not None:
            self.option_for_reinstall: bool = options.get('option_reinstall', False)

    def process_and_log(self, command: str, filename: str, progress_message: str) -> None:
        """Start a multiprocessing process.

        Args:
            command (str): The command of process
            filename (str): The filename of process.
            progress_message (str): The message of progress.

        No Longer Returned:
            None.
        """
        pg_color: str = self.green
        if progress_message == 'Building':
            pg_color = self.yellow

        width: int = 11
        if progress_message == 'Removing':
            pg_color = self.red
            width = 9

        if self.progress_bar:
            skip: str = f'{self.yellow}{self.imp.skipped}{self.endc}'
            done: str = f'{self.green}{self.imp.done}{self.endc}'
            failed: str = f'{self.red}{self.imp.failed}{self.endc}'
            installed: str = ''

            if filename.endswith(tuple(self.package_type)) and not self.option_for_reinstall:
                installed_package = self.log_packages.glob(filename[:-4])
                for inst in installed_package:
                    if inst.name == filename[:-4]:
                        installed = filename[:-4]

            # Starting multiprocessing
            process_1 = Process(target=self._run, args=(command,))
            process_2 = Process(target=self.progress.progress_bar, args=(progress_message, filename))

            process_1.start()
            process_2.start()

            # Wait until process 1 finish
            process_1.join()

            # Terminate process 2 if process 1 finished
            if not process_1.is_alive():
                process_2.terminate()
                print(f"\r{' ' * (self.columns - 1)}", end='')  # Delete previous line.
                if process_1.exitcode != 0:
                    print(f"\r {pg_color}{progress_message:<{width}}{self.endc}: {filename} {failed}", end='')
                elif installed:
                    print(f"\r {pg_color}{progress_message:<{width}}{self.endc}: {filename} {skip}", end='')
                else:
                    print(f"\r {pg_color}{progress_message:<{width}}{self.endc}: {filename} {done}", end='')

            # Restore the terminal cursor
            print('\x1b[?25h', self.endc)
        else:
            self._run(command)

    def _run(self, command: str, stdout: Optional[int] = subprocess.PIPE,
             stderr: Optional[int] = subprocess.STDOUT) -> None:
        """Build the package and write a log file.

        Args:
            command (str): The command of process
            stdout (Optional[int], optional): Captured stdout from the child process.
            stderr (Optional[int], optional): Captured stderr from the child process.

        No Longer Returned:
            None.

        Raises:
            SystemExit: Description
        """
        with subprocess.Popen(command, shell=True, stdout=stdout, stderr=stderr, text=True) as process:

            self._write_log_head()

            # Write the process to the log file and to the terminal.
            if process.stdout:
                with process.stdout as output:
                    for line in output:
                        if not self.progress_bar:
                            print(line.strip())  # Print to console
                        if self.process_log:
                            with open(self.slpkg_log_file, 'a', encoding='utf-8') as log:
                                log.write(line)  # Write to log file

            self._write_log_eof()

            process.wait()  # Wait for the process to finish

            # If the process failed, return exit code.
            if process.returncode != 0:
                self._error_process()
                raise SystemExit(process.returncode)

    def _error_process(self) -> None:
        """Print error message for a process."""
        if not self.progress_bar:
            message: str = 'Error occurred with process. Please check the log file.'
            print()
            print(len(message) * '=')
            print(f'{self.red}{message}{self.endc}')
            print(len(message) * '=')
            print()

    def _write_log_head(self) -> None:
        """Write the timestamp at the head of the log file."""
        if self.process_log:
            with open(self.slpkg_log_file, 'a', encoding='utf-8') as log:
                log.write(f"{len(self.head_message) * '='}\n")
                log.write(f'{self.head_message}\n')
                log.write(f"{len(self.head_message) * '='}\n")

    def _write_log_eof(self) -> None:
        """Write the bottom of the log file."""
        if self.process_log:
            with open(self.slpkg_log_file, 'a', encoding='utf-8') as log:
                log.write(f"\n{len(self.bottom_message) * '='}\n")
                log.write(f'{self.bottom_message}\n')
                log.write(f"{len(self.bottom_message) * '='}\n\n")

    @staticmethod
    def process(command: str, stderr: Optional[TextIOWrapper] = None, stdout: Optional[TextIOWrapper] = None) -> None:
        """Run a command to the shell.

        Args:
            command (str): The command of process
            stderr (Optional[TextIOWrapper], optional): Captured stderr from the child process.
            stdout (Optional[TextIOWrapper], optional): Captured stdout from the child process.

        No Longer Returned:
            None.

        Raises:
            SystemExit: Description
        """
        try:
            output = subprocess.run(f'{command}', shell=True, stderr=stderr, stdout=stdout, check=False)
        except KeyboardInterrupt as e:
            raise SystemExit(1) from e

        if output.returncode != 0:
            if not command.startswith(('wget', 'wget2', 'curl', 'lftp', 'aria2c')):
                raise SystemExit(output.returncode)

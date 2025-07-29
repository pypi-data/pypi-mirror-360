#!/usr/bin/python3
# -*- coding: utf-8 -*-


import time
from typing import Any

from slpkg.config import config_load
from slpkg.views.imprint import Imprint


class ProgressBar:  # pylint: disable=[R0902]
    """Progress spinner bar."""

    def __init__(self) -> None:
        self.progress_spinner = config_load.progress_spinner
        self.colors = config_load.colors
        self.spinner_color = config_load.spinner_color
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.cyan = config_load.cyan
        self.grey = config_load.grey
        self.red = config_load.red
        self.endc = config_load.endc

        self.imp = Imprint()

        self.color = self.endc
        self.spinners: dict[str, Any] = {}
        self.spinners_color: dict[str, str] = {}
        self.spinner = ''
        self.bar_message = ''

    def progress_bar(self, message: str, filename: str = '') -> None:
        """Create the progress bar."""
        self.assign_spinner_chars()
        self.set_spinner()
        self.assign_spinner_colors()
        self.set_color()
        self.set_the_spinner_message(str(filename), message)
        print('\x1b[?25l', end='')  # Hide cursor before starting

        current_state = 0  # Index of the current state
        try:
            while True:
                print(f"\r{self.bar_message}{self.color}{self.spinner[current_state]}{self.endc}", end="")
                time.sleep(0.1)
                current_state = (current_state + 1) % len(self.spinner)
        except KeyboardInterrupt as e:
            print('\x1b[?25h', end='')
            raise SystemExit(1) from e

    def assign_spinner_colors(self) -> None:
        """Assign spinner colors."""
        self.spinners_color = {
            'green': self.green,
            'yellow': self.yellow,
            'cyan': self.cyan,
            'grey': self.grey,
            'red': self.red,
            'white': self.endc
        }

    def assign_spinner_chars(self) -> None:
        """Assign for characters."""
        self.spinners = {
            'spinner': ('-', '\\', '|', '/'),
            'pie': ('◷', '◶', '◵', '◴'),
            'moon': ('◑', '◒', '◐', '◓'),
            'line': ('⎺', '⎻', '⎼', '⎽', '⎼', '⎻'),
            'pixel': ('⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽'),
            'ball': ('_', '.', '|', 'o'),
            'clock': ('🕛', '🕑', '🕒', '🕔', '🕧', '🕗', '🕘', '🕚')
        }

    def set_the_spinner_message(self, filename: str, message: str) -> None:
        """Set message to the spinner.

        Args:
            filename (str): Name of file.
            message (str): The progress bar message.
        """
        width: int = 11
        if message == 'Removing':
            width = 9

        self.bar_message = f'{message}... '
        if filename:
            self.bar_message = f' {message:<{width}}{self.endc}: {filename} '

    def set_spinner(self) -> None:
        """Spanners characters."""
        try:
            self.spinner = self.spinners[self.progress_spinner]
        except KeyError:
            self.spinner = self.spinners['spinner']

    def set_color(self) -> None:
        """Set the spinner color."""
        try:
            self.color = self.spinners_color[self.spinner_color]
        except KeyError:
            self.color = self.endc

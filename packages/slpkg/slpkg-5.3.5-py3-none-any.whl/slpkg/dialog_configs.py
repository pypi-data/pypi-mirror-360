#!/usr/bin/python3
# -*- coding: utf-8 -*-


import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import tomlkit

from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.error_messages import Errors


class FormConfigs:  # pylint: disable=[R0902]
    """Edit slpkg.toml config file with dialog utility."""

    def __init__(self) -> None:
        self.dialog = config_load.dialog
        self.etc_path = config_load.etc_path
        self.prog_name = config_load.prog_name
        self.config = config_load.config

        self.dialogbox = DialogBox()
        self.errors = Errors()

        self.original_configs: dict[str, dict[str, Any]] = {}
        self.config_file: Path = Path(self.etc_path, f'{self.prog_name}.toml')

    def is_dialog_enabled(self) -> None:
        """Check if the dialog box is enabled by the user."""
        if not self.dialog:
            editor = os.environ.get('EDITOR', '')
            command = [editor, f'{self.etc_path}/slpkg.toml']
            subprocess.run(command, check=True)
            sys.exit(0)

    def edit(self) -> None:
        """Read and write the configuration file."""
        self.is_dialog_enabled()
        elements: list[Any] = []
        height: int = 0
        width: int = 0
        form_height: int = 0
        text: str = f'Edit the configuration file: {self.config_file}'
        title: str = ' Configuration File '

        # Creating the elements for the dialog form.
        for i, (key, value) in enumerate(self.config.items(), start=1):
            if value is True:  # type: ignore
                value = 'true'
            elif value is False:  # type: ignore
                value = 'false'
            elements.extend(
                [(key, i, 1, str(value), i, 21, 47, 200, '0x0', f'Config: {key} = {value}')]
            )

        code, tags = self.dialogbox.mixedform(text, title, elements, height, width, form_height)

        os.system('clear')

        if code == 'help':  # type: ignore
            self.help()

        if code == 'ok':  # type: ignore
            self.write_configs(tags)

    def help(self) -> None:
        """Load the configuration file on a text box."""
        self.dialogbox.textbox(str(self.config_file), 40, 60)
        self.edit()

    def read_configs(self) -> None:
        """Read the original config file."""
        with open(self.config_file, 'r', encoding='utf-8') as file:
            self.original_configs = tomlkit.parse(file.read())

    def write_configs(self, tags: list[str]) -> None:
        """Write new configs to the file.

        Args:
            tags (list[str]): User new configs.
        """
        self.read_configs()
        new: Any
        for key, new in zip(self.original_configs['CONFIGS'], tags):
            digit_pattern = re.compile(r"^-?\d+(\.\d+)?$")  # pattern for int and float numbers.
            list_pattern = re.compile(r'^\s*\[.*\]\s*$')  # pattern for list.

            if new == 'true':
                new = True
            elif new == 'false':
                new = False
            elif digit_pattern.match(new):
                if new.isdigit():
                    new = int(new.replace('"', ''))
                else:
                    new = float(new.replace('"', ''))
            elif list_pattern.match(new):
                try:
                    new = ast.literal_eval(new)
                except (SyntaxError, ValueError, TypeError):
                    self.errors.raise_error_message('Error parsing config file', 1)

            self.original_configs['CONFIGS'][key] = new

        with open(self.config_file, 'w', encoding='utf-8') as file:
            file.write(tomlkit.dumps(self.original_configs))

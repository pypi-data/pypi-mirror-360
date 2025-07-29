#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from typing import Any

from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.terminal_selector import TerminalSelector
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess


class ChooseDependencies:  # pylint: disable=[R0902,R0903]
    """
    Choose dependencies with dialog or with terminal selector.
    """

    def __init__(self, repository: str, data: dict[str, dict[str, str]], options: dict[str, bool], mode: str) -> None:
        self.repository = repository
        self.data = data
        self.mode = mode

        self.dialog = config_load.dialog

        self.upgrade = Upgrade(repository, data)
        self.utils = Utilities()
        self.dialogbox = DialogBox()

        self.option_for_reinstall: bool = options.get('option_reinstall', False)

    def choose(self, dependencies: list[str], view_process: ViewProcess) -> list[str]:  # pylint: disable=[R0914]
        """Choose dependencies for install with dialog tool or terminal selector."""
        if dependencies:
            choices: list[Any] = []
            initial_selection: list[int] = []
            is_upgrade = False
            height: int = 10
            width: int = 70
            list_height: int = 0
            title: str = ' Choose dependencies you want to install '

            for package in dependencies:
                status: bool = True
                repo_ver: str = self.data[package]['version']
                description: str = self.data[package]['description']
                help_text: str = f'Description: {description}'
                installed: str = self.utils.is_package_installed(package)
                upgradeable: bool = self.upgrade.is_package_upgradeable(installed)

                if installed:
                    status = False

                if self.mode == 'upgrade' and upgradeable:
                    status = True

                if self.option_for_reinstall:
                    status = True

                if status:
                    initial_selection.append(1)
                else:
                    initial_selection.append(0)

                choices.extend(
                    [(package, repo_ver, status, help_text)]
                )

            view_process.done()

            if self.dialog:
                text: str = f'There are {len(choices)} dependencies:'
                code, dependencies = self.dialogbox.checklist(text, title, height, width, list_height, choices)  # pylint: disable=[W0612]

                os.system('clear')
            else:
                if self.mode == 'upgrade':
                    is_upgrade = True

                terminal_selector = TerminalSelector(dependencies, title, self.data, is_upgrade, initial_selection)
                dependencies = terminal_selector.select()

        return dependencies

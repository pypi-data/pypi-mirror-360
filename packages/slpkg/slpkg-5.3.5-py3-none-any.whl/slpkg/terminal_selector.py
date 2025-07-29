#!/usr/bin/python3
# -*- coding: utf-8 -*-

import shutil
import sys
import termios
import tty
from typing import Union

from slpkg.config import config_load
from slpkg.utilities import Utilities


class TerminalSelector:  # pylint: disable=[R0902,R0903]
    """
    A class for interactive multi-selection in the terminal using arrow keys and spacebar.
    Supports Unix-like systems only.
    """

    def __init__(self, items: list[str], title: str, data: dict[str, dict[str, str]], is_upgrade: bool, initial_selection: Union[list[int], str, None] = None):  # pylint: disable=[R0912,R0913,R0917]
        """
        Initializes the TerminalSelector with a list of items and an optional initial selection.

        Args:
            initial_selection (list | str): Initial selection string or list of integers.
            items (list): A list of strings to be displayed and selected.
            title (str): The title of the operation.
            data (dict[str, dict[str, str]]): The data of the packages.
            is_upgrade (bool): Whether the command is for upgrade.
        """
        self.data = data
        self.is_upgrade = is_upgrade
        self.title = title.strip()
        self.initial_selection = initial_selection

        self.terminal_selector = config_load.terminal_selector
        self.bold = config_load.bold
        self.back_white = config_load.back_white
        self.black = config_load.black
        self.hg = f'{self.back_white}{self.black}{self.bold}'
        self.endc = config_load.endc
        self.colors = config_load.colors
        self.columns, self.rows = shutil.get_terminal_size()

        self.utils = Utilities()

        if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
            raise TypeError('Items must be a list of strings.')
        if not items:
            self._items: list[str] = []
        else:
            self._items = items

        self._selected_indices: set[int] = set()
        self._current_selection_index = 0
        self._num_items = len(self._items)
        self.longest_name: int = len(max(self._items, key=len))

        # --- Handle initial_selection ---
        if initial_selection == "all":
            self._selected_indices = set(range(self._num_items))
        elif isinstance(initial_selection, list):
            # Validate indices and add to selected_indices
            for i, status_flag in enumerate(initial_selection[:self._num_items]):
                if status_flag == 1:
                    self._selected_indices.add(i)
        # If initial_selection is "none" or anything else, _selected_indices remains empty as initialized.

        # Number of lines printed for instructions and borders
        self._header_lines: int = 3  # Instructions (3) + top border (1)
        self._footer_lines: int = 0  # Bottom border (1)

    def _repo_pkg_version(self, package: str) -> str:
        """Returns the package version of the repository package.

        Args:
            package: The name of the package.

        Returns:
            Repository package version.
        """
        version: str = self.data[package]['version']
        return version

    def _installed_pkg_name(self, package: str) -> str:
        """Returns the name of the installed package.

        Args:
            package: The name of the package.

        Returns:
            Name of the installed package.
        """
        installed: str = self.utils.is_package_installed(package)
        return installed

    def _installed_pkg_version(self, package: str) -> str:
        """Returns the installed version of the package.

        Args:
            package: The name of the package.

        Returns:
            Version of the package.
        """
        package_name: str = self._installed_pkg_name(package)
        if package_name:
            version: str = self.utils.split_package(package_name)['version']
            return version
        return ''

    def _repo_pkg_build(self, package: str) -> str:
        """Returns the build number of the repository package.

        Args:
            package: The name of the package.

        Returns:
            The build number.
        """
        build: str = self.data[package]['build']
        return build

    def _installed_pkg_build(self, package: str) -> str:
        """Returns the build number of installed package.

        Args:
            package: The name of the package.

        Returns:
            Build number of installed package.
        """
        installed: str = self._installed_pkg_name(package)
        if installed:
            build: str = self.utils.split_package(installed)['build']
            return build
        return ''

    # def _display_info_line(self, message: str) -> None:
    #     """
    #     Displays a dynamic info message at the bottom of the selection list.
    #     """
    #     # Calculate how many lines down to move from the current item
    #     lines_to_move_down = (self._num_items - 1 - self._current_selection_index) + 2  # +1 for the line below the last item
    #
    #     sys.stdout.write('\033[s')  # Save current cursor position
    #     self._move_cursor_down(lines_to_move_down)  # Move cursor to the line below the list
    #     sys.stdout.write('\r')  # Go to beginning of line
    #     self._erase_line()  # Erase previous info message
    #     sys.stdout.write(message)  # Print the new message
    #     sys.stdout.write('\033[u')  # Restore cursor position

    @staticmethod
    def _get_char() -> str:
        """Reads a single character from stdin without waiting for Enter."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    @staticmethod
    def _move_cursor_up(lines: int = 1) -> None:
        """Moves the cursor up N lines using ANSI escape codes."""
        sys.stdout.write(f'\033[{lines}A')
        sys.stdout.flush()

    @staticmethod
    def _move_cursor_down(lines: int = 1) -> None:
        """Moves the cursor down N lines using ANSI escape codes."""
        sys.stdout.write(f'\033[{lines}B')
        sys.stdout.flush()

    @staticmethod
    def _move_cursor_to_col(col: int = 0) -> None:
        """Moves the cursor to a specific column on the current line (0-indexed)."""
        sys.stdout.write(f'\r\033[{col}C')  # \r moves to start of line, then move right
        sys.stdout.flush()

    @staticmethod
    def _erase_line() -> None:
        """Erases the current line from the cursor position to the end."""
        sys.stdout.write('\033[K')
        sys.stdout.flush()

    @staticmethod
    def _hide_cursor() -> None:
        """Hides the terminal cursor using ANSI escape codes."""
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

    @staticmethod
    def _show_cursor() -> None:
        """Shows the terminal cursor using ANSI escape codes."""
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

    def _redraw_current_item(self) -> None:
        """
        Redraws the line of the currently selected item,
        updating its prefix (">" or " ") and checkbox state.
        Assumes cursor is already on the correct line.
        """
        # Save cursor position before updating a line
        sys.stdout.write('\033[s')

        sys.stdout.write('\r')  # Go to beginning of current line

        prefix: str = ''
        if not self.colors:
            prefix = '>'  # This item IS the current selection
        checkbox: str = ' [*]' if self._current_selection_index in self._selected_indices else ' [ ]'

        package = self._items[self._current_selection_index]
        if self.is_upgrade:
            installed: str = self._installed_pkg_version(package)
            repo_pkg_version: str = self._repo_pkg_version(package)
            repo_build: str = self._repo_pkg_build(package)
            installed_build: str = self._installed_pkg_build(package)
            sys.stdout.write(f'{prefix}{checkbox} {self.hg}{package:<{self.longest_name}} {installed} ({installed_build})'
                             f' -> {repo_pkg_version} ({repo_build}){self.endc}')
        else:
            sys.stdout.write(f'{prefix}{checkbox} {self.hg}{package}{self.endc}')
        self._erase_line()  # Erase any leftover characters

        # Restore cursor position (to the start of the current selection line)
        sys.stdout.write('\033[u')

    def _cleanup_previous_item(self, old_index: int) -> None:
        """
        Removes the '>' prefix from a previously highlighted item.
        Assumes cursor is on the line of the old_index item.
        """
        sys.stdout.write('\033[s')  # Save current cursor position
        sys.stdout.write('\r')  # Go to beginning of current line

        old_prefix: str = ''
        if not self.colors:
            old_prefix = ' '  # It's no longer highlighted

        old_checkbox: str = ' [*]' if old_index in self._selected_indices else ' [ ]'

        package = self._items[self._current_selection_index]
        if self.is_upgrade:
            installed: str = self._installed_pkg_version(package)
            repo_pkg_version: str = self._repo_pkg_version(package)
            repo_build: str = self._repo_pkg_build(package)
            installed_build: str = self._installed_pkg_build(package)
            sys.stdout.write(f'{old_prefix}{old_checkbox} {package:<{self.longest_name}} {installed} ({installed_build})'
                             f' -> {repo_pkg_version} ({repo_build})')
        else:
            sys.stdout.write(f'{old_prefix}{old_checkbox} {package}')
        self._erase_line()
        sys.stdout.write('\033[u')  # Restore cursor position

    def select(self) -> list[str]:  # pylint: disable=[R0912,R0915]
        """
        Starts the interactive selection process.

        Returns:
            list: A list of selected items (strings), or an empty list if nothing was selected
                  or the process was cancelled.
        """
        if not self._items:
            return []

        if not self.terminal_selector or len(self._items) < 2:
            return self._items

        self._hide_cursor()

        try:
            print(f'{self.title}:')

            # Print initial list
            for i, item_display in enumerate(self._items):
                # We need to correctly show the initial checkbox state here
                prefix: str = ''
                if not self.colors:
                    prefix = '>' if i == self._current_selection_index else ' '
                checkbox: str = ' [*]' if i in self._selected_indices else ' [ ]'  # Check initial selection

                if self.is_upgrade:
                    installed: str = self._installed_pkg_version(item_display)
                    repo_pkg_version: str = self._repo_pkg_version(item_display)
                    repo_build: str = self._repo_pkg_build(item_display)
                    installed_build: str = self._installed_pkg_build(item_display)
                    print(f'{prefix}{checkbox} {item_display:<{self.longest_name}} {installed} ({installed_build})'
                          f' -> {repo_pkg_version} ({repo_build})')
                else:
                    print(f'{prefix}{checkbox} {item_display}')

            # Position cursor back at the first selectable item
            # Moves up from the end of the list: footer_lines + num_items lines
            self._move_cursor_up(self._footer_lines + self._num_items)

            while True:
                # Feature to display information for current selection.
                # desc = self.data[self._items[self._current_selection_index]]['description']
                # self._display_info_line(desc)

                # Always ensure the current item is drawn correctly
                self._redraw_current_item()

                char: str = self._get_char()

                if char == '\x1b':  # ASCII escape sequence start for arrow keys
                    char += self._get_char()  # Read '['
                    char += self._get_char()  # Read 'A', 'B', etc.

                    # Clean up previous highlighted item BEFORE moving the cursor
                    self._cleanup_previous_item(self._current_selection_index)

                    if char == '\x1b[A':  # Up arrow
                        if self._current_selection_index > 0:
                            self._move_cursor_up(1)  # Move cursor up one line
                            self._current_selection_index -= 1
                    elif char == '\x1b[B':  # Down arrow
                        if self._current_selection_index < self._num_items - 1:
                            self._move_cursor_down(1)  # Move cursor down one line
                            self._current_selection_index += 1
                    elif char == '\x1b[5':  # Page Up
                        # Calculate the new index, ensuring it doesn't go below 0
                        new_index = max(0, self._current_selection_index - self.rows)
                        lines_to_move = self._current_selection_index - new_index
                        if lines_to_move > 0:
                            self._move_cursor_up(lines_to_move)
                            self._current_selection_index = new_index
                    elif char == '\x1b[6':  # Page Down
                        # Calculate the new index, ensuring it doesn't exceed _num_items - 1
                        new_index = min(self._num_items - 1, self._current_selection_index + self.rows)
                        lines_to_move = new_index - self._current_selection_index
                        if lines_to_move > 0:
                            self._move_cursor_down(lines_to_move)
                            self._current_selection_index = new_index

                elif char == ' ':  # Spacebar for select/deselect
                    if self._current_selection_index in self._selected_indices:
                        self._selected_indices.remove(self._current_selection_index)
                    else:
                        self._selected_indices.add(self._current_selection_index)
                    # _redraw_current_item will handle the visual update of the checkbox

                elif char in ('\r', '\n'):  # Enter key to finalize selection
                    # Move cursor past the list to allow for final output
                    lines_to_move_down = (self._num_items - 1 - self._current_selection_index) + self._footer_lines + 1
                    self._move_cursor_down(lines_to_move_down)
                    print('')  # New line to ensure output appears below list

                    # Convert selected indices back to names, maintaining original order
                    final_selection: list[str] = [self._items[i] for i in sorted(self._selected_indices)]
                    break  # Exit the loop

                elif char in ('\x03', 'q', 'Q'):  # Ctrl+C or q for quit.
                    # Move cursor past the list before printing cancellation message
                    lines_to_move_down = (self._num_items - 1 - self._current_selection_index) + self._footer_lines + 1
                    self._move_cursor_down(lines_to_move_down)
                    print('\nSelection cancelled.')
                    sys.exit(1)  # Exit the loop

                # For any other key, do nothing or handle as needed

        finally:
            self._show_cursor()  # Always show cursor when done

        return final_selection

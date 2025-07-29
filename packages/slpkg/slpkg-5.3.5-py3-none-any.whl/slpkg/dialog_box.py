#!/usr/bin/python3
# -*- coding: utf-8 -*-


import locale
from pathlib import Path
from typing import Any, Tuple, Union

try:
    from dialog import Dialog

    DIALOG_AVAILABLE = True
except ModuleNotFoundError:
    DIALOG_AVAILABLE = False

from slpkg.config import config_load
from slpkg.views.version import Version

locale.setlocale(locale.LC_ALL, '')


class DialogBox:
    """Class for dialog box."""

    def __init__(self) -> None:
        self.prog_name = config_load.prog_name
        self.more_kwargs: dict[str, bool] = {}

        if DIALOG_AVAILABLE:
            self.d = Dialog(dialog="dialog")
            self.d.add_persistent_args(["--colors"])
            self.d.set_background_title(f'{self.prog_name} {Version().version} - Software Package Manager')
        else:
            self.d = None

    def checklist(self, text: str, title: str, height: int, width: int, list_height: int, choices: list[tuple[Any, ...]]) -> Tuple[str, list[str]]:  # pylint: disable=[R0913, R0917]
        """Display a checklist box.

        Args:
            text (str): Text to display in the box.
            title (str): Title of checklist.
            height (int): Height of the box.
            width (int): Width of the box.
            list_height (int): Number of entries displayed in the box at a given time (the contents can be scrolled).
            choices (list[str]): An iterable of (tag, item, status) tuples where status specifies the initial
                                 selected/unselected state of each entry; can be True or False, 1 or 0, "on" or
                                 "off" (True, 1 and "on" meaning selected), or any case variation of these two strings.

        Returns:
            Tuple[str, list]: a tuple of the form (code, [tag, ...]) whose first element is a Dialog exit code and
                              second element lists all tags for the entries selected by the user.
                              If the user exits with Esc or Cancel, the returned tag list is empty.
        """
        self.more_kwargs.update(
            {"item_help": True}
        )

        code, tags = self.d.checklist(text=text, choices=choices, title=title, height=height, width=width,
                                      # pylint: disable=[R0913, R0917]
                                      list_height=list_height, help_status=True, **self.more_kwargs)

        return code, tags

    def mixedform(self, text: str, title: str, elements: list[str], height: int, width: int, form_height: int) -> Tuple[
        bool, list[str]]:  # pylint: disable=[R0913, R0917]
        """Display a mixedform box.

        Args:
            text (str): Text to display in the box.
            title (str): Title of box.
            elements (list[str]): Sequence describing the labels and fields.
            height (int): Height of the box.
            width (int): Width of the box.
            form_height (int): Number of form lines displayed at the same time.

        Returns:
            Tuple[bool, list]: a tuple of the form (code, list) where:
                               - code is a Dialog exit code;
                               - list gives the contents of every field on exit, with the same order as in elements.
        """
        self.more_kwargs.update(
            {"item_help": True,
             "help_tags": True}
        )
        code, tags = self.d.mixedform(text=text, title=title, elements=elements,
                                      height=height, width=width, form_height=form_height, help_button=True,
                                      help_status=True, **self.more_kwargs)

        return code, tags

    def msgbox(self, text: str, height: int, width: int) -> None:
        """Display a message box.

        Args:
            text (str): Text to display in the box.
            height (int): Height of the box.
            width (int): Width of the box.
        """
        self.d.msgbox(text, height, width)

    def textbox(self, text: Union[str, Path], height: int, width: int) -> None:
        """Display a text box.

        Args:
            text (Union[str, Path]): Text to display in the box.
            height (int): Height of the box.
            width (int): Width of the box.
        """
        self.d.textbox(text, height, width)

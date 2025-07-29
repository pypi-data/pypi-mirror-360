#!/usr/bin/python3
# -*- coding: utf-8 -*-


from slpkg.config import config_load


class Errors:  # pylint: disable=[R0903]
    """Raise an error message."""

    def __init__(self) -> None:
        self.prog_name = config_load.prog_name
        self.red = config_load.red
        self.endc = config_load.endc

    def raise_error_message(self, message: str, exit_status: int) -> None:
        """General method to raise an error message and exit.

        Args:
            message (str): Str message.
            exit_status (int): Exit status code.

        Raises:
            SystemExit: Description
        """
        print(f"\n{self.prog_name}: {self.red}Error{self.endc}: {message}\n")
        raise SystemExit(exit_status)

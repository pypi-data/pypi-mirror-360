#!/usr/bin/python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional, Union
from urllib.parse import unquote

from slpkg.config import config_load
from slpkg.error_messages import Errors
from slpkg.views.views import View


class Md5sum:
    """Checksum the file sources."""

    def __init__(self, options: dict[str, bool]) -> None:
        self.checksum_md5 = config_load.checksum_md5

        self.errors = Errors()
        self.view = View(options)

    def md5sum(self, path: Union[str, Path], source: str, checksum: str) -> None:
        """Checksum the source file.

        Args:
            path (Union[str, Path]): Path to source file.
            source (str): Source file.
            checksum (str): Expected checksum.
        """
        if self.checksum_md5:
            source_file = unquote(source)
            name = source_file.split('/')[-1]
            filename = Path(path, name)

            md5: Optional[bytes] = self.read_binary_file(filename)
            file_check: str = hashlib.md5(md5 or b'').hexdigest()
            checksum = "".join(checksum)

            if file_check != checksum:
                print(f'FAILED: MD5SUM check for {name}')
                print(f'Expected: {checksum}')
                print(f'Found: {file_check}')
                self.view.question()

    def read_binary_file(self, filename: Path) -> bytes:
        """Read the file source.

        Args:
            filename (Path): File name.

        Returns:
            bytes: Binary bytes.
        """
        try:
            with open(filename, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            self.errors.raise_error_message(f"No such file or directory: '{filename}'", exit_status=20)
        return b''

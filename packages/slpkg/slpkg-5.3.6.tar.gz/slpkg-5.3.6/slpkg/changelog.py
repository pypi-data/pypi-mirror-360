#!/usr/bin/python3
# -*- coding: utf-8 -*-

import shutil
import sys
from pathlib import Path

from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities


class Changelog:  # pylint: disable=[R0903]

    """Manages and prints changelog information for specified repositories.

    This class handles the retrieval and display of changelog entries.
    It allows filtering changelog content based on a user-provided query
    and includes terminal-based pagination for large outputs.
    """

    def __init__(self) -> None:
        self.repos = Repositories()
        self.utils = Utilities()
        self.columns, self.rows = shutil.get_terminal_size()

    def changelog(self, query: str, repository: str) -> None:
        """Prints repository changelog.
        """
        days: tuple[str, str, str, str, str, str, str] = ('Mon ', 'Tue ', 'Wed ', 'Thu ', 'Fri ', 'Sat ', 'Sun ')
        back_white: str = config_load.back_white
        black: str = config_load.black
        green: str = config_load.green
        endc: str = config_load.endc
        repo_path: Path = self.repos.repositories[repository]['path']
        changelog_txt: str = self.repos.repositories[repository]['changelog_txt']

        changelog_file: Path = Path(repo_path, changelog_txt)
        row: int = 1
        for line in self.utils.read_text_file(changelog_file):
            if query in line:

                if any(day in line for day in days):
                    line = f'{green}{line}{endc}'

                row += 1
                print(line, end='')
                if (row % (self.rows - 1)) == 0:
                    user_input: str = input(f'{back_white}{black}[-- More --] Press Enter to continue, q to quit:{endc}')
                    if user_input.lower() in ['q', 'quit', ]:
                        print('Operation aborted by the user.')
                        sys.exit(0)

#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
from pathlib import Path
from typing import Any

from slpkg.blacklist import Blacklist
from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess


class LoadData:  # pylint: disable=[R0902]
    """Reads data form json file and load to dictionary."""

    def __init__(self) -> None:
        self.cyan = config_load.cyan
        self.green = config_load.green
        self.red = config_load.red
        self.endc = config_load.endc

        self.repos = Repositories()
        self.utils = Utilities()
        self.black = Blacklist()
        self.view_process = ViewProcess()

    def load(self, repository: str, message: bool = True) -> dict[str, dict[str, str]]:
        """Load data to the dictionary.

        Args:
            repository (str): Repository name.
            message (bool, optional): Prints or not progress message.

        Returns:
            dict[str, dict[str, str]]: Dictionary data.
        """
        self.is_database_exist(repository)

        if message:
            self.view_process.message('Database loading')

        data: dict[Any, Any] = {}
        if repository == '*':
            for repo, value in self.repos.repositories.items():
                if value['enable']:  # Check if the repository is enabled
                    json_data_file: Path = Path(value['path'], self.repos.data_json)
                    data[repo] = self.read_data_file(json_data_file)
        else:
            json_data_file = Path(self.repos.repositories[repository]['path'], self.repos.data_json)

            data = self.read_data_file(json_data_file)

        blacklist: tuple[str, ...] = tuple(self.black.packages())
        if blacklist:
            if repository == '*':
                self._remove_blacklist_from_all_repos(data)
            else:
                self._remove_blacklist_from_a_repo(data)

        if message:
            self.view_process.done()

        return data

    def is_database_exist(self, repository: str) -> None:
        """Check if database data.json exist.

        Args:
            repository (str): Name of repository.

        Raises:
            SystemExit: Raise exit code.
        """
        if repository == '*':
            for repo, value in self.repos.repositories.items():
                if value['enable']:  # Check if the repository is enabled
                    json_data_file: Path = Path(value['path'], self.repos.data_json)
                    self._error_database(json_data_file, repo)
        else:
            json_data_file = Path(self.repos.repositories[repository]['path'], self.repos.data_json)
            self._error_database(json_data_file, repository)

    def _error_database(self, json_data_file: Path, repository: str) -> None:
        """Print error for database.

        Args:
            json_data_file (Path): Name of data.json file.

        Raises:
            SystemExit: Raise system exit error.
        """
        if not json_data_file.is_file():
            print(f'\nRepository: {repository}')
            print(f'\n{self.red}Error{self.endc}: File {json_data_file} not found!')
            print('\nNeed to update the database first, please run:\n')
            print(f"{'':>2} $ {self.green}slpkg update{self.endc}\n")
            raise SystemExit(1)

    @staticmethod
    def read_data_file(file: Path) -> dict[str, str]:
        """Read JSON data from the file.

        Args:
            file (Path): Path file for reading.

        Returns:
            dict[str, str]

        Raises:
            SystemExit: Description
        """
        json_data: dict[str, str] = {}
        try:
            json_data = json.loads(file.read_text(encoding='utf-8'))
        except json.decoder.JSONDecodeError:
            pass
        return json_data

    def _remove_blacklist_from_all_repos(self, data: dict[str, Any]) -> dict[str, str]:
        """Remove blacklist packages from all repositories.

        Args:
            data (dict[str, Any]): Repository data.

        Returns:
            dict[str, str]
        """
        # Remove blacklist packages from keys.
        for name, repo in data.items():
            blacklist_packages: list[str] = self.utils.ignore_packages(list(data[name].keys()))
            for pkg in blacklist_packages:
                if pkg in data[name].keys():
                    del data[name][pkg]

        # Remove blacklist packages from dependencies (values).
        for name, repo in data.items():
            blacklist_packages = self.utils.ignore_packages(list(data[name].keys()))
            for pkg, dep in repo.items():
                deps: list[str] = dep['requires']
                for blk in blacklist_packages:
                    if blk in deps:
                        deps.remove(blk)
                        data[name][pkg]['requires'] = deps
        return data

    def _remove_blacklist_from_a_repo(self, data: dict[str, Any]) -> dict[str, str]:
        """Remove blacklist from a repository.

        Args:
            data (dict[str, Any]): Repository data.

        Returns:
            dict[str, str]
        """
        blacklist_packages: list[str] = self.utils.ignore_packages(list(data.keys()))
        # Remove blacklist packages from keys.
        for pkg in blacklist_packages:
            if pkg in data.keys():
                del data[pkg]

        # Remove blacklist packages from dependencies (values).
        for pkg, dep in data.items():
            deps: list[str] = dep['requires']
            for blk in blacklist_packages:
                if blk in deps:
                    deps.remove(blk)
                    data[pkg]['requires'] = deps
        return data

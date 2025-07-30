#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
from multiprocessing import Process, Queue
from pathlib import Path
from typing import Optional

from urllib3 import PoolManager, ProxyManager, make_headers
from urllib3.exceptions import HTTPError, NewConnectionError

from slpkg.config import config_load
from slpkg.progress_bar import ProgressBar
from slpkg.repo_info import RepoInfo
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint


class CheckUpdates:  # pylint: disable=[R0902]
    """Checks for changes in the ChangeLog files."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        self.options = options
        self.repository = repository

        self.urllib_timeout = config_load.urllib_timeout
        self.proxy_username = config_load.proxy_username
        self.proxy_password = config_load.proxy_password
        self.proxy_address = config_load.proxy_address
        self.urllib_retries = config_load.urllib_retries
        self.urllib_timeout = config_load.urllib_timeout
        self.urllib_redirect = config_load.urllib_redirect
        self.green = config_load.green
        self.endc = config_load.endc

        self.utils = Utilities()
        self.progress = ProgressBar()
        self.repos = Repositories()
        self.repo_info = RepoInfo(options, repository)
        self.imp = Imprint()

        self.compare: dict[str, bool] = {}
        self.error_connected: list[str] = []

        self.http = PoolManager(timeout=self.urllib_timeout)
        self.proxy_default_headers = make_headers(
            proxy_basic_auth=f'{self.proxy_username}:{self.proxy_password}')

        self.option_for_repository: bool = options.get('option_repository', False)
        self.option_for_check: bool = options.get('option_check', False)

    def check_the_repositories(self, queue: Optional[Queue]) -> None:  # type: ignore
        """Save checks to a dictionary.

        Args:
            queue (Optional[Queue]): Puts attributes to the queue.
        """
        if self.option_for_repository:
            self.save_the_compares(self.repository)
        else:
            for repo, enable in self.repos.repositories.items():
                if enable['enable']:
                    self.save_the_compares(repo)

        if queue is not None:
            queue.put(self.compare)
            queue.put(self.error_connected)

    def save_the_compares(self, repo: str) -> None:
        """Save compares to a dictionary.

        Args:
            repo (str): Repository name.
        """
        local_chg_txt: Path = Path(
            self.repos.repositories[repo]['path'],
            self.repos.repositories[repo]['changelog_txt']
        )

        repo_chg_txt: str = (
            f"{self.repos.repositories[repo]['mirror_changelog']}"
            f"{self.repos.repositories[repo]['changelog_txt']}"
        )
        repo_data_file: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.data_json)

        if not repo_data_file.is_file():
            self.compare[repo] = True
        else:
            self.compare[repo] = self.compare_the_changelogs(
                local_chg_txt, repo_chg_txt)

    def compare_the_changelogs(self, local_chg_txt: Path, repo_chg_txt: str) -> bool:
        """Compare the two ChangeLog files for changes.

        Args:
            local_chg_txt (Path): Path to the local ChangeLog file.
            repo_chg_txt (str): Mirror or remote ChangeLog file.

        Returns:
            bool: True of False.

        Raises:
            SystemExit: For keyboard interrupt.
        """
        local_size: int = 0
        repo_size: int = 0

        if self.proxy_address.startswith('http'):
            self.set_http_proxy_server()

        if self.proxy_address.startswith('socks'):
            self.set_socks_proxy_server()

        # Get local changelog file size.
        if local_chg_txt.is_file():
            local_size = int(os.stat(local_chg_txt).st_size)

        try:  # Get repository changelog file size.
            repo = self.http.request(
                'GET', repo_chg_txt,
                retries=self.urllib_retries,
                redirect=self.urllib_redirect)
            repo_size = int(repo.headers.get('content-length', 0))
        except KeyboardInterrupt as e:
            raise SystemExit(1) from e
        except (HTTPError, NewConnectionError):
            self.error_connected.append(repo_chg_txt)

        if repo_size == 0:
            return False

        return local_size != repo_size

    def check_for_error_connected(self) -> None:
        """Check for error connected and prints a message."""
        if self.error_connected:
            print(f'\n{self.endc}Failed connected to the mirrors:')
            for repo in self.error_connected:
                print(repo)

    def set_http_proxy_server(self) -> None:
        """Set for HTTP proxy server."""
        self.http = ProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)

    def set_socks_proxy_server(self) -> None:
        """Set for a proxy server."""
        try:  # Try to import PySocks if it's installed.
            from urllib3.contrib.socks import \
                SOCKSProxyManager  # pylint: disable=[C0415]

            # https://urllib3.readthedocs.io/en/stable/advanced-usage.html#socks-proxies
            self.http = SOCKSProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)
        except (ModuleNotFoundError, ImportError) as error:
            print(error)

    def view_messages(self) -> None:
        """Print for update messages."""
        repo_for_update: list[str] = []
        for repo, comp in self.compare.items():
            if comp:
                repo_for_update.append(repo)

        if repo_for_update:
            last_updates: dict[str, dict[str, str]] = self.repo_info.repo_information()

            print(f"\n{self.green}There are new updates available for the "
                  f"repositories:{self.endc}\n")

            for repo in repo_for_update:
                repo_length: int = max(len(name) for name in repo_for_update)

                last_updated: str = 'None'
                if last_updates.get(repo):
                    last_updated = last_updates[repo].get('last_updated', 'None')

                print(f'> {self.green}{repo:<{repo_length}}{self.endc} Last Updated: '
                      f"'{last_updated}'")
            if not self.option_for_check:
                print()
        else:
            print('\nNo updated packages since the last check.\n')

        if self.option_for_check:
            print()

    def updates(self) -> dict[str, bool]:
        """Call methods in parallel with the progress tool or without.

        Returns:
            dict: Dictionary of compares.
        """
        message: str = 'Checking for news, please wait'
        queue: Queue = Queue()  # type: ignore

        # Starting multiprocessing
        process_1 = Process(target=self.check_the_repositories, args=(queue,))
        process_2 = Process(target=self.progress.progress_bar, args=(message,))

        process_1.start()
        process_2.start()

        # Wait until process 1 finish.
        process_1.join()

        # Terminate process 2 if process 1 finished.
        if not process_1.is_alive():
            process_2.terminate()
            print(f'\r{message}... {self.imp.done} ', end='')

        self.compare = queue.get()
        self.error_connected = queue.get()

        # Reset cursor to normal.
        print('\x1b[?25h')

        self.check_for_error_connected()
        self.view_messages()
        return self.compare

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
from multiprocessing import Process
from pathlib import Path
from typing import Any, Callable, Union
from urllib.parse import unquote, urlparse

import requests

from slpkg.config import config_load
from slpkg.error_messages import Errors
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.views import View


class Downloader:  # pylint: disable=[R0902]
    """Download the sources using external tools."""

    def __init__(self, options: dict[str, bool]) -> None:
        self.options = options

        self.downloader = config_load.downloader
        self.maximum_parallel = config_load.maximum_parallel
        self.parallel_downloads = config_load.parallel_downloads

        self.wget_options = config_load.wget_options
        self.curl_options = config_load.curl_options
        self.aria2_options = config_load.aria2_options
        self.lftp_get_options = config_load.lftp_get_options
        self.red = config_load.red
        self.endc = config_load.endc

        self.errors = Errors()
        self.utils = Utilities()
        self.multi_process = MultiProcess(options)
        self.views = View(options)
        self.repos = Repositories()

        self.filename: str = ''
        self.repo_data: list[str] = []
        self.downloader_command: str = ''
        self.downloader_tools: dict[str, Callable[[str, Path], None]] = {
            'wget': self.set_wget_downloader,
            'wget2': self.set_wget_downloader,
            'curl': self.set_curl_downloader,
            'aria2c': self.set_aria2_downloader,
            'lftp': self.set_lftp_downloader
        }

        # Semaphore to control the number of concurrent threads
        self.semaphore = threading.BoundedSemaphore(int(self.maximum_parallel))

    def download(self, sources: Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]],
                 repo_data: Union[list[str], None] = None) -> None:
        """Start the process for downloading."""
        if repo_data is not None:
            self.repo_data = repo_data

        if self.parallel_downloads:
            self.parallel_download(sources)
        else:
            self.normal_download(sources)

    def parallel_download(self, sources: Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]]) -> None:
        """Download sources with parallel mode."""
        processes: list[Any] = []
        for urls, path in sources.values():
            with self.semaphore:
                for url in urls:
                    proc = Process(target=self.tools, args=(url, path))
                    processes.append(proc)
                    proc.start()

        for process in processes:
            process.join()

    def normal_download(self, sources: Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]]) -> None:
        """Download sources with normal mode."""
        for urls, path in sources.values():
            for url in urls:
                self.tools(url, path)

    def tools(self, url: str, path: Path) -> None:
        """Run the tool to downloading.

        Args:
            url (str): The URL link.
            path (Path): Path to save.
        """
        url_parse: str = urlparse(url).path
        self.filename = unquote(Path(url_parse).name)

        try:
            self.downloader_tools[self.downloader](url, path)
        except KeyError:
            self.errors.raise_error_message(f"Downloader '{self.downloader}' not supported", exit_status=1)

        self.multi_process.process(self.downloader_command)
        self.check_if_downloaded(path)

    def set_wget_downloader(self, url: str, path: Path) -> None:
        """Set for wget tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = f'{self.downloader} {self.wget_options} --directory-prefix={path} "{url}"'

    def set_curl_downloader(self, url: str, path: Path) -> None:
        """Set for curl tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = (f'{self.downloader} {self.curl_options} "{url}" '
                                   f'--output {path}/{self.filename}')

    def set_aria2_downloader(self, url: str, path: Path) -> None:
        """Set for wget tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = f'aria2c {self.aria2_options} --dir={path} "{url}"'

    def set_lftp_downloader(self, url: str, path: Path) -> None:
        """Set for lftp tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = f'{self.downloader} {self.lftp_get_options} {url} -o {path}'

    def check_if_downloaded(self, path: Path) -> None:
        """Check for downloaded.

        Args:
            path (Path): Path to check the file.
        """
        path_file: Path = Path(path, self.filename)
        if not path_file.exists():
            if self.repos.sbosrcarch_mirror and len(self.repo_data) > 1:
                if self.repo_data[0] in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                    location = self.repo_data[1]
                    sbo = str(path).rsplit('/', maxsplit=1)[-1]
                    url = f"{self.repos.sbosrcarch_mirror}{location}/{sbo}/{self.filename}"
                    try:
                        response = requests.get(url, stream=True, timeout=3)
                        response.raise_for_status()

                        if response.status_code == 200:
                            self.tools(url, path)
                        else:
                            print(f"{self.red}>{self.endc} Failed: URL: '{url}' does not exist!")
                    except requests.RequestException:
                        print(f'{self.red}Error{self.endc}: Failed to resolve: {url}')
            else:
                print(f"{self.red}Failed{self.endc}: Download the file: '{self.filename}'\n")
                self.views.question()

#!/usr/bin/python3
# -*- coding: utf-8 -*-


import shutil
import time
from pathlib import Path
from typing import Any

from slpkg.config import config_load
from slpkg.downloader import Downloader
from slpkg.error_messages import Errors
from slpkg.gpg_verify import GPGVerify
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint
from slpkg.views.views import View


class DownloadOnly:  # pylint: disable=[R0902]
    """Download only the sources or packages."""

    def __init__(self, directory: str, options: dict[str, bool], data: dict[str, dict[str, str]], repository: str) -> None:
        self.directory: Path = Path(directory)
        self.options = options
        self.data = data
        self.repository = repository

        self.gpg_verification = config_load.gpg_verification
        self.is_64bit = config_load.is_64bit()

        self.view = View(options, repository, data)
        self.download = Downloader(options)
        self.repos = Repositories()
        self.utils = Utilities()
        self.imp = Imprint()
        self.errors = Errors()
        self.gpg = GPGVerify()

        self.urls: dict[str, tuple[list[str], Path]] = {}
        self.asc_files: list[Any] = []
        self.count_sources: int = 0

    def packages(self, packages: list[str]) -> None:
        """Download the packages.

        Args:
            packages (list[str]): List of packages.
        """
        if not self.directory.is_dir():
            self.errors.raise_error_message(f"Path '{self.directory}' does not exist", 1)

        packages = self.utils.apply_package_pattern(self.data, packages)

        self.view.download_packages(packages, self.directory)
        self.view.question()
        start: float = time.time()

        print('\rPrepare sources for downloading... ', end='')
        for pkg in packages:
            if self.repository in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                self.save_slackbuild_sources(pkg)
                self.copy_slackbuild_scripts(pkg)
            else:
                self.save_binary_sources(pkg)

        print(self.imp.done)
        self.download_the_sources()

        elapsed_time: float = time.time() - start
        self.utils.finished_time(elapsed_time)

    def save_binary_sources(self, name: str) -> None:
        """Assign for binary repositories.

        Args:
            name (str): Package name.
        """
        package: str = self.data[name]['package']
        mirror: str = self.data[name]['mirror']
        location: str = self.data[name]['location']
        url: list[str] = [f'{mirror}{location}/{package}']
        self.count_sources += len(url)
        self.urls[name] = (url, self.directory)
        asc_url: list[str] = [f'{mirror}{location}/{package}.asc']
        asc_file: Path = Path(self.directory, f'{package}.asc')

        if self.gpg_verification:
            self.urls[f'{name}.asc'] = (asc_url, self.directory)
            self.asc_files.append(asc_file)

    def save_slackbuild_sources(self, name: str) -> None:
        """Assign for sbo repositories.

        Args:
            name (str): SBo name.
        """
        if self.is_64bit and self.data[name].get('download64'):
            sources: list[str] = list(self.data[name]['download64'])
        else:
            sources = list(self.data[name]['download'])

        self.count_sources += len(sources)

        self.urls[name] = (sources, Path(self.directory, name))

        if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
            location: str = self.data[name]['location']
            asc_file: Path = Path(self.repos.repositories_path, self.repos.sbo_repo_name,
                                  location, f'{name}{self.repos.sbo_repo_tar_suffix}.asc')
            self.asc_files.append(asc_file)

    def copy_slackbuild_scripts(self, name: str) -> None:
        """Copy slackbuilds from local repository to download path.

        Args:
            name (str): SBo name.
        """
        repo_path_package: Path = Path(self.repos.repositories[self.repository]['path'],
                                       self.data[name]['location'], name)
        if not Path(self.directory, name).is_dir():
            shutil.copytree(repo_path_package, Path(self.directory, name))

    def download_the_sources(self) -> None:
        """Download the sources."""
        if self.urls:
            print(f'Started to download total ({self.count_sources}) sources:\n')
            self.download.download(self.urls)
            print()
            self.gpg_verify()

    def gpg_verify(self) -> None:
        """Verify files with GPG."""
        if self.gpg_verification and self.repository != self.repos.ponce_repo_name:
            self.gpg.verify(self.asc_files)

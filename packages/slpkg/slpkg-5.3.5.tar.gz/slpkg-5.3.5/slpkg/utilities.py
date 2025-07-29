#!/usr/bin/python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import json
import os
import re
import shutil
import time
from collections.abc import Generator
from pathlib import Path

from slpkg.blacklist import Blacklist
from slpkg.config import config_load
from slpkg.error_messages import Errors


class Utilities:
    """List of utilities."""

    def __init__(self) -> None:
        self.log_packages = config_load.log_packages

        self.black = Blacklist()
        self.errors = Errors()

    def is_package_installed(self, name: str) -> str:
        """Return the installed package binary.

        Args:
            name (str): Package name.

        Returns:
            str: Full package name.
        """
        installed_package: Generator[Path] = self.log_packages.glob(f'{name}*')

        for installed in installed_package:
            inst_name: str = self.split_package(installed.name)['name']
            if inst_name == name and inst_name not in self.ignore_packages([inst_name]):
                return installed.name
        return ''

    def all_installed(self) -> dict[str, str]:
        """Return all installed packages from /var/log/packages folder.

        Returns:
            dict[str, str]: All installed packages and names.
        """
        installed_packages: dict[str, str] = {}

        for file in self.log_packages.glob('*'):
            name: str = self.split_package(file.name)['name']

            if not name.startswith('.'):
                installed_packages[name] = file.name

        blacklist_packages: list[str] = self.ignore_packages(list(installed_packages.keys()))
        if blacklist_packages:
            for black in blacklist_packages:
                del installed_packages[black]

        return installed_packages

    @staticmethod
    def remove_file_if_exists(path: Path, file: str) -> None:
        """Remove the old files.

        Args:
            path (Path): Path to the file.
            file (str): File name.
        """
        archive: Path = Path(path, file)
        if archive.is_file():
            archive.unlink()

    @staticmethod
    def remove_folder_if_exists(folder: Path) -> None:
        """Remove the folder if exists.

        Args:
            folder (Path): Path to the folder.
        """
        if folder.exists():
            shutil.rmtree(folder)

    @staticmethod
    def create_directory(directory: Path) -> None:
        """Create folder like mkdir -p.

        Args:
            directory (Path): Path to folder.
        """
        if not directory.is_dir():
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def split_package(package: str) -> dict[str, str]:
        """Split the binary package name in name, version, arch, build and tag.

        Args:
            package (str): Full package name for splitting.

        Returns:
            dict[str, str]: Split package by name, version, arch, build and package tag.
        """
        name: str = '-'.join(package.split('-')[:-3])
        version: str = ''.join(package[len(name):].split('-')[:-2])
        arch: str = ''.join(package[len(name + version) + 2:].split('-')[:-1])
        build_tag: str = package.split('-')[-1]
        build: str = ''.join(re.findall(r'\d+', build_tag[:2]))
        pkg_tag: str = build_tag[len(build):]

        return {
            'name': name,
            'version': version,
            'arch': arch,
            'build': build,
            'tag': pkg_tag
        }

    @staticmethod
    def finished_time(elapsed_time: float) -> None:
        """Print the elapsed time.

        Args:
            elapsed_time (float): Unformatted time.
        """
        print('\nFinished:', time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))

    def read_packages_from_file(self, file: Path) -> Generator[str]:
        """Read packages from file.

        Args:
            file (Path): Path to the file.

        Yields:
            Generator[str]: Package names.
        """
        try:
            with open(file, 'r', encoding='utf-8') as pkgs:
                packages: list[str] = pkgs.read().splitlines()

            for package in packages:
                if package and not package.startswith('#'):
                    if '#' in package:
                        package = package.split('#')[0].strip()
                    yield package
        except FileNotFoundError:
            self.errors.raise_error_message(f"No such file or directory: '{file}'", exit_status=20)

    def read_text_file(self, file: Path) -> list[str]:
        """Read a text file.

        Args:
            file (Path): Path to the file.

        Returns:
            list[str]: The lines in the list.
        """
        try:
            with open(file, 'r', encoding='utf-8', errors='replace') as text_file:
                return text_file.readlines()
        except FileNotFoundError:
            self.errors.raise_error_message(f"No such file or directory: '{file}'", exit_status=20)
        return []

    def count_file_size(self, name: str) -> int:
        """Count the file size.

        Read the contents files from the package file list
        and count the total installation file size in bytes.

        Args:
            name (str): The name of the package.

        Returns:
            int
        """
        count_files: int = 0
        installed: Path = Path(self.log_packages, self.is_package_installed(name))
        if installed:
            file_installed: list[str] = installed.read_text(encoding="utf-8").splitlines()
            for line in file_installed:
                file: Path = Path('/', line)
                if file.is_file():
                    count_files += file.stat().st_size
        return count_files

    @staticmethod
    def convert_file_sizes(byte_size: float) -> str:
        """Convert bytes to kb, mb and gb.

        Args:
            byte_size (float): The file size in bytes.

        Returns:
            str
        """
        kb_size: float = byte_size / 1024
        mb_size: float = kb_size / 1024
        gb_size: float = mb_size / 1024

        if gb_size >= 1:
            return f"{gb_size:.0f} GB"
        if mb_size >= 1:
            return f"{mb_size:.0f} MB"
        if kb_size >= 1:
            return f"{kb_size:.0f} KB"

        return f"{byte_size} B"

    @staticmethod
    def apply_package_pattern(data: dict[str, dict[str, str]], packages: list[str]) -> list[str]:
        """If the '*' applied returns all the package names.

        Args:
            data (dict[str, dict[str, str]]): The repository data.
            packages (list[str]): The packages that applied.

        Returns:
            list[str]: Package names.
        """
        for pkg in packages:
            if pkg == '*':
                packages.remove('*')
                packages.extend(list(data.keys()))
        return packages

    @staticmethod
    def change_owner_privileges(folder: Path) -> None:
        """Change the owner privileges.

        Args:
            folder (Path): Path to the folder.
        """
        os.chown(folder, 0, 0)
        for file in os.listdir(folder):
            os.chown(Path(folder, file), 0, 0)

    @staticmethod
    def case_insensitive_pattern_matching(packages: list[str], data: dict[str, dict[str, str]],
                                          options: dict[str, bool]) -> list[str]:
        """Case-insensitive pattern matching packages.

        Args:
            packages (list[str]): List of packages.
            data (dict[str, dict[str, str]]): Repository data.
            options (list[str]): User options.

        Returns:
            list[str]: Matched packages.
        """
        if options.get('option_no_case'):
            repo_packages: tuple[str, ...] = tuple(data.keys())
            for package in packages:
                for pkg in repo_packages:
                    if package.lower() == pkg.lower():
                        packages.append(pkg)
                        packages.remove(package)
                        break
        return packages

    def read_json_file(self, file: Path) -> dict[str, dict[str, str]]:
        """Read JSON data from the file.

        Args:
            file (Path): Path file for reading.

        Returns:
            dict[str, dict[str, str]]: Json data file.
        """
        json_data: dict[str, dict[str, str]] = {}
        try:
            json_data = json.loads(file.read_text(encoding='utf-8'))
        except FileNotFoundError:
            self.errors.raise_error_message(f'{file} not found.', exit_status=1)
        except json.decoder.JSONDecodeError:
            pass
        return json_data

    def ignore_packages(self, packages: list[str]) -> list[str]:
        """Match packages using regular expression.

        Args:
            packages (list[str]): The packages to apply the pattern.

        Returns:
            list[str]
        """
        matching_packages: list[str] = []
        blacklist: list[str] = self.black.packages()
        if blacklist:
            pattern: str = '|'.join(tuple(blacklist))
            matching_packages = [pkg for pkg in packages if re.search(pattern, pkg)]
        return matching_packages

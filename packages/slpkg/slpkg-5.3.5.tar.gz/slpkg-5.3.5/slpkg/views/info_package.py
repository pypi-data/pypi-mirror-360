#!/usr/bin/python3
# -*- coding: utf-8 -*-


from pathlib import Path

from slpkg.repositories import Repositories
from slpkg.utilities import Utilities


class InfoPackage:  # pylint: disable=[R0902]
    """View the packages' information."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        self.options = options
        self.repository = repository

        self.utils = Utilities()
        self.repos = Repositories()

        self.repository_packages: tuple[str, ...] = ()
        self.readme: list[str] = []
        self.info_file: list[str] = []
        self.repo_build_tag: str = ''
        self.mirror: str = ''
        self.homepage: str = ''
        self.maintainer: str = ''
        self.email: str = ''
        self.dependencies: str = ''
        self.repo_tar_suffix: str = ''

        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)

    def slackbuild(self, data: dict[str, dict[str, str]], slackbuilds: list[str]) -> None:
        """View slackbuilds information.

        Args:
            data (dict[str, dict[str, str]]): Repository data.
            slackbuilds (list[str]): List of slackbuilds.
        """
        print()
        repo: dict[str, str] = {
            self.repos.sbo_repo_name: self.repos.sbo_repo_tar_suffix,
            self.repos.ponce_repo_name: ''
        }
        git_mirror: dict[str, str] = {
            self.repos.sbo_repo_name: self.repos.sbo_git_mirror,
            self.repos.ponce_repo_name: self.repos.ponce_git_mirror
        }

        self.repo_tar_suffix = repo[self.repository]

        self.mirror = self.repos.repositories[self.repository]['mirror_packages']
        if '.git' in git_mirror[self.repository]:

            branch: str = self.repos.sbo_branch
            if self.repository == self.repos.ponce_repo_name:
                branch = self.repos.ponce_branch

            self.mirror = git_mirror[self.repository].replace('.git', f'/tree/{branch}/')
            self.repo_tar_suffix = '/'

        self.repository_packages = tuple(data.keys())

        for sbo in slackbuilds:
            for name, item in data.items():

                if sbo in [name, '*']:
                    path_file: Path = Path(self.repos.repositories[self.repository]['path'],
                                           item['location'], name, 'README')
                    path_info: Path = Path(self.repos.repositories[self.repository]['path'],
                                           item['location'], name, f'{name}.info')

                    self.read_the_readme_file(path_file)
                    self.read_the_info_file(path_info)
                    self.repo_build_tag = data[name]['build']
                    self.assign_the_info_file_variables()
                    self.assign_dependencies(item)
                    self.assign_dependencies_with_version(item, data)
                    self.view_slackbuild_package(name, item)

    def read_the_readme_file(self, path_file: Path) -> None:
        """Read the README file.

        Args:
            path_file (Path): Path to the file.
        """
        self.readme = self.utils.read_text_file(path_file)

    def read_the_info_file(self, path_info: Path) -> None:
        """Read the .info file.

        Args:
            path_info (Path): Path to the file.
        """
        self.info_file = self.utils.read_text_file(path_info)

    def assign_the_info_file_variables(self) -> None:
        """Assign data from the .info file."""
        for line in self.info_file:
            if line.startswith('HOMEPAGE'):
                self.homepage = line[10:-2].strip()
            if line.startswith('MAINTAINER'):
                self.maintainer = line[12:-2].strip()
            if line.startswith('EMAIL'):
                self.email = line[7:-2].strip()

    def assign_dependencies(self, item: dict[str, str]) -> None:
        """Assign the package dependencies.

        Args:
            item (dict[str, str]): Data value.
        """
        self.dependencies = ', '.join([f'{pkg}' for pkg in item['requires']])

    def assign_dependencies_with_version(self, item: dict[str, str], data: dict[str, dict[str, str]]) -> None:
        """Assign dependencies with version.

        Args:
            item (dict[str, str]): Data value.
            data (dict[str, dict[str, str]]): Repository data.
        """
        if self.option_for_pkg_version:
            self.dependencies = (', '.join(
                [f"{pkg}-{data[pkg]['version']}" for pkg in item['requires']
                 if pkg in self.repository_packages]))

    def view_slackbuild_package(self, name: str, item: dict[str, str]) -> None:
        """Print slackbuild information.

        Args:
            name (str): Slackbuild name.
            item (dict[str, str]): Data value.
        """
        space_align: str = ''
        print(f"{'Repository':<15}: {self.repository}\n"
              f"{'Name':<15}: {name}\n"
              f"{'Version':<15}: {item['version']}\n"
              f"{'Build':<15}: {self.repo_build_tag}\n"
              f"{'Homepage':<15}: {self.homepage}\n"
              f"{'Download SBo':<15}: {self.mirror}{item['location']}/{name}{self.repo_tar_suffix}\n"
              f"{'Sources':<15}: {' '.join(item['download'])}\n"
              f"{'Md5sum':<15}: {' '.join(item['md5sum'])}\n"
              f"{'Sources x86_64':<15}: {' '.join(item['download64'])}\n"
              f"{'Md5sum x86_64':<15}: {' '.join(item['md5sum64'])}\n"
              f"{'Files':<15}: {' '.join(item['files'])}\n"
              f"{'Category':<15}: {item['location']}\n"
              f"{'SBo url':<15}: {self.mirror}{item['location']}/{name}/\n"
              f"{'Maintainer':<15}: {self.maintainer}\n"
              f"{'Email':<15}: {self.email}\n"
              f"{'Requires':<15}: {self.dependencies}\n"
              f"{'Description':<15}: {item['description']}\n"
              f"{'README':<15}: {f'{space_align:>17}'.join(self.readme)}")

    def package(self, data: dict[str, dict[str, str]], packages: list[str]) -> None:
        """View binary packages information.

        Args:
            data (dict[str, dict[str, str]]): Repository data.
            packages (list[str]): List of packages.
        """
        print()
        self.repository_packages = tuple(data.keys())
        for package in packages:
            for name, item in data.items():
                if package in [name, '*']:
                    self.assign_dependencies(item)
                    self.assign_dependencies_with_version(item, data)
                    self.view_binary_package(name, item)

    def view_binary_package(self, name: str, item: dict[str, str]) -> None:
        """Print binary packages information.

        Args:
            name (str): Package name.
            item (dict[str, str]): Data values.
        """
        print(f"{'Repository':<15}: {self.repository}\n"
              f"{'Name':<15}: {name}\n"
              f"{'Version':<15}: {item['version']}\n"
              f"{'Build':<15}: {item['build']}\n"
              f"{'Package':<15}: {item['package']}\n"
              f"{'Download':<15}: {item['mirror']}{item['location']}/{item['package']}\n"
              f"{'Md5sum':<15}: {item['checksum']}\n"
              f"{'Mirror':<15}: {item['mirror']}\n"
              f"{'Location':<15}: {item['location']}\n"
              f"{'Size Comp':<15}: {item['size_comp']} KB\n"
              f"{'Size Uncomp':<15}: {item['size_uncomp']} KB\n"
              f"{'Requires':<15}: {self.dependencies}\n"
              f"{'Conflicts':<15}: {item['conflicts']}\n"
              f"{'Suggests':<15}: {item['suggests']}\n"
              f"{'Description':<15}: {item['description']}\n")

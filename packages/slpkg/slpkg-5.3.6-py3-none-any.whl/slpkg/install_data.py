#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import re
from pathlib import Path
from typing import Any, Union

from slpkg.config import config_load
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess


class InstallData:
    """Installs data to the repositories path."""

    def __init__(self) -> None:
        self.cpu_arch = config_load.cpu_arch
        self.package_type = config_load.package_type

        self.utils = Utilities()
        self.repos = Repositories()
        self.multi_process = MultiProcess()
        self.view_process = ViewProcess()

    def write_repo_info(self, changelog_file: Path, info: dict[str, Any]) -> None:
        """Write some repo information.

        Args:
            changelog_file (Path): Repository ChangeLog.txt path.
            info (dict[str, Any]): Repository information.
        """
        repo_name: str = info['repo_name']
        full_requires: bool = info['full_requires']
        last_date: str = ''
        repo_info: dict[str, Any] = {}
        lines: list[str] = self.utils.read_text_file(changelog_file)
        days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        for line in lines:
            if line.startswith(days):
                last_date = line.replace('\n', '')
                break

        if self.repos.repos_information.is_file():
            repo_info = self.utils.read_json_file(self.repos.repos_information)

        repo_info[repo_name] = {
            'last_updated': last_date,
            'full_requires': full_requires
        }

        self.repos.repos_information.write_text(json.dumps(repo_info, indent=4), encoding='utf-8')

    def install_sbo_data(self, repo: str) -> None:  # pylint: disable=[R0914]
        """Read the SLACKBUILDS.TXT FILE and creates a json data file.

        Args:
            repo (str): repository name.
        """
        self.view_process.message(f'Updating the database for {repo}')

        data: dict[str, dict[str, Union[str, list[str]]]] = {}
        cache: list[str] = []
        sbo_tags: list[str] = [
            'SLACKBUILD NAME:',
            'SLACKBUILD LOCATION:',
            'SLACKBUILD FILES:',
            'SLACKBUILD VERSION:',
            'SLACKBUILD DOWNLOAD:',
            'SLACKBUILD DOWNLOAD_x86_64:',
            'SLACKBUILD MD5SUM:',
            'SLACKBUILD MD5SUM_x86_64:',
            'SLACKBUILD REQUIRES:',
            'SLACKBUILD SHORT DESCRIPTION:'
        ]

        slackbuilds_txt: list[str] = Path(self.repos.repositories[repo]['path'],
                                          self.repos.repositories[repo]['slackbuilds_txt']).read_text(
            encoding='utf-8').splitlines()

        for i, line in enumerate(slackbuilds_txt, 1):
            for tag in sbo_tags:
                if line.startswith(tag):
                    line = line.replace(tag, '').strip()
                    cache.append(line)

            if (i % 11) == 0:
                build: str = ''
                name: str = cache[0]
                version: str = cache[3]
                location: str = cache[1].split('/')[1]

                data[name] = {
                    'location': location,
                    'files': cache[2].split(),
                    'version': version,
                    'download': cache[4].split(),
                    'download64': cache[5].split(),
                    'md5sum': cache[6].split(),
                    'md5sum64': cache[7].split(),
                    'requires': cache[8].replace('%README%', '').split(),
                    'description': cache[9].replace(name, '').strip()
                }

                arch: str = self.cpu_arch
                sbo_file: Path = Path(self.repos.repositories[repo]['path'], location, name, f'{name}.SlackBuild')
                if sbo_file.is_file():
                    slackbuild = sbo_file.read_text(encoding='utf-8').splitlines()
                    for sbo_line in slackbuild:
                        if sbo_line.startswith('BUILD=$'):
                            build = ''.join(re.findall(r'\d+', sbo_line))
                        if sbo_line.startswith('ARCH=noarch'):
                            arch = 'noarch'

                data[name].update({'arch': arch})
                data[name].update({'build': build})
                package: str = f"{name}-{version}-{arch}-{build}{self.repos.repositories[repo]['repo_tag']}.tgz"
                data[name].update({'package': package})

                cache = []  # reset cache after 11 lines

        repo_info: dict[str, Any] = {
            'repo_name': repo,
            'full_requires': False
        }

        path_changelog: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.repositories[repo]['changelog_txt'])
        self.write_repo_info(path_changelog, repo_info)

        data_file: Path = Path(self.repos.repositories[repo]['path'], self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4), encoding='utf-8')

        self.view_process.done()
        print()

    def install_binary_data(self, repo: str) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Installs the data for binary repositories.

        Args:
            repo (str): Description
        """
        print()
        self.view_process.message(f'Updating the database for {repo}')

        slack_repos: list[str] = [self.repos.slack_patches_repo_name, self.repos.slack_extra_repo_name]

        mirror: str = self.repos.repositories[repo]['mirror_packages']
        if repo in slack_repos:
            mirror = self.repos.repositories[repo]['mirror_changelog']

        checksums_dict: dict[str, str] = {}
        data: dict[str, dict[str, Union[str, list[str]]]] = {}
        build: str = ''
        arch: str = ''
        requires: list[str] = []
        full_requires: bool = False
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.repositories[repo]['path'],
                                   self.repos.repositories[repo]['packages_txt'])
        path_checksums: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.repositories[repo]['checksums_md5'])
        packages_txt: list[str] = self.utils.read_text_file(path_packages)

        checksums_md5: list[str] = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()
            if line.endswith(tuple(self.package_type)):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list[str] = []  # init cache

        for i, line in enumerate(packages_txt):
            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build = self.utils.split_package(package)['build']
                arch = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (.) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                required = line.replace(pkg_tag[4], '').strip()
                if '|' in required:
                    full_requires = True
                    deps: list[str] = []
                    for req in required.split(','):
                        dep = req.split('|')
                        if len(dep) > 1:
                            deps.append(dep[1])
                        else:
                            deps.extend(dep)
                    requires = list(set(deps))
                else:
                    requires = required.split(',')

            if line.startswith(pkg_tag[5]):
                package_description = packages_txt[i + 1][(len(name) * 2) + 2:].strip()
                if not package_description:
                    package_description = 'Not found'
                if not package_description.startswith('(') and not package_description.endswith(')'):
                    package_description = f'({package_description})'
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]] = {
                    'repo': repo,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': '',
                }

                cache = []  # reset cache
                requires = []  # reset requires

        repo_info: dict[str, Any] = {
            'repo_name': repo,
            'full_requires': full_requires
        }

        path_changelog: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.repositories[repo]['changelog_txt'])
        self.write_repo_info(path_changelog, repo_info)

        data_file: Path = Path(self.repos.repositories[repo]['path'], self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4), encoding='utf-8')

        self.view_process.done()
        print()

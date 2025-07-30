#!/usr/bin/python3
# -*- coding: utf-8 -*-


import re
import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

from slpkg.check_updates import CheckUpdates
from slpkg.config import config_load
from slpkg.downloader import Downloader
from slpkg.install_data import InstallData
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.sbos.sbo_generate import SBoGenerate
from slpkg.utilities import Utilities
from slpkg.views.views import View


class UpdateRepositories:  # pylint: disable=[R0902]
    """Update the local repositories."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        self.gpg_verification = config_load.gpg_verification
        self.ask_question = config_load.ask_question
        self.git_clone = config_load.git_clone
        self.green = config_load.green
        self.red = config_load.red
        self.endc = config_load.endc
        self.lftp_mirror_options = config_load.lftp_mirror_options

        self.view = View(options)
        self.multi_process = MultiProcess(options)
        self.repos = Repositories()
        self.utils = Utilities()
        self.data = InstallData()
        self.generate = SBoGenerate()
        self.check_updates = CheckUpdates(options, repository)
        self.download = Downloader(options)

        self.repos_for_update: dict[str, bool] = {}

    def repositories(self) -> None:
        """Check and call the repositories for update."""
        self.repos_for_update = self.check_updates.updates()

        if not any(list(self.repos_for_update.values())):
            self.view.question(message='Do you want to force update?')
            # Force update the repositories.
            for repo in self.repos_for_update:
                self.repos_for_update[repo] = True

        self.run_update()

    def import_gpg_key(self, repo: str) -> None:
        """Import the GPG KEY.

        Args:
            repo (str): Repository GPG mirror key.

        Returns:
            None
        """
        if self.gpg_verification:
            mirror: str = self.repos.repositories[repo]['mirror_changelog']

            if repo == self.repos.sbo_repo_name:
                mirror = 'https://www.slackbuilds.org/'

            gpg_key: str = f'{mirror}GPG-KEY'
            gpg_command: str = 'gpg --fetch-key'

            try:
                process = subprocess.run(f'{gpg_command} {gpg_key}', shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, encoding='utf-8', text=True, check=True)

                self._getting_gpg_print(process, mirror)
            except subprocess.CalledProcessError:
                mirror = self.repos.repositories[repo]['mirror_packages']
                gpg_key = f'{mirror}GPG-KEY'

                try:
                    process = subprocess.run(f'{gpg_command} {gpg_key}', shell=True, stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT, encoding='utf-8', text=True, check=True)
                    self._getting_gpg_print(process, mirror)
                except subprocess.CalledProcessError:
                    print(f'Getting GPG key: {self.red}Failed{self.endc}')
                    self.view.question()

    @staticmethod
    def _getting_gpg_print(process: CompletedProcess, mirror: str) -> None:  # type: ignore
        """Print the gpg mirror.

        Args:
            process: Subprocess process output.
            mirror: The GPG key mirror

        Returns:
            None
        """
        output: list[str | Any] = re.split(r"/|\s", process.stdout)
        if process.returncode == 0 and 'imported:' in output:
            print(f'Getting GPG key from: {mirror}\n')

    def run_update(self) -> None:
        """Update the repositories by category."""
        for repo, update in self.repos_for_update.items():
            if update:

                self.view_downloading_message(repo)
                if repo in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                    self.update_slackbuild_repos(repo)
                else:
                    self.update_binary_repos(repo)

    def view_downloading_message(self, repo: str) -> None:
        """Print the syncing message.

        Args:
            repo (str): Repository name.
        """
        print(f"Syncing with the repository '{self.green}{repo}{self.endc}', please wait...\n")

    def update_binary_repos(self, repo: str) -> None:
        """Update the binary repositories.

        Args:
            repo (str): Repository name.
        """
        urls: dict[str, tuple[tuple[str, str, str], Path]] = {}

        self.import_gpg_key(repo)

        changelog: str = (f"{self.repos.repositories[repo]['mirror_changelog']}"
                          f"{self.repos.repositories[repo]['changelog_txt']}")
        packages: str = (f"{self.repos.repositories[repo]['mirror_packages']}"
                         f"{self.repos.repositories[repo]['packages_txt']}")
        checksums: str = (f"{self.repos.repositories[repo]['mirror_packages']}"
                          f"{self.repos.repositories[repo]['checksums_md5']}")

        urls[repo] = ((changelog, packages, checksums), self.repos.repositories[repo]['path'])

        self.utils.remove_file_if_exists(self.repos.repositories[repo]['path'],
                                         self.repos.repositories[repo]['changelog_txt'])
        self.utils.remove_file_if_exists(self.repos.repositories[repo]['path'],
                                         self.repos.repositories[repo]['packages_txt'])
        self.utils.remove_file_if_exists(self.repos.repositories[repo]['path'],
                                         self.repos.repositories[repo]['checksums_md5'])

        self.utils.create_directory(self.repos.repositories[repo]['path'])

        self.download.download(urls)

        self.data.install_binary_data(repo)

    def update_slackbuild_repos(self, repo: str) -> None:
        """Update the slackbuild repositories.

        Args:
            repo (str): Repository name.
        """
        self.import_gpg_key(repo)

        mirror: str = self.repos.repositories[repo]['mirror_packages']

        git_mirror: dict[str, str] = {
            self.repos.sbo_repo_name: self.repos.sbo_git_mirror,
            self.repos.ponce_repo_name: self.repos.ponce_git_mirror
        }

        repo_path: Path = self.repos.repositories[repo]['path']

        if '.git' in git_mirror[repo]:
            self.utils.remove_folder_if_exists(repo_path)
            syncing_command: str = f'{self.git_clone} {git_mirror[repo]} {repo_path}'
        else:
            self.utils.remove_file_if_exists(repo_path, self.repos.repositories[repo]['slackbuilds_txt'])
            self.utils.remove_file_if_exists(repo_path, self.repos.repositories[repo]['changelog_txt'])
            self.utils.create_directory(repo_path)
            syncing_command = f'lftp {self.lftp_mirror_options} {mirror} {repo_path}'

        self.multi_process.process(syncing_command)

        # It checks if there is a SLACKBUILDS.TXT file, otherwise it's going to create one.
        if not Path(self.repos.repositories[repo]['path'],
                    self.repos.repositories[repo]['slackbuilds_txt']).is_file():
            if '.git' in git_mirror[repo]:
                print()
            self.generate.slackbuild_file(self.repos.repositories[repo]['path'],
                                          self.repos.repositories[repo]['slackbuilds_txt'])

        self.data.install_sbo_data(repo)

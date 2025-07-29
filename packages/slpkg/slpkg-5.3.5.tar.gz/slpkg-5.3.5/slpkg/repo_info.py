#!/usr/bin/python3
# -*- coding: utf-8 -*-


import shutil
import time
from pathlib import Path
from typing import Any

import requests

from slpkg.config import config_load
from slpkg.load_data import LoadData
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities


class RepoInfo:  # pylint: disable=[R0902]
    """View information about repositories."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        self.repository = repository

        self.cyan = config_load.cyan
        self.green = config_load.green
        self.red = config_load.red
        self.grey = config_load.grey
        self.endc = config_load.endc

        self.load_data = LoadData()
        self.utils = Utilities()
        self.repos = Repositories()
        self.columns, self.rows = shutil.get_terminal_size()

        self.name_alignment: int = self.columns - 61
        self.name_alignment = max(self.name_alignment, 1)

        self.mirror_alignment: int = self.columns - 32
        self.mirror_alignment = max(self.mirror_alignment, 1)

        self.enabled: int = 0
        self.total_packages: int = 0
        self.repo_data: dict[str, dict[str, str]] = {}
        self.dates: dict[str, Any] = {}
        self.mirrors_score: dict[str, int] = {}

        self.option_for_repository: bool = options.get('option_repository', False)
        self.option_for_fetch: bool = options.get('option_fetch', False)

    def info(self) -> None:
        """Print information about repositories."""
        if self.option_for_fetch:
            self.view_the_score_title()

            if self.option_for_repository:
                mirror: str = self.repos.repositories[self.repository]['mirror_changelog']
                self.enabled += 1
                self.check_mirror_speed(self.repository, mirror)
                self.view_summary_of_repository()
            else:
                for repo, data in self.repos.repositories.items():
                    if data['enable']:
                        mirror = data['mirror_changelog']
                        self.enabled += 1
                        self.check_mirror_speed(repo, mirror)
                self.view_summary_of_all_repositories()
        else:

            self.load_repo_data()
            self.view_the_title()

            if self.option_for_repository:
                self.view_the_repository_information()
            else:
                self.view_the_repositories_information()

    def check_mirror_speed(self, repo: str, url: str) -> None:
        """Check mirrors speed.

        Args:
            repo (str): Name of the repository.
            url (str): The repository mirror.
        """
        if repo in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            git_repos: dict[str, str] = {
                self.repos.sbo_repo_name: self.repos.sbo_git_mirror,
                self.repos.ponce_repo_name: self.repos.ponce_git_mirror,
            }
            if git_repos[repo].endswith('git'):
                url = git_repos[repo]

        url_view = url
        url_length = 45 + (self.columns - 80)
        if url_length < len(url):
            url_view = f'{url[:url_length]}...'

        try:
            start_time: float = time.time()  # Record the start time
            response = requests.get(url, timeout=10)
            end_time: float = time.time()  # Record the end time

            response.raise_for_status()

            if response.status_code == 200:
                response_time = int((end_time - start_time) * 1000)  # Convert to milliseconds
                self.mirrors_score[repo] = response_time
                print(f"{repo:<19}{url_view:<{self.mirror_alignment}}"
                      f"{response_time:>9} ms")
            else:
                print(f"{self.red}{repo:<19}{self.endc}{url_view:<{self.mirror_alignment}}{self.red}"
                      f"{response.status_code:>12}{self.endc}")
        except requests.RequestException as e:
            error_message = f"HTTP {e.response.status_code}" if e.response else "Error"
            print(f"{repo:<19}{url_view:<{self.mirror_alignment}}{self.red}{error_message:>12}{self.endc}")
        except Exception:  # pylint: disable=[W0703]
            url_length = 45 + (self.columns - 80)
            if url_length < len(url):
                url_view = f'{url[:url_length - 3]}...'
            error_message = "Unknown Error"
            print(f"{repo:<19}{url_view:<{self.mirror_alignment - 1}}{self.red}{error_message}{self.endc}")

    def load_repo_data(self) -> None:
        """Load repository data."""
        self.dates = self.repo_information()
        if self.option_for_repository:
            self.repo_data = self.load_data.load(self.repository)
        else:
            self.repo_data = self.load_data.load('*')

    def repo_information(self) -> dict[str, dict[str, str]]:
        """Load repository information.

        Returns:
            dict[str, dict[str, str]]: Json data file.
        """
        repo_info_json: Path = Path(f'{self.repos.repositories_path}', self.repos.repos_information)
        if repo_info_json.is_file():
            repo_info_json = Path(f'{self.repos.repositories_path}', self.repos.repos_information)
            return self.utils.read_json_file(repo_info_json)
        return {}

    def view_the_score_title(self) -> None:
        """Print the title."""
        title: str = 'Fetching mirrors, please wait...'
        print(f'{title}\n')
        print('=' * (self.columns - 1))
        print(f"{'Name:':<19}{'Mirror:':<{self.mirror_alignment}}{'Score:':>12}")
        print('=' * (self.columns - 1))

    def view_the_title(self) -> None:
        """Print the title."""
        title: str = 'repositories information:'.title()
        if self.option_for_repository:
            title = 'repository information:'.title()
        print(f'\n{title}')
        print('=' * (self.columns - 1))
        print(f"{'Name:':<{self.name_alignment}}{'Status:':<14}{'Last Updated:':<34}{'Packages:':>12}")
        print('=' * (self.columns - 1))

    def view_the_repository_information(self) -> None:
        """Print the repository information."""
        args: dict[str, Any] = {
            'repo': self.repository,
            'date': 'None',
            'count': 0,
            'color': self.red,
            'status': 'Disable'
        }

        if self.dates.get(self.repository):
            args['date'] = self.dates[self.repository].get('last_updated', 'None')

        if self.repos.repositories[self.repository]['enable']:
            self.enabled += 1
            args['status'] = 'Enabled'
            args['color'] = self.green
            args['count'] = len(self.repo_data)
            self.total_packages += len(self.repo_data)

        self.view_the_line_information(args)
        self.view_summary_of_repository()

    def view_the_repositories_information(self) -> None:
        """Print the repositories' information."""
        for repo, conf in self.repos.repositories.items():
            args: dict[str, Any] = {
                'repo': repo,
                'date': 'None',
                'count': 0,
                'color': self.red,
                'status': 'Disable'
            }

            if self.dates.get(repo):
                args['date'] = self.dates[repo].get('last_updated', 'None')

            if conf['enable']:
                self.enabled += 1
                args['status'] = 'Enabled'
                args['color'] = self.green
                args['count'] = len(self.repo_data[repo])
                self.total_packages += len(self.repo_data[repo])

            self.view_the_line_information(args)
        self.view_summary_of_all_repositories()

    def view_the_line_information(self, args: dict[str, str]) -> None:
        """Print the row of information.

        Args:
            args (dict[str, str]): Arguments for print.
        """
        repository: str = args['repo']
        repo_color: str = ''
        if args['repo'] == self.repos.default_repository:
            repo_color = self.cyan
            repository = f"{args['repo']} *"

        print(f"{repo_color}{repository:<{self.name_alignment}}{self.endc}{args['color']}{args['status']:<14}"
              f"{self.endc}{args['date']:<34}{args['count']:>12}")

    def view_summary_of_repository(self) -> None:
        """Print the repository summary."""
        print('=' * (self.columns - 1))
        if self.option_for_fetch:
            print(f"{self.grey}Score {int(self.mirrors_score[self.repository])} ms for repository "
                  f"'{self.repository}'.\n{self.endc}")
        else:
            print(f"{self.grey}Total {self.total_packages} packages available from the "
                  f"'{self.repository}' repository.\n{self.endc}")

    def view_summary_of_all_repositories(self) -> None:
        """Print the total summary of repositories."""
        print('=' * (self.columns - 1))
        if self.option_for_fetch and self.mirrors_score:
            slower_mirror: str = max(self.mirrors_score, key=lambda key: self.mirrors_score[key])
            fastest_mirror: str = min(self.mirrors_score, key=lambda key: self.mirrors_score[key])

            print(f"{self.grey}Fastest mirror is '{fastest_mirror}' and "
                  f"slower mirror is '{slower_mirror}'.\n{self.endc}")
        else:
            print(f"{self.grey}Total of {self.enabled}/{len(self.repos.repositories)} "
                  f"repositories are enabled with {self.total_packages} packages available.\n"
                  f"* Default repository is '{self.repos.default_repository}'.\n{self.endc}")

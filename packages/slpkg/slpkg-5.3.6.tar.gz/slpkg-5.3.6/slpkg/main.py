#!/usr/bin/python3
# -*- coding: utf-8 -*-


import argparse
import logging
import os
import re
import sys
import time
from pathlib import Path
from signal import SIG_DFL, SIGPIPE, signal
from typing import Any, Callable, NoReturn, Union

from slpkg.binaries.install import Packages
from slpkg.changelog import Changelog
from slpkg.check_updates import CheckUpdates
from slpkg.checks import Check
from slpkg.choose_packages import Choose
from slpkg.cleanings import Cleanings
from slpkg.config import config_load
from slpkg.dependees import Dependees
from slpkg.dialog_configs import FormConfigs
from slpkg.download_only import DownloadOnly
from slpkg.error_messages import Errors
from slpkg.list_installed import ListInstalled
from slpkg.load_data import LoadData
from slpkg.multi_process import MultiProcess
from slpkg.remove_packages import RemovePackages
from slpkg.repo_info import RepoInfo
from slpkg.repositories import Repositories
from slpkg.sbos.slackbuild import Slackbuilds
from slpkg.search import SearchPackage
from slpkg.self_check import check_self_update
from slpkg.tracking import Tracking
from slpkg.update_repositories import UpdateRepositories
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.info_package import InfoPackage
from slpkg.views.version import Version
from slpkg.views.views import View

signal(SIGPIPE, SIG_DFL)


class Run:  # pylint: disable=[R0902]
    """Run main slpkg methods."""

    def __init__(self, options: dict[str, bool], repository: str, directory: str) -> None:  # pylint: disable=[R0915]
        self.options = options
        self.repos = Repositories()

        self.repository = repository
        if not repository:
            self.repository = self.repos.default_repository

        self.prog_name = config_load.prog_name
        self.dialog = config_load.dialog
        self.tmp_slpkg = config_load.tmp_slpkg
        self.file_list_suffix = config_load.file_list_suffix
        self.bootloader_command = config_load.bootloader_command
        self.red = config_load.red
        self.green = config_load.green
        self.endc = config_load.endc

        self.directory = directory
        if not directory:
            self.directory = str(self.tmp_slpkg)

        self.utils = Utilities()
        self.multi_process = MultiProcess()
        self.views = View()

        self.data: dict[str, dict[str, str]] = {}

        self.load_data = LoadData()

        self.check = Check()
        self.choose = Choose(self.options, self.repository)

    def is_file_list_packages(self, packages: list[str]) -> list[str]:
        """Check for filelist.pkgs file."""
        if packages[0].endswith(self.file_list_suffix):
            file = Path(packages[0])
            file_packages: list[str] = list(self.utils.read_packages_from_file(file))
            return file_packages
        return packages

    @staticmethod
    def is_root() -> None:
        """Checking for root privileges.
        """
        if not os.geteuid() == 0:
            sys.exit('Must run as root.')

    def update(self) -> NoReturn:
        """Update the local repositories.

        Raises:
            SystemExit: Exit code 0.
        """
        self.is_root()

        if self.options.get('option_check'):
            check = CheckUpdates(self.options, self.repository)
            check.updates()
        else:
            start: float = time.time()
            update = UpdateRepositories(self.options, self.repository)
            update.repositories()
            elapsed_time: float = time.time() - start
            self.utils.finished_time(elapsed_time)
        sys.exit(0)

    def upgrade(self) -> NoReturn:  # pylint: disable=[R0912]
        """Upgrade the installed packages.

        Raises:
            SystemExit: Exit code 0.
        """
        self.is_root()
        command: str = Run.upgrade.__name__
        removed: list[str] = []
        added: list[str] = []
        ordered: bool = True
        kernel_generic_current_package: str = self.utils.is_package_installed('kernel-generic')

        if self.options.get('option_check'):
            self.data = self.load_data.load(self.repository)
            upgrade = Upgrade(self.repository, self.data)
            upgrade.check_packages()

        elif self.repository != '*':
            self.data = self.load_data.load(self.repository)
            upgrade = Upgrade(self.repository, self.data)
            packages: list[str] = list(upgrade.packages())

            for package in packages:
                if package.endswith('_Removed.'):
                    removed.append(package.replace('_Removed.', ''))
                if package.endswith('_Added.'):
                    added.append(package.replace('_Added.', ''))

            # Remove packages that not exists in the repository.
            if removed:
                packages = [pkg for pkg in packages if not pkg.endswith('_Removed.')]
                remove = RemovePackages(removed, self.options)
                remove.remove(upgrade=True)

            if added:
                packages = sorted([pkg for pkg in packages if not pkg.endswith('_Added.')])
                packages = added + packages
                ordered = False

            packages = self.choose.packages(self.data, packages, command, ordered)

            if not packages:
                print('\nEverything is up-to-date!\n')
                sys.exit(0)

            if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                install_bin = Packages(self.repository, self.data, packages, self.options, mode=command)
                install_bin.execute()
            else:
                install_sbo = Slackbuilds(self.repository, self.data, packages, self.options, mode=command)
                install_sbo.execute()

            self._is_kernel_upgrade(kernel_generic_current_package)

        sys.exit(0)

    def _is_kernel_upgrade(self, kernel_generic_current_package: str) -> None:
        """Compare current and installed kernel package.

        Args:
            kernel_generic_current_package (str): Kernel-generic package
        """
        kernel_generic_new_package: str = self.utils.is_package_installed('kernel-generic')
        if kernel_generic_current_package != kernel_generic_new_package:
            if self.bootloader_command:
                self._bootloader_update()
            else:
                self._kernel_image_message()

    def _kernel_image_message(self) -> None:
        """Print a warning kernel upgrade message.
        """
        print(f"\n{self.red}Warning!{self.endc} Your kernel image looks like to have been upgraded!\n"
              "Please update the bootloader with the new parameters of the upgraded kernel.\n"
              "See: lilo, eliloconfig or grub-mkconfig -o /boot/grub/grub.cfg,\n"
              "depending on how you have your system configured.\n")

    def _bootloader_update(self) -> None:
        print(f'\nYour kernel image upgraded, do you want to run this command:\n'
              f'\n{self.green}    {self.bootloader_command}{self.endc}\n')
        self.views.question()
        self.multi_process.process(self.bootloader_command)

    def repo_info(self) -> NoReturn:
        """Print repositories information.

        Raises:
            SystemExit: Exit code 0.
        """
        repo = RepoInfo(self.options, self.repository)
        repo.info()
        sys.exit(0)

    def edit_configs(self) -> NoReturn:
        """Edit configurations via dialog box.

        Raises:
            SystemExit: Exit code 0.
        """
        self.is_root()
        form_configs = FormConfigs()
        form_configs.edit()
        sys.exit(0)

    def clean_tmp(self) -> NoReturn:
        """Remove all files and directories from tmp.

        Raises:
            SystemExit: Exit code 0.
        """
        self.is_root()
        clean = Cleanings()
        clean.tmp()
        sys.exit(0)

    @staticmethod
    def self_check() -> NoReturn:
        """Check for slpkg updates.
        Returns:
            NoReturn
        """
        check_self_update()
        sys.exit(0)

    def build(self, packages: list[str]) -> NoReturn:
        """Build slackbuilds with dependencies without install.

        Raises:
            SystemExit: Exit code 0.
        """
        self.is_root()
        command: str = Run.build.__name__

        self.data = self.load_data.load(self.repository)
        build_packages = self.is_file_list_packages(packages)
        build_packages = self.utils.case_insensitive_pattern_matching(build_packages, self.data, self.options)

        if self.options.get('option_select'):
            build_packages = self.choose.packages(self.data, build_packages, command)

        self.check.is_package_exists(build_packages, self.data)

        build = Slackbuilds(
            self.repository, self.data, build_packages, self.options, mode=command
        )
        build.execute()

        sys.exit(0)

    def install(self, packages: list[str]) -> NoReturn:
        """Build and install packages with dependencies.

        Raises:
            SystemExit: Exit code 0.
        """
        self.is_root()
        command: str = Run.install.__name__
        kernel_generic_current_package: str = self.utils.is_package_installed('kernel-generic')

        self.data = self.load_data.load(self.repository)
        install_packages = self.is_file_list_packages(packages)
        install_packages = self.utils.case_insensitive_pattern_matching(install_packages, self.data, self.options)

        if self.options.get('option_select'):
            install_packages = self.choose.packages(self.data, install_packages, command)

        self.check.is_package_exists(install_packages, self.data)

        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            install_bin = Packages(self.repository, self.data, install_packages, self.options, mode=command)
            install_bin.execute()
        else:
            install_sbo = Slackbuilds(self.repository, self.data, install_packages, self.options, mode=command)
            install_sbo.execute()

        self._is_kernel_upgrade(kernel_generic_current_package)

        sys.exit(0)

    def remove(self, packages: list[str]) -> NoReturn:
        """Remove packages with dependencies.

        Raises:
            SystemExit: Exit code 0.
        """
        self.is_root()
        command: str = Run.remove.__name__

        remove_packages: list[str] = self.is_file_list_packages(packages)

        if self.options.get('option_select'):
            remove_packages = self.choose.packages({}, remove_packages, command)

        self.check.is_package_installed(remove_packages)

        remove = RemovePackages(remove_packages, self.options)
        remove.remove()
        sys.exit(0)

    def download(self, packages: list[str]) -> NoReturn:
        """Download only packages.

        Raises:
            SystemExit: Exit code 0.
        """
        command: str = Run.download.__name__

        self.data = self.load_data.load(self.repository)
        download_packages = self.is_file_list_packages(packages)
        download_packages = self.utils.case_insensitive_pattern_matching(download_packages, self.data, self.options)

        if self.options.get('option_select'):
            download_packages = self.choose.packages(self.data, download_packages, command)

        self.check.is_package_exists(download_packages, self.data)
        down_only = DownloadOnly(self.directory, self.options, self.data, self.repository)
        down_only.packages(download_packages)
        sys.exit(0)

    def list_installed(self, packages: list[str]) -> NoReturn:
        """Find installed packages.

        Raises:
            SystemExit: Exit code 0.
        """
        command: str = Run.list_installed.__name__

        ls_packages: list[str] = self.is_file_list_packages(packages)

        if self.options.get('option_select'):
            data: dict[str, dict[str, str]] = {}  # No repository data needed for installed packages.
            ls_packages = self.choose.packages(data, ls_packages, command)

        ls = ListInstalled(self.options, ls_packages)

        ls.installed()
        sys.exit(0)

    def info_package(self, packages: list[str]) -> NoReturn:
        """View package information.

        Raises:
            SystemExit: Exit code 0.
        """
        command: str = Run.info_package.__name__

        self.data = self.load_data.load(self.repository)
        info_packages = self.is_file_list_packages(packages)
        info_packages = self.utils.case_insensitive_pattern_matching(info_packages, self.data, self.options)

        if self.options.get('option_select'):
            info_packages = self.choose.packages(self.data, info_packages, command)

        self.check.is_package_exists(info_packages, self.data)

        view = InfoPackage(self.options, self.repository)

        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            view.package(self.data, info_packages)
        else:
            view.slackbuild(self.data, info_packages)
        sys.exit(0)

    def search(self, packages: list[str]) -> NoReturn:
        """Search packages from the repositories.

        Raises:
            SystemExit: Exit code 0.
        """
        command: str = Run.search.__name__
        self.data = self.load_data.load(self.repository)

        search_packages: list[str] = self.is_file_list_packages(packages)

        if self.options.get('option_select'):
            search_packages = self.choose.packages(self.data, search_packages, command)

        pkgs = SearchPackage(self.options, search_packages, self.data, self.repository)
        pkgs.search()
        sys.exit(0)

    def dependees(self, packages: list[str]) -> NoReturn:
        """View packages that depend on other packages.

        Raises:
            SystemExit: Exit code 0.
        """
        command: str = Run.dependees.__name__

        self.data = self.load_data.load(self.repository)
        dependees_packages = self.is_file_list_packages(packages)
        dependees_packages = self.utils.case_insensitive_pattern_matching(dependees_packages, self.data, self.options)

        if self.options.get('option_select'):
            dependees_packages = self.choose.packages(self.data, dependees_packages, command)

        self.check.is_package_exists(dependees_packages, self.data)

        dependees = Dependees(self.data, dependees_packages, self.options)
        dependees.find()
        sys.exit(0)

    def tracking(self, packages: list[str]) -> NoReturn:
        """Tracking package dependencies.

        Raises:
            SystemExit: Exit code 0.
        """
        command: str = Run.tracking.__name__

        self.data = self.load_data.load(self.repository)
        tracking_packages = self.is_file_list_packages(packages)
        tracking_packages = self.utils.case_insensitive_pattern_matching(tracking_packages, self.data, self.options)

        if self.options.get('option_select'):
            tracking_packages = self.choose.packages(self.data, tracking_packages, command)

        self.check.is_package_exists(tracking_packages, self.data)

        tracking = Tracking(self.data, tracking_packages, self.options, self.repository)
        tracking.package()
        sys.exit(0)

    def changelog_print(self, query: str) -> NoReturn:
        """Prints repository changelog.
        """
        changelog_manager = Changelog()
        changelog_manager.changelog(query, self.repository)
        sys.exit(0)

    @staticmethod
    def version() -> NoReturn:
        """Print program version and exit.

        Raises:
            SystemExit: Exit code 0.
        """
        version = Version()
        version.view()
        sys.exit(0)


def check_for_repositories(repository: str, args: argparse.Namespace, parser: argparse.ArgumentParser, option_args: dict[str, bool]) -> None:
    """Manages repository rules and validation."""
    repos = Repositories()
    repo_config = repos.repositories.get(repository)
    if repository != '*' and repository is not None and repository != '':
        if repo_config is None:
            parser.error(f"Repository '{repository}' does not exist.")
        elif not repo_config.get('enable'):
            parser.error(f"Repository '{repository}' is not enabled.")

    if repository == '*' and not (args.command == 'search' or (args.command == 'upgrade' and option_args.get('option_check'))):
        parser.error(f"Repository '{repository}' is not allowed with this command.")

    if args.command == 'build' and repository and repository not in list(repos.repositories)[:2]:
        parser.error(f"Repository '{repository}' is not allowed with this command.")


class CustomCommandsFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter that produces exactly the requested output format:
    - Main help shows: slpkg <COMMAND> [PACKAGES] [OPTIONS]
    - Command help shows: slpkg install [PACKAGE ...] [OPTIONS]
    - Clean command listing with proper indentation
    """

    def __init__(self, prog: str, indent_increment: int = 1, max_help_position: int = 18, width: Union[int, None] = None) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)
        self._subcommands = ['update', 'upgrade', 'config', 'repo-info', 'clean-tmp',
                             'self-check', 'build', 'install', 'remove', 'download',
                             'list', 'info', 'search', 'dependees', 'tracking', 'version']
        self.custom_usage = f"{self._prog} <COMMAND> [PACKAGES] [OPTIONS]"

    def add_usage(self, usage: Union[str, None], actions: list[argparse.Action], groups: list[argparse._ArgumentGroup], prefix: Union[str, None] = None) -> None:  # type: ignore
        """Custom usage formatting that handles both main and command help"""
        if prefix is None:
            prefix = f'{config_load.bold}Usage{config_load.endc}: '

        if 'help' in sys.argv[1:] and len(sys.argv) == 2:
            usage = self.custom_usage
        elif any(arg in self._subcommands for arg in sys.argv[1:]) and len(sys.argv[1:]) > 2:
            usage = self.custom_usage
        elif len(sys.argv) == 2 and any(arg == '-h' or arg == '--help' for arg in sys.argv[1:]):  # pylint: disable=[R1714]
            usage = self.custom_usage
        elif len(sys.argv) == 1:
            usage = self.custom_usage
        elif any(arg not in self._subcommands and arg != '-h' and arg != '--help' and arg != 'help' for arg in sys.argv[1:]):
            usage = self.custom_usage

        return super().add_usage(usage, actions, groups, prefix)  # type: ignore[arg-type]

    def _format_action(self, action: list[argparse.Action]) -> Union[str, None]:  # type: ignore
        """Remove command choices and format subcommands cleanly"""
        if isinstance(action, argparse._SubParsersAction) and action.dest == 'command':  # pylint: disable=[W0212]
            # Store original values
            orig_help = action.help
            orig_choices = action.choices

            # Temporarily modify for clean output
            action.help = None
            action.choices = None  # type: ignore

            # Get formatted string
            result = super()._format_action(action)

            # Restore original values
            action.help = orig_help
            action.choices = orig_choices

            # Remove all unwanted artifacts
            result = re.sub(r'^ *command.*\n', '', result, flags=re.MULTILINE)
            result = re.sub(r'\{.*}.*\n', '', result, flags=re.MULTILINE)
            return result

        return super()._format_action(action)  # type: ignore[arg-type]

    def _format_action_invocation(self, action: argparse.Action) -> Union[str, None]:  # type: ignore
        """Ensure consistent 10-space indentation for commands"""
        if not action.option_strings and not isinstance(action, argparse._SubParsersAction):  # pylint: disable=[W0212]
            metavar = self._format_args(action, self._get_default_metavar_for_positional(action))
            return metavar
        return super()._format_action_invocation(action)

    def format_help(self) -> str:
        """Final help text processing"""
        help_text = super().format_help()

        # Replace section headers
        help_text = help_text.replace(
            'positional arguments:',
            f'{config_load.bold}Commands:{config_load.endc}'
        )

        # Clean up any remaining artifacts
        help_text = re.sub(r'\{.*}.*\n', '', help_text)  # Remove {command1,command2} line
        help_text = re.sub(r'command\n', '', help_text)  # Remove command line

        return help_text


def main() -> None:  # pylint: disable=[R0912,R0914,R0915]
    """Main control function for argparse arguments."""
    error = Errors()

    if config_load.error_log_file.is_file():
        config_load.error_log_file.unlink()

    logging.basicConfig(filename=config_load.error_log_file,
                        level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    commands_that_use_repos = [
        'install', 'build', 'download', 'info', 'search',
        'dependees', 'tracking', 'update', 'upgrade', 'repo-info'
    ]

    commands_that_use_packages = [
        'install', 'remove', 'build', 'download', 'info', 'search', 'list', 'dependees', 'tracking'
    ]

    yes_parser = argparse.ArgumentParser(add_help=False)
    yes_group = yes_parser.add_argument_group()
    yes_group.add_argument('-y', '--yes', action='store_true', dest='option_yes', help='Answer Yes to all questions.')

    check_parser = argparse.ArgumentParser(add_help=False)
    check_group = check_parser.add_argument_group()
    check_group.add_argument('-c', '--check', action='store_true', dest='option_check', help='Check a procedure before you run it.')

    resolve_off_parser = argparse.ArgumentParser(add_help=False)
    resolve_off_group = resolve_off_parser.add_argument_group()
    resolve_off_group.add_argument('-O', '--resolve-off', action='store_true', dest='option_resolve_off', help='Turns off dependency resolving.')

    reinstall_parser = argparse.ArgumentParser(add_help=False)
    reinstall_group = reinstall_parser.add_argument_group()
    reinstall_group.add_argument('-r', '--reinstall', action='store_true', dest='option_reinstall', help='Upgrade packages of the same version.')

    skip_install_parser = argparse.ArgumentParser(add_help=False)
    skip_install_group = skip_install_parser.add_argument_group()
    skip_install_group.add_argument('-k', '--skip-installed', action='store_true', dest='option_skip_installed', help='Skip installed packages during the building or installation progress.')

    fetch_parser = argparse.ArgumentParser(add_help=False)
    fetch_group = fetch_parser.add_argument_group()
    fetch_group.add_argument('-f', '--fetch', action='store_true', dest='option_fetch', help='Fetch the fastest and slower mirror.')

    full_reverse_parser = argparse.ArgumentParser(add_help=False)
    full_reverse_group = full_reverse_parser.add_argument_group()
    full_reverse_group.add_argument('-E', '--full-reverse', action='store_true', dest='option_full_reverse', help='Display the full reverse dependency tree.')

    select_parser = argparse.ArgumentParser(add_help=False)
    select_group = select_parser.add_argument_group()
    select_group.add_argument('-S', '--select', action='store_true', dest='option_select', help='Matching and select packages with selector or dialog.')

    progress_bar_parser = argparse.ArgumentParser(add_help=False)
    progress_bar_group = progress_bar_parser.add_argument_group()
    progress_bar_group.add_argument('-B', '--progress-bar', action='store_true', dest='option_progress_bar', help='Display static progress bar instead of process execute.')

    pkg_version_parser = argparse.ArgumentParser(add_help=False)
    pkg_version_group = pkg_version_parser.add_argument_group()
    pkg_version_group.add_argument('-p', '--pkg-version', action='store_true', dest='option_pkg_version', help='Print the repository package version.')

    parallel_parser = argparse.ArgumentParser(add_help=False)
    parallel_group = parallel_parser.add_argument_group()
    parallel_group.add_argument('-P', '--parallel', action='store_true', dest='option_parallel', help='Enable download files in parallel.')

    no_case_parser = argparse.ArgumentParser(add_help=False)
    no_case_group = no_case_parser.add_argument_group()
    no_case_group.add_argument('-m', '--no-case', action='store_true', dest='option_no_case', help='Case-insensitive pattern matching.')

    color_parser = argparse.ArgumentParser(add_help=False)
    color_group = color_parser.add_argument_group()
    color_group.add_argument('-x', '--color', choices=['on', 'off', 'ON', 'OFF'], metavar='<ON/OFF>', dest='option_color', help='Switch on or off color output.')

    dialog_parser = argparse.ArgumentParser(add_help=False)
    dialog_group = dialog_parser.add_argument_group()
    dialog_group.add_argument('-D', '--dialog', action='store_true', dest='option_dialog', help='Enable dialog-based interface instead, terminal selector.')

    description_parser = argparse.ArgumentParser(add_help=False)
    description_group = description_parser.add_argument_group()
    description_group.add_argument('-t', '--desc', action='store_true', dest='option_pkg_description', help='Print the package description.')

    repository_parser = argparse.ArgumentParser(add_help=False)
    repository_group = repository_parser.add_argument_group()
    repository_group.add_argument('-o', '--repository', metavar='<NAME>', dest='repository', help='Change repository you want to work.')

    directory_parser = argparse.ArgumentParser(add_help=False)
    directory_group = directory_parser.add_argument_group()
    directory_group.add_argument('-z', '--directory', metavar='<PATH>', dest='directory', help='Download files to a specific path.')

    changelog_parser = argparse.ArgumentParser(add_help=False)
    changelog_group = changelog_parser.add_argument_group()
    changelog_group.add_argument('-q', '--query', metavar='<QUERY>', dest='query', help='Filter results based on a search query.')

    # --- Main Parser ---
    # custom_usage_message: str = "%(prog)s <COMMAND> [PACKAGES] [OPTIONS]"
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='slpkg',
        description="Description:\n  Package manager utility for Slackware Linux.",
        # usage=custom_usage_message,
        formatter_class=CustomCommandsFormatter,
        epilog='For command-specific help: slpkg help <COMMAND> or use manpage.',
        add_help=False
    )

    subparsers = parser.add_subparsers(
        dest='command',
        # help=f'{bold}Available Commands{endc}'
    )
    subparsers.required = True  # Makes subcommand selection mandatory

    subparsers.add_parser('update', parents=[check_parser, color_parser, repository_parser], help='Sync repository database with local.')
    subparsers.add_parser('upgrade', parents=[yes_parser, check_parser, resolve_off_parser, progress_bar_parser, parallel_parser, color_parser, repository_parser],
                          help='Upgrade the installed packages.')
    subparsers.add_parser('config', parents=[], help='Edit the configuration file.')
    subparsers.add_parser('repo-info', parents=[fetch_parser, color_parser, repository_parser], help='Display the repositories information.')
    subparsers.add_parser('clean-tmp', parents=[], help='Clean old downloaded packages and scripts.')
    subparsers.add_parser('self-check', parents=[], help='Checks for available slpkg updates.')

    build_parser = subparsers.add_parser('build', parents=[yes_parser, resolve_off_parser, skip_install_parser, progress_bar_parser, parallel_parser, no_case_parser, select_parser, dialog_parser, color_parser,
                                         repository_parser],
                                         help='Build SBo scripts without install it.')
    build_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to build.')

    install_parser = subparsers.add_parser('install', parents=[yes_parser, reinstall_parser, resolve_off_parser, skip_install_parser, progress_bar_parser, parallel_parser, no_case_parser,
                                           select_parser, dialog_parser, color_parser, repository_parser],
                                           help='Build/install SBo scripts or binary packages.')
    install_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to install.')

    remove_parser = subparsers.add_parser('remove', parents=[yes_parser, resolve_off_parser, select_parser, dialog_parser, progress_bar_parser, color_parser],
                                          help='Remove installed packages with dependencies.')
    remove_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to remove.')

    download_parser = subparsers.add_parser('download', parents=[yes_parser, no_case_parser, select_parser, dialog_parser, color_parser, directory_parser, repository_parser],
                                            help='Download only the packages without build or install.')
    download_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to download.')

    list_parser = subparsers.add_parser('list', parents=[no_case_parser, description_parser, select_parser, dialog_parser, color_parser,], help='Matching and display list of the installed packages.')
    list_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to display.')

    info_parser = subparsers.add_parser('info', parents=[select_parser, dialog_parser, color_parser, repository_parser], help='Display package information by the repository.')
    info_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to display information for.')

    search_parser = subparsers.add_parser('search', parents=[no_case_parser, pkg_version_parser, description_parser, select_parser, dialog_parser, color_parser, repository_parser],
                                          help='This will match each package by the repository.')
    search_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to search for.')

    dependees_parser = subparsers.add_parser('dependees', parents=[no_case_parser, pkg_version_parser, full_reverse_parser, select_parser, dialog_parser, color_parser, repository_parser],
                                             help='Display packages that depend on other packages.')
    dependees_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names for dependencies.')

    tracking_parser = subparsers.add_parser('tracking', parents=[no_case_parser, pkg_version_parser, select_parser, dialog_parser, color_parser, repository_parser],
                                            help='Display and tracking the packages dependencies.')
    tracking_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names for tracking.')

    subparsers.add_parser('changelog', parents=[repository_parser, changelog_parser, color_parser], help='Display the changelog for a given repository.')

    _ = subparsers.add_parser('version', parents=[], help='Show version and exit.')

    # 'help' command is now a subparser
    help_parser = subparsers.add_parser('help', parents=[], help='Show this help message and exit.')
    help_parser.add_argument('command_for_help', nargs='?', help='Show help for a specific command.')

    if len(sys.argv) == 1:
        parser.error('Missing command. Use "help" for more information.')

    if len(sys.argv) == 2 and any(arg == '-h' or arg == '--help' for arg in sys.argv[1:]):  # pylint: disable=[R1714]
        # if len(sys.argv) == 2 and sys.argv[1] in ('-h', '--help'):
        parser.error('Missing command. Use "help" for more information.')

    args: argparse.Namespace = parser.parse_args()

    # Update configs from argparse args.
    config_load.update_from_args(args)

    # Retrieve repository and directory - now they are in args.repository/args.directory
    # Ensure they are not None before assigning, default to empty string or /tmp/slpkg/
    repository = args.repository if hasattr(args, 'repository') and args.repository is not None else ''
    directory = args.directory if hasattr(args, 'directory') and args.directory is not None else '/tmp/slpkg/'
    query = args.query if hasattr(args, 'query') and args.query is not None else ''

    # option_args can now be created directly from args
    option_args: dict[str, bool] = {k: v for k, v in args.__dict__.items() if k.startswith('option_')}
    # Manually add repository/directory if they were provided as options and are not defaults
    if repository:  # if repository is a non-empty string
        option_args['option_repository'] = True
    if directory != '/tmp/slpkg/':  # Check if it changed from the default
        option_args['option_directory'] = True

    # --- Check: Call check_for_repositories only for commands that require it ---
    if args.command in commands_that_use_repos:
        check_for_repositories(repository, args, parser, option_args)

    run = Run(option_args, repository, directory)

    try:
        command = args.command

        command_map: dict[str, Callable[..., Any]] = {
            'install': run.install,
            'update': run.update,
            'upgrade': run.upgrade,
            'config': run.edit_configs,
            'repo-info': run.repo_info,
            'clean-tmp': run.clean_tmp,
            'self-check': run.self_check,
            'build': run.build,
            'remove': run.remove,
            'download': run.download,
            'list': run.list_installed,
            'info': run.info_package,
            'search': run.search,
            'dependees': run.dependees,
            'tracking': run.tracking,
            'version': run.version
        }

        if command in commands_that_use_packages:
            command_map[args.command](args.packages)
        if command == 'changelog':
            run.changelog_print(query)
        elif command == 'help':
            # Specific handling for the 'help' command
            if args.command_for_help:
                subcommand = args.command_for_help
                # This is a bit "hacky" but effective to make the subparser print its help.
                # We force argparse to parse with the command and '--help'.
                try:
                    parser.parse_args([subcommand, '--help'])
                except SystemExit:
                    # argparse.error or action='help' calls sys.exit().
                    # We catch it so the main program doesn't stop prematurely.
                    pass
            else:
                parser.print_help()  # Display general help
        else:
            command_map[args.command]()

    except (KeyboardInterrupt, EOFError):
        print('\nOperation canceled by the user.')
        sys.exit(1)
    except KeyError as e:
        logging.error('Exception occurred', exc_info=True)
        message: str = f'An error occurred: {e}. Check the log {config_load.error_log_file} file.'
        error.raise_error_message(message=message, exit_status=1)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError) as err:
        print('\nOperation canceled by the user.')
        raise SystemExit(1) from err

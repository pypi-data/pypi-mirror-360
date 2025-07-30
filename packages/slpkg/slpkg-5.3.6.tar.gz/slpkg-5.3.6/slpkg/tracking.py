#!/usr/bin/python3
# -*- coding: utf-8 -*-


from slpkg.binaries.required import Required
from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.sbos.dependencies import Requires
from slpkg.utilities import Utilities


class Tracking:  # pylint: disable=[R0902]
    """Tracking of the package dependencies."""

    def __init__(self, data: dict[str, dict[str, str]], packages: list[str], options: dict[str, bool],
                 repository: str) -> None:
        self.data = data
        self.packages = packages
        self.options = options
        self.repository = repository

        self.view_missing_deps = config_load.view_missing_deps
        self.bold = config_load.bold
        self.grey = config_load.grey
        self.red = config_load.red
        self.endc = config_load.endc

        self.utils = Utilities()
        self.repos = Repositories()

        self.package_version: str = ''
        self.package_dependency_version: str = ''
        self.package_requires: list[str] = []
        self.package_line: str = ''
        self.require_line: str = ''
        self.count_requires: int = 0
        self.require_length: int = 0

        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)

    def package(self) -> None:
        """Call methods and prints the results."""
        self.view_the_title()

        for package in self.packages:
            self.count_requires = 0

            self.set_the_package_line(package)
            self.set_package_requires(package)
            self.view_the_main_package()
            self.view_no_dependencies()

            for require in self.package_requires:
                self.count_requires += 1

                self.set_the_package_require_line(require)
                self.view_requires()

            self.view_summary_of_tracking(package)

    def view_the_title(self) -> None:
        """Print the title."""
        print("The list below shows the packages with dependencies:\n")
        self.packages = self.utils.apply_package_pattern(self.data, self.packages)

    def view_the_main_package(self) -> None:
        """Print the main package."""
        print(f'{self.package_line}:')

    def view_requires(self) -> None:
        """Print the package requires."""
        print(f"{'':>2}{self.require_line}")

    def view_no_dependencies(self) -> None:
        """Print the message 'No dependencies'."""
        if not self.package_requires:
            print(f"{'':>1}No dependencies")

    def set_the_package_line(self, package: str) -> None:
        """Set for package line.

        Args:
            package (str): Package name.
        """
        self.package_line = f'{self.bold}{package}{self.endc}'
        if self.option_for_pkg_version:
            self.set_package_version(package)
            self.package_line = f'{self.bold}{package} {self.package_version}{self.endc}'

    def set_the_package_require_line(self, require: str) -> None:
        """Set the requires.

        Args:
            require (str): Require name.
        """
        color: str = ''
        if require not in self.data:
            color = self.red

        self.require_line = f'{color}{require}{self.endc}'

        if self.option_for_pkg_version:
            self.set_package_dependency_version(require)
            self.require_line = (f'{color}{require:<{self.require_length}}{self.endc}'
                                 f'{self.package_dependency_version}')

    def set_package_dependency_version(self, require: str) -> None:
        """Set the dependency version.

        Args:
            require (str): Description
        """
        self.package_dependency_version = f"{'':>1}(not included)"
        if self.data.get(require):
            self.package_dependency_version = (
                f"{'':>1}{self.data[require]['version']}"
            )

    def set_package_version(self, package: str) -> None:
        """Set the main package version.

        Args:
            package (str): Package name.
        """
        self.package_version = self.data[package]['version']

    def set_package_requires(self, package: str) -> None:
        """Set for the package require.

        Args:
            package (str): Package name.
        """
        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            self.package_requires = list(Required(self.data, package, self.options).resolve())
        else:
            self.package_requires = list(Requires(self.data, package, self.options).resolve())

        if self.package_requires:
            if self.view_missing_deps:
                requires: list[str] = list(self.data[package]['requires'])
                for req in requires:
                    if req not in self.data:
                        self.package_requires.append(req)
            self.require_length = max(len(name) for name in self.package_requires)

    def view_summary_of_tracking(self, package: str) -> None:
        """Print the summary.

        Args:
            package (str): Package name.
        """
        print(f'\n{self.grey}{self.count_requires} dependencies for {package}{self.endc}\n')

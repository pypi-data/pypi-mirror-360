#!/usr/bin/python3
# -*- coding: utf-8 -*-


from typing import Any, cast

from slpkg.repositories import Repositories
from slpkg.utilities import Utilities


class Required:
    """Create a tuple of dependencies with the right order to install."""

    __slots__ = ('data', 'name', 'flags', 'repos', 'utils',
                 'full_requires', 'repository_packages',
                 'option_for_resolve_off')

    def __init__(self, data: dict[str, dict[str, str]], name: str, options: dict[str, bool]) -> None:
        self.data = data
        self.name = name
        self.utils = Utilities()
        self.repos = Repositories()

        # Reads about how requires are listed, full listed is True
        # and normal listed is false.
        self.full_requires: bool = False
        if self.repos.repos_information.is_file():
            info = cast(dict[str, dict[str, Any]], self.utils.read_json_file(self.repos.repos_information))
            repo_name: str = data[name]['repo']
            if info.get(repo_name):
                self.full_requires = info[repo_name].get('full_requires', False)

        self.option_for_resolve_off: bool = options.get('option_resolve_off', False)

    def resolve(self) -> tuple[str, ...]:
        """Resolve the dependencies."""
        dependencies: tuple[str, ...] = ()
        if not self.option_for_resolve_off:
            requires: list[str] = self.remove_deps(cast(list[str], self.data[self.name]['requires']))

            # Resolve dependencies for some special repos.
            if not self.full_requires:
                for require in requires:

                    sub_requires: list[str] = self.remove_deps(cast(list[str], self.data[require]['requires']))
                    for sub in sub_requires:
                        if sub not in requires:
                            requires.append(sub)

            requires.reverse()
            dependencies = tuple(dict.fromkeys(requires))

        return dependencies

    def remove_deps(self, requires: list[str]) -> list[str]:
        """Remove requirements that not in the repository.

        Args:
            requires (list[str]): List of requires.

        Returns:
            list: List of packages name.
        """
        return [req for req in requires if req in self.data]

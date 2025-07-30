#!/usr/bin/python3
# -*- coding: utf-8 -*-


from typing import cast


class Requires:
    """Create a tuple with package dependencies."""

    __slots__ = (
        'data', 'name', 'options', 'option_for_resolve_off'
    )

    def __init__(self, data: dict[str, dict[str, str]], name: str, options: dict[str, bool]) -> None:
        self.data = data
        self.name = name

        self.option_for_resolve_off: bool = options.get('option_resolve_off', False)

    def resolve(self) -> tuple[str, ...]:
        """Resolve the dependencies.

        Return package dependencies in the right order.
        """
        dependencies: tuple[str, ...] = ()

        if not self.option_for_resolve_off:
            requires: list[str] = self.remove_deps(cast(list[str], self.data[self.name]['requires']))

            for require in requires:
                sub_requires: list[str] = self.remove_deps(cast(list[str], self.data[require]['requires']))

                for sub in sub_requires:
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

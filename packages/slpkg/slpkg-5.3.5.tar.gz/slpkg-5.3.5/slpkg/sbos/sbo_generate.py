#!/usr/bin/python3
# -*- coding: utf-8 -*-


from pathlib import Path

from slpkg.views.view_process import ViewProcess


class SBoGenerate:
    """Generating the SLACKBUILDS.TXT file."""

    def __init__(self) -> None:
        self.view_process = ViewProcess()

    def slackbuild_file(self, repo_path: Path, repo_slackbuild_txt: str) -> None:  # pylint: disable=[R0914]
        """Create a SLACKBUILDS.TXT file.

        Args:
            repo_path (Path): Path to file.
            repo_slackbuild_txt (str): Name of file to create.
        """
        # slackbuild.info variables
        info_var: dict[int, str] = {
            1: 'PRGNAM=',
            2: 'VERSION=',
            3: 'HOMEPAGE=',
            4: 'DOWNLOAD=',
            5: 'MD5SUM=',
            6: 'DOWNLOAD_x86_64=',
            7: 'MD5SUM_x86_64=',
            8: 'REQUIRES=',
            9: 'MAINTAINER=',
            10: 'EMAIL='
        }

        self.view_process.message(f'Generating the {repo_slackbuild_txt} file')

        with open(Path(repo_path, repo_slackbuild_txt), 'w', encoding='utf-8') as sbo:
            for path in repo_path.glob('**/*'):
                if path.name.endswith('.info'):
                    sbo_path = Path('/'.join(str(path).split('/')[:-1]))

                    name: str = str(path).split('/')[-2]
                    location: str = str(Path('/'.join(str(path).split('/')[-3:-1])))
                    files: str = ' '.join([file.name for file in list(sbo_path.iterdir())])

                    version: str = (
                        ' '.join([var.strip() for var in self.read_info_file(
                            path, info_var[2], info_var[3])])[len(info_var[2]):].replace('"', ''))

                    download: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[4], info_var[5])])[len(info_var[4]):].replace('"', ''))

                    download_x86_64: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[6], info_var[7])])[len(info_var[6]):].replace('"', ''))

                    md5sum: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[5], info_var[6])])[len(info_var[5]):].replace('"', ''))

                    md5sum_x86_64: str = (
                        ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                            path, info_var[7], info_var[8])])[len(info_var[7]):].replace('"', ''))

                    requires: str = (' '.join(list(self.read_info_file(
                        path, info_var[8], info_var[9])))[len(info_var[8]):].replace('"', ''))

                    short_description: str = self.read_short_description(sbo_path, name)

                    sbo.write(f'SLACKBUILD NAME: {name}\n')
                    sbo.write(f'SLACKBUILD LOCATION: ./{location}\n')
                    sbo.write(f'SLACKBUILD FILES: {files}\n')
                    sbo.write(f'SLACKBUILD VERSION: {version}\n')
                    sbo.write(f'SLACKBUILD DOWNLOAD: {download}\n')
                    sbo.write(f'SLACKBUILD DOWNLOAD_x86_64: {download_x86_64}\n')
                    sbo.write(f'SLACKBUILD MD5SUM: {md5sum}\n')
                    sbo.write(f'SLACKBUILD MD5SUM_x86_64: {md5sum_x86_64}\n')
                    sbo.write(f'SLACKBUILD REQUIRES: {requires}\n')
                    sbo.write(f'SLACKBUILD SHORT DESCRIPTION: {short_description}\n')
                    sbo.write('\n')

        self.view_process.done()
        print()

    @staticmethod
    def read_short_description(path: Path, name: str) -> str:
        """Return the short description from slack-desc file.

        Args:
            path (Path): Path to file.
            name (str): Slackbuild name.

        Returns:
            str: Short description
        """
        slack_desc: Path = Path(path, 'slack-desc')
        if slack_desc.is_file():
            with open(slack_desc, 'r', encoding='utf-8') as f:
                slack = f.readlines()

            for line in slack:
                pattern: str = f'{name}: {name}'
                if line.startswith(pattern):
                    return line[len(name) + 1:].strip()
        return ''

    @staticmethod
    def read_info_file(info_file: Path, start: str, stop: str) -> list[str]:
        """Read the .info file and return the line between to variables.

        Args:
            info_file (Path): Slackbuild file name.
            start (str): Variable name to start.
            stop (str): Variable name to stop.

        Returns:
            list[str]: Results in list.
        """
        begin = end = 0
        with open(info_file, 'r', encoding='utf-8') as f:
            info = f.read().splitlines()

        for index, line in enumerate(info):
            if line.startswith(start):
                begin = index
            if line.startswith(stop):
                end = index
                break

        return info[begin:end]

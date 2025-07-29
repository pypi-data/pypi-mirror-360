#!/bin/python3
# -*- coding: utf-8 -*-

import sys
from typing import NoReturn

from sbpkg.config import Config
from sbpkg.metadata import Metadata


class CliHelp(Config):
    """CLI help menu.
    """

    def __init__(self) -> None:
        super().__init__()

        self.prgnam: str = Metadata.__prgnam__
        self.description: str = Metadata.__description__

    def print_help(self) -> NoReturn:
        """Print cli help message.
        """
        cli_help: str = (
            f'Usage: {self.bold}{self.prgnam} [COMMAND] [OPTIONS] <packages>{self.endc}\n\n'
            f'  {self.description}\n\n'
            'Command arguments:\n'
            f'  -u, {self.bold}--update{self.endc}                     Synchronizes the repository database\n'
            f"{'':>35}with your local database.\n"
            f'  -U, {self.bold}--upgrade{self.endc}                    Checking and upgrade the SBo packages on\n'
            f"{'':>35}the system.\n"
            f'  -C, {self.bold}--clean-tmp{self.endc}                  Clean the tmp folder from old downloaded\n'
            f"{'':>35}files and sources.\n"
            f"  -L, {self.bold}--repo-clog{self.endc} <packages>       Display repos Changelog or match\n"
            f"{'':>35}packages to see their history.\n"
            f"  -b, {self.bold}--build{self.endc} <packages>           It builds only packages without install.\n"
            f"  -i, {self.bold}--install{self.endc} <packages>         Exactly as the '-b' command, but install\n"
            f"{'':>35}the built packages.\n"
            f'  -R, {self.bold}--remove{self.endc} <packages>          Remove packages with dependencies that\n'
            f"{'':>35}previously installed with the '-i' command.\n"
            f'  -q, {self.bold}--requires{self.endc} <packages>        List of the package dependencies.\n'
            f'  -e, {self.bold}--dependees{self.endc} <packages>       List of the packages that depends\n'
            f"{'':>35}on a package.\n"
            f'  -s, {self.bold}--search{self.endc} <packages>          Matching for packages in the database\n'
            f"{'':>35}based on name and print the package\n"
            f"{'':>35}and the description.\n"
            f'  -f, {self.bold}--find-installed{self.endc} <packages>  Find and print all SBo installed packages.\n'
            f"{'':>35}with dependencies.\n"
            f'  -w, {self.bold}--download-only{self.endc} <packages>   Download only packages without build\n'
            f"{'':>35}or install them.\n"
            f'  -p, {self.bold}--pkg-info{self.endc} <packages>        Display information about the packages.\n'
            f'  -d, {self.bold}--display{self.endc} <packages>         Select and print the contents of the\n'
            f"{'':>35}files, such as PRGNAM.SlackBuild, README,\n"
            f"{'':>35}PRGNAM.info and etc.\n\n"

            'Options:\n'
            '  -n, --no-confirm                 Ignore any message confirmation.\n'
            f"{'':>35}Bad idea to do this unless you want\n"
            f"{'':>35}to run sbpkg from a script.\n"
            '  -P, --parallel                   Download files in parallel.\n'
            '  -k, --skip-installed             Skip installed packages during\n'
            f"{'':>35}the building or installation progress.\n"
            '  -r, --reinstall                  Upgrade all packages even if the same\n'
            f"{'':>35}version is already installed.\n"
            '  -V, --no-version                 Hide version and show only packages name.\n'
            '  -c, --check-deps                 Check installed dependencies based on\n'
            f"{'':>35}repository.\n"
            '  -E, --edit-sbo                   Edit the PRGNAM.SlackBuild file\n'
            f"{'':>35}before build the package.\n"
            '  -a, --view-readme                View README file before build the package.\n'
            '  -l, --row-list                   Instead of view packages in list mode,\n'
            f"{'':>35}view packages side by side.\n"
            '  -o, --no-deps                    Switch off resolving dependencies.\n'
            f"{'':>35}Useful to install individual packages.\n"
            '  -g, --gpg-off                    Switch off GPG verification.\n'
            '  -m, --checksum-off               Switch off checksum verification.\n'
            '  -Q, --quite                      Show less information. This is useful.\n'
            f"{'':>35}when sbpkg output is processed in a script.\n"
            '  -B, --progress-bar               Apply it to see a progress bar instead\n'
            f"{'':>35}of package progress.\n"
            '  -x, --exclude-pkgs=<packages>    Separate packages by a comma or using\n'
            f"{'':>35}regex pattern to exclude them from process.\n\n"
            '  -h, --help                       Show this message and exit.\n'
            '  -v, --version                    Print the version and exit.\n\n'
            f'Edit the configuration file in the {self.etc_path}/{self.prgnam}.conf.\n'
            f'Open issues at https://gitlab.com/dslackw/sbpkg/-/issues'

        )
        print(cli_help)
        sys.exit(0)

    def invalid_options(self) -> NoReturn:
        """Print for an invalid option help message."""
        invalid: str = (
            f'{self.prgnam}: invalid options\n'
            f'Usage: {self.prgnam} [COMMAND] [OPTIONS] <packages>\n\n'
            f"Try '{self.prgnam} --help' for more options"
        )
        print(invalid)
        sys.exit(1)

#!/bin/python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Generator

from sbpkg.config import Config
from sbpkg.metadata import Metadata


class Utils(Config):
    """sbpkg utilities.
    """

    def __init__(self) -> None:
        super().__init__()

        self.prgnam: str = Metadata.__prgnam__

    def read_json_file(self, file: Path) -> dict[str, str]:
        """Read JSON data from the file.

        Args:
            file (Path): Path file for reading.

        Returns:
            The json file.
        """
        json_data: dict[str, str] = {}
        try:
            json_data = json.loads(file.read_text(encoding='utf-8'))
        except FileNotFoundError:
            print(f'{self.prgnam}: Error file {file} not found.\n')
        except json.JSONDecodeError as e:
            print(f'{self.prgnam}: Error decoding JSON data: {e}')
        return json_data

    def write_json_file(self) -> None:  # pylint: disable=[R0912,R0914]
        """Read the SLACKBUILDS.TXT FILE and creates a json data file.
        """
        data: dict[str, dict[str, str | list]] = {}
        cache: list[str] = []
        names: list[str] = []
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

        slackbuilds_txt: list[str] = Path(
            self.local_repo, self.slackbuilds_txt).read_text(encoding='utf-8').splitlines()

        for line in slackbuilds_txt:
            if line.startswith(sbo_tags[0]):
                names.append(line.replace(sbo_tags[0], '').strip())

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

                requires: list[str] = [item for item in cache[8].split() if item in names]

                data[name] = {
                    'location': location,
                    'files': cache[2].split(),
                    'version': version,
                    'download': cache[4].split(),
                    'download64': cache[5].split(),
                    'md5sum': cache[6].split(),
                    'md5sum64': cache[7].split(),
                    'requires': requires,
                    'description': cache[9]
                }

                arch: str = self.arch
                sbo_file: Path = Path(self.local_repo, location, name, f'{name}.SlackBuild')
                if sbo_file.is_file():
                    slackbuild = sbo_file.read_text(encoding='utf-8').splitlines()
                    for sbo_line in slackbuild:
                        if sbo_line.startswith('BUILD=$'):
                            build = ''.join(re.findall(r'\d+', sbo_line))
                        if sbo_line.startswith('ARCH=noarch'):
                            arch = 'noarch'

                data[name].update({'arch': arch})
                data[name].update({'build': build})
                package: str = f'{name}-{version}-{arch}-{build}{self.repo_tag}{self.pkgtype}'
                data[name].update({'package': package})

                cache = []  # reset cache after 11 lines
        self.json_data_file.write_text(json.dumps(data, indent=4), encoding='utf-8')

    def mkdir_init(self) -> None:
        """Create the paths if they are not existing.
        """
        paths: list[Path] = [
            self.tmp_sbpkg_path,
            self.build_path,
            self.log_path,
            self.lib_path,
            self.local_repo,
            self.etc_path
        ]
        for path in paths:
            if not path.is_dir():
                path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_packages_list(file: Path) -> Generator:
        """Read packages from a file.

        Args:
            file (Path): Path to file.

        Yields:
            Generator: The name of the packages.
        """
        if file.is_file():
            pkglist: list[str] = file.read_text(encoding='utf-8').splitlines()

            for package in pkglist:
                if package and not package.startswith('#'):
                    yield package.split('#')[0].strip()

    def run_process(self, command: str, stdout: int | None = None, stderr: int | None = None) -> None:
        """Subprocess run command and raise the exit code.

        Args:
            command (str): The command that will go to run.
            stdout (int | None, optional): Captured stdout from the child process.
            stderr (int | None, optional): Captured stderr from the child process.
        """
        process = subprocess.run(command, shell=True, stdout=stdout, stderr=stderr, text=True, check=True)

        if process.returncode != 0:
            print(f"\n{self.bred}FAILED!{self.endc} to run command '{command.split()[0]}' "
                  f"exit code: {process.returncode}\n")
            sys.exit(process.returncode)

    @staticmethod
    def matched_packages(packages: list[str], dependencies: list[str]) -> list[str]:
        """Match packages between two lists.

        Args:
            packages (list[str]): List of packages.
            dependencies (list[str]): List of dependencies.

        Returns:
            list[str]: The matching packages.
        """
        matched: list[str] = list(set(dependencies) & set(packages))
        # Remove main packages from the list if they exist as dependency.
        packages = [pkg for pkg in packages if pkg not in matched]
        return packages

    @staticmethod
    def ignore_packages(blacklist: list[str], packages: list[str]) -> list[str]:
        """Match packages using regular expression.

        Args:
            blacklist (list[str]): The packages will be used as a pattern.
            packages (list[str]): The packages to apply the pattern.

        Returns:
            list[str]: The matching packages.
        """
        pattern: str = '|'.join(blacklist)
        matching_packages: list[str] = [pkg for pkg in packages if re.search(pattern, pkg)]
        return matching_packages

    @staticmethod
    def split_package(package: str) -> dict[str, str]:
        """Split the package to name, version, arch and build number.

        Args:
            package (str): The full package name.

        Returns:
            dict[str, str]: The spitted packages.
        """
        name: str = '-'.join(package.split('-')[:-3])
        version: str = package[len(name):].split('-')[1]
        arch: str = package[len(name):].split('-')[2]
        build: str = ''.join(re.findall(r'\d+', package.split('-')[-1]))
        return {
            'name': name,
            'version': version,
            'arch': arch,
            'build': build,
        }

    def all_installed(self) -> list[str]:
        """Return all SBo installed packages from /val/log/packages folder.

        Returns:
            list[str]: List of installed packages.
        """
        blacklist: list[str] = list(self.read_packages_list(self.blacklist_file))
        installed_packages: dict[str, str] = {}

        for file in self.log_pkgs_path.glob(f'*{self.repo_tag}'):
            name: str = self.split_package(file.name)['name']

            if not name.startswith('.'):
                installed_packages[name] = file.name

        if blacklist:
            blacklist_packages: list[str] = self.ignore_packages(blacklist, list(installed_packages.keys()))
            for black in blacklist_packages:
                del installed_packages[black]

        return list(installed_packages.values())

    def is_installed(self, name: str) -> Path | None:
        """Find installed packages.

        Args:
            name (str): The name of the package to search.
        Returns:
            Path | None: Installed package if exists and None if not.
        """
        installed_package: Generator = Path(self.log_pkgs_path).glob(f'{name}*{self.repo_tag}')
        for installed in installed_package:
            inst_name: str = self.split_package(installed.name)['name']
            if inst_name == name:
                return installed
        return None

    def is_upgradeable(self, package: str, data: dict[str, dict[str, str]]) -> bool:
        """Compare two packages installed and repository.

        Args:
            package (str): The name of the package.
            data (dict[str, dict[str, str]]): Data of packages.

        Returns:
            bool: True for upgradeable and false for not.
        """
        installed: Path | None = self.is_installed(package)
        if installed:
            repo_package: str = data[package]['package'].replace(self.pkgtype, '')
            if repo_package != installed.name:
                return True
        return False

    @staticmethod
    def convert_bytes(byte_size: int) -> str:
        """Convert bytes to kb, mb and gb.

        Args:
            byte_size (int): The file size in bytes.

        Returns:
            str: The size converted.
        """
        kb_size: float = byte_size / 1024
        mb_size: float = kb_size / 1024
        gb_size: float = mb_size / 1024

        if gb_size >= 1:
            return f"{gb_size:.2f} GB"
        if mb_size >= 1:
            return f"{mb_size:.2f} MB"
        if kb_size >= 1:
            return f"{kb_size:.2f} KB"

        return f"{byte_size} B"

    def count_file_size(self, name: str) -> int:
        """Read the package file list and count the size in bytes.

        Args:
            name (str): The name of the package.

        Returns:
            int: The total package installation file size.
        """
        count_files: int = 0
        installed: Path | None = self.is_installed(name)
        if installed:
            file_installed: list[str] = installed.read_text().splitlines()
            for line in file_installed:
                file: Path = Path('/', line)
                if file.is_file():
                    count_files += file.stat().st_size
        return count_files

#!/bin/python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import hashlib
import itertools
import json
import multiprocessing
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from signal import SIG_DFL, SIGPIPE, signal
from threading import Thread
from typing import Any, Callable, cast
from urllib.parse import urlparse

from sbpkg.chars import Chars
from sbpkg.cli_help import CliHelp
from sbpkg.config import Config
from sbpkg.metadata import Metadata
from sbpkg.pb_config import PbConfig
from sbpkg.sbo_generate import SBoGenerate
from sbpkg.utils import Utils

# Fixes: BrokenPipeError: [Errno 32] Broken pipe
# Redirect the SIGPIPE signals to the default SIG_DFL signal,
# which the system generally ignores so that the rest part of
# the code can be executed seamlessly.
signal(SIGPIPE, SIG_DFL)


class SBpkg(Config, Chars, PbConfig):  # pylint: disable=[R0902,C0302]
    """Build, install and download the sbo scripts."""

    def __init__(self) -> None:
        super().__init__()

        self.prgnam: str = Metadata.__prgnam__
        self.version: str = Metadata.__version__
        self.description: str = Metadata.__description__
        self.cli_help = CliHelp()
        self.utils = Utils()

        self.data: dict[str, Any] = {}
        self.command: str = ''
        self.flags: list[str] = []
        self.blacklist_packages: list[str] = []
        self.exclude_pkgs: list[str] = []
        self.package_install: str = self.install_command
        self.output_env: Path = Path()

        # Creates the necessary paths.
        self.utils.mkdir_init()

        # Get terminal sizes.
        self.columns = shutil.get_terminal_size().columns
        self.rows = shutil.get_terminal_size().lines

        # Semaphore to control the number of concurrent threads
        self.semaphore = threading.BoundedSemaphore(int(self.maximum_parallel))

        self.kernel_ver: str = platform.uname()[2]

    def _check_md5sum(self, filename: Path, expected_md5: str) -> None:
        """Check the MD5 sum of a file against an expected value.

        Args:
            filename (Path): Path to the file.
            expected_md5 (str): The expected MD5 sum in hexadecimal format.
        """
        if not self._is_extra_options(['-m', '--checksum-off']) and self.checksum_md5 == 'on':
            with open(filename, 'rb') as f:
                data: bytes = f.read()
                md5_hash = hashlib.md5(data).hexdigest()

            if md5_hash != expected_md5:
                print('\nChecking MD5SUM:')
                print((31 + len(filename.name)) * '=')
                print(f"MD5SUM check for '{filename.name}' ... {self.bred}FAILED!{self.endc}")
                print(f'Expected: {expected_md5}')
                print(f'Found: {md5_hash}')
                print((31 + len(filename.name)) * '=')
                self._question_proceed('downloading')

    def _gpg_verify(self, packages: list[str]) -> None:
        """GPG verifying packages.

        Args:
            packages (list[str]): List of package names.
        """
        verify_message: str = '\rVerify files with GPG ... '
        if not self._is_extra_options(['-g', '--gpg-off']) and self.gpg_verification == 'on':
            gpg_command: str = 'gpg --verify'
            if not self._is_extra_options(['-Q', '--quite']):
                print(verify_message, end='')

            exit_code: int = 0
            for i, package in enumerate(packages):
                file: str = f'{package}{self.compressed}{self.gpg_archive}'
                asc_file: Path = Path(self.local_repo, self.data[package]['location'], file)

                with subprocess.Popen(f'{gpg_command} {asc_file}', shell=True, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True) as process:

                    process.wait()

                    if process.returncode != 0 and not self._is_extra_options(['-Q', '--quite']):
                        exit_code = process.returncode
                        if i == 0:
                            print(f'{self.bred}FAILED!{self.endc}')
                        print(f"{'':>2}Error {process.returncode}: {file}")

            if exit_code == 0 and not self._is_extra_options(['-Q', '--quite']):
                print('Ok')

    def _view_packages(self, packages: list[str]) -> None:  # pylint: disable=[R0912]
        """Print packages side by side.

        Args:
            packages (list[str]): List of package names.
        """
        pkg_version: list[str] = []
        version: str = ''
        sp: int = 2
        if self._is_extra_options(['-Q', '--quite']):
            sp = 0
        for dep in packages:
            if self.command in ['-R', '--remove']:
                # If packages for view are for removing,
                # get the version from installed packages.
                installed: Path | None = self.utils.is_installed(dep)
                if installed and not self._is_extra_options(['-V', '--no-version']):
                    version = self.utils.split_package(installed.name)['version']
            else:
                version = self._pkg_version(dep)

            pkg_version.append(f"{dep}{self.grey} {version}{self.endc}")

        if self._is_extra_options(['-l', '--rows-list']):
            if self.columns <= 80:
                for i in range(0, len(pkg_version), 3):
                    if i + 2 < len(pkg_version):
                        print(f"{'':>{sp}}{pkg_version[i]}  {pkg_version[i + 1]}  {pkg_version[i + 2]}")
                    elif i + 1 < len(pkg_version):
                        print(f"{'':>{sp}}{pkg_version[i]}  {pkg_version[i + 1]}")
                    else:
                        print(f"{'':>{sp}}{pkg_version[i]}")
            elif self.columns > 80:
                for i in range(0, len(pkg_version), 4):
                    if i + 3 < len(pkg_version):
                        print(f"{'':>{sp}}{pkg_version[i]}  {pkg_version[i + 1]}  {pkg_version[i + 2]}  "
                              f"{pkg_version[i + 3]}")
                    elif i + 2 < len(pkg_version):
                        print(f"{'':>{sp}}{pkg_version[i]}  {pkg_version[i + 1]}  {pkg_version[i + 2]}")
                    elif i + 1 < len(pkg_version):
                        print(f"{'':>{sp}}{pkg_version[i]}  {pkg_version[i + 1]}")
                    else:
                        print(f"{'':>{sp}}{pkg_version[i]}")
        else:
            for pkg in pkg_version:
                print(f"{'':>{sp}}{pkg}")

    def repo_update(self) -> None:
        """Download and update the repository.
        """
        print(f'Checking for changes in the {self.changelog_txt} ...\n')
        changelog_new: Path = Path(self.local_repo, 'ChangeLog.new')
        url_changelog_txt: str = f'{self.repo_mirror}{self.repo_branch}/{self.changelog_txt}'

        if self.repo_branch == 'current':
            url_changelog_txt = f'{self.repo_mirror}{self.changelog_txt}'

        if '.git' in self.repo_mirror:
            url_changelog_txt = f'{self.repo_git_mirror}{self.changelog_txt}'

        if self.gpg_verification == 'on':
            # Import GPG KEY
            gpg_key: str = 'https://www.slackbuilds.org/GPG-KEY'
            gpg_command: str = 'gpg --quiet --fetch-key'
            self.utils.run_process(f'{gpg_command} {gpg_key}')

        if changelog_new.is_file():
            changelog_new.unlink()

        if Path(self.local_repo, self.changelog_txt).is_file() and Path(self.local_repo,
                                                                        'data.json').is_file():
            self.utils.run_process(f'{self.wget} {self.wget_options} {url_changelog_txt} -O {changelog_new}')

            if Path(self.local_repo, 'ChangeLog.new').stat().st_size == Path(self.local_repo,
                                                                             self.changelog_txt).stat().st_size:
                print(f'\n{self.byellow}There are no new changes in the {self.changelog_txt}.{self.endc}')
                self._question_proceed('updating')

        print(f'\nSyncing with the remote repository into {self.local_repo} path:\n')

        if self.repo_branch == 'current':
            sync: str = f'{self.lftp} {self.lftp_options} {self.repo_mirror} {self.local_repo}'
        else:
            repo_link: str = f'slackbuilds.org::slackbuilds/{self.repo_branch}'
            sync = f'{self.rsync} {self.rsync_options} {repo_link} {self.local_repo.parent}'

        if '.git' in self.repo_mirror:
            shutil.rmtree(self.local_repo)
            sync = f'{self.git} {self.repo_mirror} {self.local_repo}'

        self.utils.run_process(sync)

        if not Path(self.local_repo, self.slackbuilds_txt).is_file():
            gen = SBoGenerate()
            gen.slackbuild_file()

        self.utils.write_json_file()
        self._print_complete_message()

    def upgrade_packages(self) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Check for a newer packages version on repository and send them for installation.
        """
        packages_for_upgrade: dict[str, list[str]] = {}
        self._load_data()
        # Delete log file before starts.
        if self.upgrade_log_file.is_file():
            self.upgrade_log_file.unlink()

        for installed in self.utils.all_installed():
            pkg_name: str = self.utils.split_package(installed)['name']
            pkg_version: str = self.utils.split_package(installed)['version']
            pkg_build: str = self.utils.split_package(installed)['build']

            if self.kernel_version == 'on' and pkg_version.endswith(f'_{self.kernel_ver}'):
                installed = installed.replace(f'_{self.kernel_ver}', '')
                pkg_version = pkg_version.replace(f'_{self.kernel_ver}', '')

            if self.data.get(pkg_name):
                repo_package: str = self.data[pkg_name]['package']

                if installed != repo_package[:-4]:  # Add the package if a new one on the repository.
                    repo_version: str = self.data[pkg_name]['version']
                    repo_build: str = self.data[pkg_name]['build']
                    packages_for_upgrade[pkg_name] = [pkg_version, pkg_build, repo_version, repo_build]

        if packages_for_upgrade:
            name_alignment: int = 16
            if self.columns > 80:
                name_alignment = (self.columns - 80) + 16

            if not self._is_extra_options(['-Q', '--quite']):
                print('Found newer packages in repository:\n')
                packages: str = f'Packages ({len(packages_for_upgrade.keys())})'
                title: str = f"{packages:<{name_alignment + 4}} {'Version':<23} {'Build':<12} {'Repo Version':<15} {'Build':>5}"
                print(f'{self.bcyan}{title}{self.endc}\n')

                for n, (pkg, view) in enumerate(packages_for_upgrade.items(), 1):
                    name: str = pkg
                    version: str = view[0]
                    repo_ver: str = view[2]

                    if len(name) > name_alignment:
                        name = f'{name[:name_alignment - 4]}...'
                    if len(version) > 23:
                        version = f'{version[:11]}...'
                    if len(repo_ver) > 15:
                        repo_ver = f'{repo_ver[:11]}...'

                    print(f"{n:<3} {name:<{name_alignment}} {version:<23} {view[1]:<12} {repo_ver:<15} {view[3]:>5}")

                all_packages = list(packages_for_upgrade.keys())
                choose: str

                if not self._is_extra_options(['-n', '--no-confirm']) and self.no_confirm == 'off':
                    try:
                        choose = input(f'\n{self.bgreen}{self.square_emoji}{self.endc}'
                                       f'{self.bold} Choose packages separate by comma: [1-{len(all_packages)}/ALL] {self.endc}')
                    except (KeyboardInterrupt, EOFError):
                        sys.exit(1)

                if choose:
                    try:
                        # Split the string into a list of numbers and subtract 1 from each index.
                        indices = [int(index) - 1 for index in choose.split(',')]

                        # Match the numbers with the items on the list.
                        result: list[str] = [all_packages[index] for index in indices]
                        all_packages = result
                    except (IndexError, ValueError):
                        print(f'{self.red}  Wrong number selection!{self.endc}')

                print()

            self.build_install_packages(packages=all_packages)
        else:
            print('\nNo newer packages were found in the repository.')
        sys.exit(0)

    def clean_tmp(self) -> None:
        """Clean the tmp directory."""
        print('The following files and folders will be deleted:\n')
        dirs = files = 0
        for item in self.tmp_sbpkg_path.rglob('*'):
            if item.is_dir():
                dirs += 1
                print(f"Directory: {item}")
            elif item.is_file():
                files += 1
                print(f"File: {item}")

        print(f'\n{self.bold}Destination directory {self.tmp_sbpkg_path}:{self.endc}')
        print(55 * '=')
        print(f'Total ({self.bred}{dirs}{self.endc}) directories and ({self.bred}{files}{self.endc})'
              f' files will be deleted.')

        self._question_proceed('deleting')

        for item in self.tmp_sbpkg_path.rglob('*'):
            if item.is_dir():
                shutil.rmtree(item)
            if item.is_file():
                item.unlink()
        self._print_complete_message()

    def repo_changelog(self, pattern: str | None = None) -> None:
        """Print the repository ChangeLog.txt file.

        Args:
            pattern (str | None, optional): The pattern for matching.
        """
        print()
        changelog_file: Path = Path(self.local_repo, self.changelog_txt)
        if not changelog_file.is_file():
            print(f"File '{self.changelog_txt}' not found.\n")
            sys.exit(1)

        changelog_txt: list = changelog_file.read_text(encoding='utf-8').splitlines()
        for row, line in enumerate(changelog_txt, 1):
            days: tuple = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
            if pattern:
                if re.findall('|'.join(pattern), line):
                    print(line)
            else:
                if line.startswith(days):
                    print(f'{self.byellow}{line}{self.endc}')
                else:
                    print(line)
                self._press_enter_to_continue(row)
        sys.exit(0)

    def _press_enter_to_continue(self, row: int) -> None:
        """Press the enter key to continue.

        Args:
            row (int): Number of row.

        Raises:
            SystemExit: Exit if press 'q' or 'Ctrl+c'
        """
        if (row % (self.rows - 1)) == 0:
            try:
                user_input: str = input("\x1b[107m\x1b[30mPress Enter to continue, "
                                        "or 'q' to quit:\x1b[0m")
                if user_input.lower() == 'q':
                    raise SystemExit(0)
            except (KeyboardInterrupt, EOFError) as e:
                raise SystemExit(1) from e

    def build_install_packages(self, packages: list) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Build or install packages.

        Args:
            packages: Packages name for built or install.
        """
        threads: list[Thread] = []
        dependencies: list[str] = []
        all_packages: list[str] = []
        proceed_packages: list[str] = []
        count_downloads: int = 0

        self._print_resolving_message()
        for requires in packages:
            dependencies.extend(list(self._resolve_deps(requires)))
        dependencies = list(OrderedDict.fromkeys(dependencies))

        packages = self.utils.matched_packages(packages, dependencies)
        self._print_done_resolving_message()

        self._gpg_verify(dependencies + packages)

        # Appends the main packages to the end of the queue.
        all_packages = [*dependencies, *packages]

        # Count the downloads.
        for package in all_packages:
            count_downloads += len(self.data[package]['download'])
            if not self.data[package]['md5sum']:
                count_downloads += len(self.data[package]['download64'])

        self._print_packages_message(len(packages), message='Packages')
        self._view_packages(packages)
        self._print_packages_message(len(dependencies), message='Dependencies')
        self._view_packages(dependencies)
        self._print_total_message(packages=len(all_packages), download=count_downloads)

        command_msg: str = 'build'
        if self.command in ['-i', '--install']:
            command_msg = 'installation'
        elif self.command in ['-U', '--upgrade']:
            command_msg = 'upgrading'

        self._question_proceed(command_msg)

        self._delete_log_file()

        self._print_starts(count_downloads, message='downloading')

        # Copy the scripts to the build director.
        for package in all_packages:
            proceed_packages.append(package)
            location: str = self.data[package]['location']
            source_dir: Path = Path(self.local_repo, location, package)
            destination_dir: Path = Path(self.build_path, package)

            # Copy the scripts to the build directory.
            if destination_dir.is_dir():
                shutil.rmtree(destination_dir)

            shutil.copytree(source_dir, destination_dir)

            urls: list[str] = self.data[package]['download']
            md5sums: list[str] = self.data[package]['md5sum']
            if self.arch_os == '64bit' and self.arch in {'x86_64', 'amd64', 'aarch64', 'arm64', 'ia64'}:
                urls = self.data[package]['download64']
                md5sums = self.data[package]['md5sum64']

            if self.parallel_downloads == 'on' or self._is_extra_options(['-P', '--parallel']):
                thread = threading.Thread(target=self._download_sources, args=(urls, md5sums, destination_dir,))
                threads.append(thread)
                thread.start()
            else:
                self._download_sources(urls, md5sums, destination_dir)

        # Print empty line if no packages for proceed.
        if not proceed_packages:
            print()

        # Starts parallel download if it's enabled.
        if self.parallel_downloads == 'on' or self._is_extra_options(['-P', '--parallel']):
            for thread in threads:
                thread.join()

        install: str = ''
        build: str = 'build'
        if self.command in ['-i', '--install']:
            install = ' and installation'
        message: str = f'{build}{install}'

        self._print_starts(len(proceed_packages), message=message)

        # Build the scripts.
        for package in proceed_packages:
            self.output_env = Path(tempfile.mkdtemp(dir=self.tmp_sbpkg_path, prefix=f'{self.prgnam}.'))

            destination_dir = Path(self.build_path, package)
            command: str = f'{destination_dir}/./{package}.SlackBuild'

            self._set_makeflags()
            self._set_output()

            self._view_readme(package, destination_dir)
            self._edit_the_sbo(package, destination_dir)
            self._set_permissions(package, destination_dir)

            if self.progress_bar == 'on' or self._is_extra_options(['-B', '--progress-bar']):
                process: str = 'building'
                build_process = multiprocessing.Process(target=self._process_and_log, args=(command,))
                progress_process = multiprocessing.Process(target=self._progress_bar_process,
                                                           args=(package, process,))
                build_process.start()
                progress_process.start()

                build_process.join()

                # Terminate process 2 if process 1 finished.
                if not build_process.is_alive():
                    progress_process.terminate()
                    if build_process.exitcode != 0:
                        sys.exit(0)

                    if self.command in ['-b', '--build']:
                        self._progress_bar_overwrite_print(package, process)
            else:
                self._process_and_log(command)

            # Install the scripts.
            if self.command in ['-i', '--install', '-U', '--upgrade']:
                if self.progress_bar == 'on' or self._is_extra_options(['-B', '--progress-bar']):
                    upgradeable: bool = self.utils.is_upgradeable(package, self.data)
                    installed: Path | None = self.utils.is_installed(package)

                    process = 'upgrading'
                    if not installed:
                        process = 'installing'

                    install_process = multiprocessing.Process(target=self._install_package, args=(package,))
                    progress_process = multiprocessing.Process(target=self._progress_bar_process,
                                                               args=(package, process,))
                    install_process.start()
                    progress_process.start()

                    install_process.join()

                    # Terminate process 2 if process 1 finished.
                    if not install_process.is_alive():
                        progress_process.terminate()
                        if install_process.exitcode != 0:
                            sys.exit(0)
                        self._progress_bar_overwrite_print(package, process, upgradeable)
                else:
                    self._install_package(package)

        self._print_complete_message()

    def _process_and_log(self, command: str) -> None:
        """Build the package and write a log file.

        Args:
            command (str): The process command.
        """
        if self.command in ['-b', '--build', '-i', '--install', '-U', '--upgrade']:
            os.environ['OUTPUT'] = str(self.output_env)

        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        head_message: str = f'Timestamp: {timestamp}'
        bottom_message: str = 'EOF - End of log file'

        with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True) as process:

            # Write the timestamp at the head of the log file.
            with open(self.log_file, 'a', encoding='utf-8') as log:
                log.write(f"{len(head_message) * '='}\n")
                log.write(f'{head_message}\n')
                log.write(f"{len(head_message) * '='}\n\n")

            # Write the process to the log file and to the terminal.
            if process.stdout is not None:
                with process.stdout as output:
                    for line in output:
                        if not self.progress_bar == 'on' and not self._is_extra_options(['-B', '--progress-bar']):
                            print(line.strip())  # Print to console
                        with open(self.log_file, 'a', encoding='utf-8') as log:
                            log.write(line)  # Write to log file

            # Write the bottom of the log file.
            with open(self.log_file, 'a', encoding='utf-8') as log:
                log.write(f"\n{len(bottom_message) * '='}\n")
                log.write(f'{bottom_message}\n')
                log.write(f"{len(bottom_message) * '='}\n\n")

            process.wait()  # Wait for the process to finish

            # If the process failed, return exit code.
            if process.returncode != 0:
                message: str = 'Error occurred with build. Please check the log file.'
                print()
                print((self.columns - 3) * '=')
                print(f'{self.bred}{message}{self.endc}')
                print((self.columns - 3) * '=')
                print()
                sys.exit(process.returncode)

        if self.command in ['-b', '--build']:
            self._move_package_and_delete_folder()

    def _download_sources(self, urls: list[str], md5sums: list[str], destination_dir: Path) -> None:
        """Download the sources into the slackbuild script folder.

        Args:
            urls (list[str]): Links for download.
            md5sums (list[str]): List of source checksum.
            destination_dir (Path): Slackbuild path folder.
        """
        # Acquire the semaphore before starting the download
        for url, md5 in zip(urls, md5sums):
            with self.semaphore:
                command: str = f'{self.wget} {self.wget_options} --directory-prefix={destination_dir} "{url}"'
                self.utils.run_process(command)

                parsed_url = urlparse(url)
                filename: str = os.path.basename(parsed_url.path)
                self._check_md5sum(Path(destination_dir, filename), md5)

    def _install_package(self, package: str) -> None:
        """Install or upgrade packages and write the dependencies to the log file.

        Args:
            package (str): Package name for installation.
        """
        data: dict[str, Any] = {}
        deps_logs: dict[str, str] = {}
        installed_requires: list[str] = []
        requires: tuple[str, ...] = self._resolve_deps(package)

        install: str = [f.name for f in self.output_env.iterdir() if f.is_file()][0]

        command: str = f'{self.package_install} {Path(self.output_env, install)}'
        if self.progress_bar == 'on' or self._is_extra_options(['-B', '--progress-bar']):
            self.utils.run_process(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            self.utils.run_process(command)

        self._move_package_and_delete_folder()

        # Verify for installation.
        for req in requires:
            if self.utils.is_installed(req):
                installed_requires.append(req)

        data[package] = installed_requires
        if self.deps_log_file.is_file():
            deps_logs = self.utils.read_json_file(self.deps_log_file)
            deps_logs.update(data)
        self.deps_log_file.write_text(json.dumps(deps_logs, indent=4), encoding='utf-8')

    def _move_package_and_delete_folder(self) -> None:
        """Move binary package to /tmp folder and delete temporary folder."""
        package_name: str = [f.name for f in self.output_env.iterdir() if f.is_file()][0]
        binary_path_file: Path = Path(self.output_env, package_name)

        # Remove binary package file from /tmp folder if exist before move the new one.
        package_tmp: Path = Path(self.tmp, package_name)
        if package_tmp.is_file():
            os.remove(package_tmp)

        # Move the new binary package file to /tmp folder.
        if binary_path_file.is_file():
            shutil.move(binary_path_file, self.tmp)
            if not self._is_extra_options(['-B', '--progress-bar']):
                message: str = f'| Moved: {package_name} to the {self.tmp} folder.'
                length_message: int = len(message) - 1
                print(f"\n+{'=' * length_message}")
                print(message)
                print(f"+{'=' * length_message}\n")

        # Delete the temporary empty folder.
        if self.output_env.is_dir():
            shutil.rmtree(self.output_env)

    def remove_packages(self, packages: list[str]) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Remove installed packages with dependencies.

        Args:
            packages (list[str]): List of packages to remove.
        """
        self._print_resolving_message()
        deps_log: dict[str, list[str]] = {}
        deps_remove: list[str] = []
        not_installed: list[str] = []
        found_dependent: list[str] = []
        total_count: int = 0

        deps_log = cast(dict[str, list[str]], self.utils.read_json_file(self.deps_log_file))

        self._delete_log_file()

        for package in packages:
            if not self.utils.is_installed(package):
                self._print_done_resolving_message()
                print(f"\nNo package '{package}' found.\n")
                sys.exit(1)

            if not self._is_extra_options(['-o', '--no-deps']) and self.deps_log_file.is_file():
                if package in deps_log:
                    deps: list[str] = deps_log[package]
                    if deps:
                        deps_remove.extend(deps)

        # Removes uninstalled packages from dependencies.
        for dep in deps_remove:
            if not self.utils.is_installed(dep):
                not_installed.append(dep)

        # Remove not dependencies installed.
        deps_remove = [pkg for pkg in deps_remove if pkg not in not_installed]

        # Remove main packages from the list if they exist as dependency.
        packages = self.utils.matched_packages(packages, deps_remove)
        self._print_done_resolving_message()

        # Checking if the package is a dependency in other
        # packages and add them in a list.
        for package in deps_remove + packages:
            for pkg, deps in deps_log.items():
                if package in deps and pkg not in deps_remove + packages:
                    found_dependent.append(pkg)

        self._print_packages_message(len(deps_remove), message='Packages')
        self._view_packages(packages)
        self._print_packages_message(len(deps_remove), message='Dependencies')
        self._view_packages(deps_remove)

        # Update the list with main packages.
        deps_remove.extend(packages)

        # Count total removed packages size.
        for package in deps_remove:
            pkg_bytes: int = self.utils.count_file_size(package)
            total_count += pkg_bytes
        total_size_removed: str = self.utils.convert_bytes(total_count)

        if found_dependent and not self._is_extra_options(['-Q', '--quite']):
            dependent_packages: list[str] = list(set(found_dependent))
            print(f'\n{self.bred}Warning: {self.endc}found extra ({len(dependent_packages)}) dependent packages:')
            self._view_packages(dependent_packages)

        self._print_total_message(len(deps_remove), size=total_size_removed)
        self._question_proceed('removing')
        self._print_starts(len(deps_remove), 'removing')

        for package in deps_remove:
            command: str = f'{self.remove_command} {package}'
            if self.progress_bar == 'on' or self._is_extra_options(['-B', '--progress-bar']):
                process: str = 'removing'
                remove_process = multiprocessing.Process(target=self._process_and_log, args=(command,))
                progress_process = multiprocessing.Process(target=self._progress_bar_process,
                                                           args=(package, process,))
                remove_process.start()
                progress_process.start()

                remove_process.join()

                # Terminate process 2 if process 1 finished
                if not remove_process.is_alive():
                    progress_process.terminate()
                    if remove_process.exitcode != 0:
                        sys.exit(0)
                    self._progress_bar_overwrite_print(package, process)
            else:
                self._process_and_log(command)
                if '--verbose' in self.remove_command:
                    print()

            if package in deps_log.keys():
                deps_log.pop(package)

        self.deps_log_file.write_text(json.dumps(deps_log, indent=4), encoding='utf-8')
        self._print_complete_message()

    def view_package_requires(self, packages: list[str]) -> None:
        """Print package dependencies.

        Args:
            packages (list[str]): Packages name to search for dependencies.
        """
        self._print_resolving_message()
        dependencies: dict[str, tuple[str, ...]] = {}
        for package in packages:
            dependencies[package] = self._resolve_deps(package)
        self._print_done_resolving_message()
        quite_mode: bool = self._is_extra_options(['-Q', '--quiet'])

        if not quite_mode:
            print()

        for package, requires in dependencies.items():
            if quite_mode:
                print(package, self._pkg_version(package))
            else:
                print(f"{self.bcyan}{package} {self._pkg_version(package)} "
                      f"{self.grey}({len(requires)}){self.endc}:")
            if requires:
                for i, req in enumerate(requires, 1):
                    if quite_mode:
                        print(f"{'':>2}{req} {self._pkg_version(req)}")
                    else:
                        ascii_char: str = self.ascii_var
                        if i == len(requires):
                            ascii_char = self.ascii_ldc
                        print(f"{'':>2}{ascii_char}{self.ascii_line} {self.yellow}{req} "
                              f"{self.endc}{self._pkg_version(req)}")
            else:
                if not quite_mode:
                    print(f"{'':>2}No dependencies found.")

            if not quite_mode:
                print()
        sys.exit(0)

    def view_package_dependees(self, packages: list[str]) -> None:  # pylint: disable=[R0912]
        """Print a list of depended on packages.

        Args:
            packages (list[str]): List of packages for searching.

        No Longer Returned:
            List of packages that depends on.
        """
        self._print_resolving_message()
        found: dict[str, list[str]] = {}
        for package in packages:
            found[package] = self._depends_on(package)
        self._print_done_resolving_message()
        quite_mode: bool = self._is_extra_options(['-Q', '--quiet'])

        if not quite_mode:
            print()

        if found:  # pylint: disable=[R1702]
            for package, requires in found.items():
                if quite_mode:
                    print(package, self._pkg_version(package))
                else:
                    print(f'{self.bcyan}{package} {self._pkg_version(package)} '
                          f'{self.grey}({len(requires)}){self.endc}:')
                if requires:
                    for i, req in enumerate(requires, 1):
                        if quite_mode:
                            print(f"{'':>2}{req} {self._pkg_version(package)}")
                        else:
                            ascii_char: str = self.ascii_var
                            if i == len(requires):
                                ascii_char = self.ascii_ldc
                            print(f"{'':>2}{ascii_char}{self.ascii_line} {self.yellow}{req} "
                                  f"{self.endc}{self._pkg_version(req)}")
                    if not quite_mode:
                        print()
                else:
                    if not quite_mode:
                        print(f"{'':>2}No dependents found\n")
        sys.exit(0)

    def search_packages(self, packages: list) -> None:
        """Print a list of matching packages.

        Args:
            packages (list): List of packages for searching.
        """
        found: list[str] = []
        for package in packages:
            package = package.replace('*', '')
            for pkg in self.data.keys():
                if package in pkg:
                    found.append(pkg)

        if found:
            self._print_found_message(len(found))
            for pkg in found:
                installed: str = ''
                if self.utils.is_installed(pkg):
                    installed = f' [{self.bcyan}installed{self.endc}]'

                if self._is_extra_options(['-Q', '--quiet']):
                    print(pkg, self._pkg_version(pkg))
                else:
                    location: str = self.data[pkg]['location']
                    description: str = self.data[pkg]['description']
                    print(f"{self.bgreen}{pkg}{self.endc} {self.byellow}{self._pkg_version(pkg)}{self.endc} "
                          f"[{self.repo_name}/{location}]{installed}")
                    print(f"{'':>2}{self.ascii_ldc}{self.ascii_line} {description[len(pkg) + 2:-1]}\n")
        else:
            print('\nNo package name matches the pattern.\n')
            sys.exit(1)
        sys.exit(0)

    def find_installed_packages(self, packages: list[str]) -> None:  # pylint: disable=[R0912]
        """Print a list of matching packages.

        Args:
            packages (list[str]): List of packages for searching.
        """
        found: list[str] = []
        total_count: int = 0
        dependencies: tuple[str, ...] = ()
        for package in packages:
            package = package.replace('*', '')
            for installed in self.utils.all_installed():
                if package in installed:
                    found.append(installed)

        if found:  # pylint: disable=[R1702]
            self._print_found_message(len(found))

            for installed in found:
                name: str = self.utils.split_package(installed)['name']

                if self._is_extra_options(['-Q', '--quiet']):
                    print(installed)
                else:
                    pkg_bytes: int = self.utils.count_file_size(name)
                    pkg_size: str = self.utils.convert_bytes(pkg_bytes)
                    total_count += pkg_bytes
                    print(f'{self.cyan}{installed}{self.endc} ({pkg_size})')

                # Checking for deps in the repository database.
                if self._is_extra_options(['-c', '--check-deps']):
                    if name in self.data.keys():
                        repo_package: str = self.data[name]['package'][:-4]

                        if installed == repo_package:
                            if not self._is_extra_options(['-o', '--no-deps']):
                                dependencies = self._resolve_deps(name)
                            if dependencies:
                                self._print_find_packages(dependencies)

                else:
                    # Checking for deps in the deps_log file.
                    deps_log: dict = self.utils.read_json_file(self.deps_log_file)
                    if name in deps_log.keys():
                        if not self._is_extra_options(['-o', '--no-deps']):
                            dependencies = deps_log[name]
                        if dependencies:
                            self._print_find_packages(dependencies)
        else:
            print('\nNo package name matches the pattern.\n')
            sys.exit(1)
        if not self._is_extra_options(['-Q', '--quiet']):
            print(f'\nTotal ({len(found)}) packages size installed: {self.utils.convert_bytes(total_count)}')
        sys.exit(0)

    def _print_find_packages(self, deps: list[str] | tuple[str, ...]) -> None:
        """Print the results of '--find-installed' method and count the total packages size.

        Args:
            deps (list[str] | tuple[str, ...]): Dependencies package names.
        """
        installed_deps: list[str] = []
        color: str = self.green
        ascii_char: str
        if self._is_extra_options(['-c', '--check-deps']):
            color = self.yellow

        for dep in deps:
            installed_dep: Path | None = self.utils.is_installed(dep)
            if installed_dep:
                if not self._is_extra_options(['-Q', '--quiet']):
                    installed_deps.append(installed_dep.name)

        if installed_deps:
            for i, dep in enumerate(installed_deps, 1):

                if self._is_extra_options(['-Q', '--quiet']):
                    print(dep)
                else:
                    ascii_char = self.ascii_var
                    if i == len(installed_deps):
                        ascii_char = self.ascii_ldc

                print(f"{'':>2}{ascii_char}{self.ascii_line} {color}{dep}{self.endc}")

    def download_packages(self, packages: list[str]) -> None:
        """Download only packages.

        Args:
            packages (list[str]): List of packages for download.
        """
        threads: list[Thread] = []
        count_downloads: int = 0

        self._gpg_verify(packages)
        self._print_packages_message(len(packages), message='Packages')
        self._view_packages(packages)

        self._question_proceed('downloading')

        # Count the urls.
        for package in packages:
            count_downloads += len(self.data[package]['download'])
            if not self.data[package].get('md5sum'):
                count_downloads += len(self.data[package]['download64'])

        self._print_starts(count_downloads, message='downloading')

        for package in packages:
            location: str = self.data[package]['location']
            source_dir: Path = Path(self.local_repo, location, package)
            download_dir: Path = Path(self.download_path, package)

            if download_dir.is_dir():
                shutil.rmtree(download_dir)

            shutil.copytree(source_dir, download_dir)

            urls: list[str] = self.data[package]['download']
            md5sums: list[str] = self.data[package]['md5sum']
            if not md5sums:
                urls = self.data[package]['download64']
                md5sums = self.data[package]['md5sum64']

            # Download the sources.
            if self.parallel_downloads == 'on' or self._is_extra_options(['-P', '--parallel']):
                thread = threading.Thread(target=self._download_sources, args=(urls, md5sums, download_dir,))
                threads.append(thread)
                thread.start()
            else:
                self._download_sources(urls, md5sums, download_dir)

        # Starts parallel download if it's enabled.
        if self.parallel_downloads == 'on' or self._is_extra_options(['-P', '--parallel']):
            for thread in threads:
                thread.join()

        if not self._is_extra_options(['-Q', '--quite']):
            print(f"\nPackages downloaded in the '{self.download_path}' folder.")
        sys.exit(0)

    def package_information(self, packages: list[str]) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Print package information.

        Args:
            packages (list[str]): List of packages for information.
        """
        self._print_resolving_message()
        package_info: dict[str, dict[str, str] | Any] = {}
        mirror_url: list = self.repo_mirror.split('/')
        mirror_url[3] = 'repository'
        sbo_url: str = f"{'/'.join(mirror_url)}{self.repo_branch}/"
        if '.git' in self.repo_mirror:
            sbo_url = self.repo_mirror.replace('.git', f'/tree/{self.repo_branch}/')

        homepage_var: str = 'HOMEPAGE="'
        maintainer_var: str = 'MAINTAINER="'
        email_var: str = 'EMAIL="'
        homepage: str = ''
        maintainer: str = ''
        email: str = ''
        days: tuple[str, ...] = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        last_updated: str = ''
        changelog_file: Path = Path(self.local_repo, self.changelog_txt)
        self._print_done_resolving_message()
        print()

        for package in packages:
            depends_on: list[str] = self._depends_on(package)
            requires: tuple[str, ...] = self._resolve_deps(package)
            location: str = self.data[package]['location']
            info_file: Path = Path(self.local_repo, location, package, f'{package}.info')
            info: list[str] = info_file.read_text(encoding='utf-8').splitlines()
            changelog: list[str] = changelog_file.read_text(encoding='utf-8').splitlines()
            installed: str = 'Yes' if self.utils.is_installed(package) else 'No'
            download_sbo: str = f'{self.repo_mirror}{self.repo_branch}/{location}/{package}{self.compressed}'
            if '.git' in self.repo_mirror:
                download_sbo = f'{sbo_url}{location}/{package}/'

            if info_file.is_file():
                for line in info:
                    if line.startswith(homepage_var):
                        homepage = line.replace(homepage_var, '')
                    if line.startswith(maintainer_var):
                        maintainer = line.replace(maintainer_var, '')
                    if line.startswith(email_var):
                        email = line.replace(email_var, '')

            if changelog_file.is_file():
                for line in changelog:
                    if line.startswith(days):
                        last_updated = line
                    if line.startswith(f'{location}/{package}'):
                        break

            package_info[package] = {
                'Repository': self.repo_name,
                'Name': package,
                'Description': self.data[package]['description'][len(package) + 2:-1],
                'Homepage:': homepage[:-1],
                'Location': location,
                'Version': self._pkg_version(package),
                'Architecture': self.data[package]['arch'],
                'Build Number': self.data[package]['build'],
                'Last Updated': last_updated,
                'Package:': self.data[package]['package'],
                'Installed': installed,
                'SBo URL': f'{sbo_url}{location}/{package}/',
                'Download SBo': download_sbo,
                'Sources': self.data[package]['download'],
                'Md5sum': self.data[package]['md5sum'],
                'Sources x86_64': self.data[package]['download64'],
                'Md5sum x86_64': self.data[package]['md5sum64'],
                'Maintainer': maintainer[:-1],
                'Email': email[:-1],
                f'Requires ({len(requires)})': requires,
                f'Dependees ({len(depends_on)})': depends_on
            }

        for items in package_info.values():
            for pkg, reqs in items.items():
                if len(reqs) > 2 and pkg.startswith('Requires'):
                    print(f"{self.bold}{pkg:<15}{self.endc}:", end='')
                    space: int = 1
                    for i in range(0, len(reqs), 3):
                        if i > 1:
                            space = 17
                        if i + 2 < len(reqs):
                            print(f"{'':<{space}}{reqs[i]}  {reqs[i + 1]}  {reqs[i + 2]}")
                        elif i + 1 < len(reqs):
                            print(f"{'':<{space}}{reqs[i]}  {reqs[i + 1]}")
                        else:
                            print(f"{'':<{space}}{reqs[i]}")
                elif len(reqs) > 2 and pkg.startswith('Dependees'):
                    print(f"{self.bold}{pkg:<15}{self.endc}:", end='')
                    space = 1
                    for i in range(0, len(reqs), 3):
                        if i > 1:
                            space = 17
                        if i + 2 < len(reqs):
                            print(f"{'':<{space}}{reqs[i]}  {reqs[i + 1]}  {reqs[i + 2]}")
                        elif i + 1 < len(reqs):
                            print(f"{'':<{space}}{reqs[i]}  {reqs[i + 1]}")
                        else:
                            print(f"{'':<{space}}{reqs[i]}")
                elif isinstance(reqs, str):
                    print(f"{self.bold}{pkg:<15}{self.endc}: {reqs}")
                else:
                    print(f"{self.bold}{pkg:<15}{self.endc}: {' '.join(reqs)}")
            print()
        sys.exit(0)

    def display_files(self, packages: list[str]) -> None:
        """Print package files on the terminal.

        Args:
            packages: List of package names.
        """
        print()
        choices: dict[int, Path] = {}
        number: int = 0
        for package in packages:
            files: list = self.data[package]['files']
            print(f'{self.bcyan}Choose file for {package}:{self.endc}\n')
            for n, file in enumerate(files, 1):
                print(f"{'':>2}{self.bold}{n}{self.endc}", file)
                file_path: Path = Path(self.local_repo, self.data[package]['location'],
                                       package, file)
                choices[n] = file_path
            try:
                number = int(input(f'\n{self.bgreen}{self.square_emoji}{self.endc}'
                                   f'{self.bold} Give a number: {self.endc}'))
            except (KeyboardInterrupt, EOFError):
                sys.exit(1)
            except ValueError:
                print()

            if number in choices:
                f_path = choices[number]
                if f_path:
                    print(f'\n{Path(f_path).read_text(encoding="utf-8")}')
                number = 0
            print()
        sys.exit(0)

    def print_version(self) -> None:
        """Print the program version."""
        version_info: dict[str, str | Path] = {
            f'{self.prgnam}:': self.version,
            'Repo:': self.repo_name,
            'Branch:': self.repo_branch,
            'Local:': self.local_repo,
            'Mirror:': self.repo_mirror,
            'Config:': f'{self.etc_path}/{self.prgnam}.conf'
        }
        for k, v in version_info.items():
            print(k, v)
        sys.exit(0)

    def _progress_bar_process(self, package: str, process: str) -> None:
        """Print an animation char moving left ant right.

        Args:
            package (str): The name of the package.
            process (str): The name of the process.
        """
        elapsed_time: float = 0
        start_time = time.time()

        if len(package) > 19:
            package = f'{package[:16]}...'

        while True:
            # Construct the string with the animated character.
            animated_string: str = (f"{self.pb_left}{' ' * self.pb_position}{self.pb_move}"
                                    f"{' ' * (self.pb_max_width - self.pb_position - 1)}{self.pb_right}")

            # Calculate the remaining space for the pkg_name.
            remaining_space = 40 - len(animated_string)

            # Print the pkg_name on the left and the animated string on the right.
            full_string = (f"{package:<24}{animated_string:>{remaining_space}} {process:<12}"
                           f"in {elapsed_time:.3f}s")

            # Print the full string using carriage return to overwrite the previous output.
            print(f'\r{full_string}', end='')
            time.sleep(0.02)

            # Update the position for the next iteration.
            self.pb_position += self.pb_direction

            # Reverse the direction if the character reaches the edge.
            if self.pb_position in [0, self.pb_max_width - 1]:
                self.pb_direction *= -1

            end_time = time.time()
            elapsed_time = end_time - start_time

    def _progress_bar_overwrite_print(self, package: str, process: str, upgradeable: bool | None = None) -> None:
        """Overwrite the progress bar print to show if the package, installed, upgraded or skipped.

        Args:
            package (str): The name of the package.
            process (str): The name of the process.
            upgradeable (bool | None, optional): Description
        """
        color: str = self.yellow
        process_done: str = 'built   '
        if process == 'installing':
            color = self.green
            process_done = 'installed '
        elif process == 'upgrading':
            process_done = 'upgraded  '
            if not upgradeable:
                color = self.cyan
                process_done = 'skipped   '
        elif process == 'removing':
            color = self.red
            process_done = 'removed '

        if len(package) > 19:
            package = f'{package[:16]}...'
        fill_string: str = f"100%{self.pb_left}{'=' * (self.pb_max_width + 1)}>{self.pb_right}"
        print(f"\r{color}{package:<20}{self.endc}{fill_string} {color}{process_done}{self.endc}")

    def _question_proceed(self, proceed: str) -> None:
        """Question for proceeding.

        Args:
            proceed (str): Message for proceeding.
        """
        if not self._is_extra_options(['-n', '--no-confirm']) and self.no_confirm == 'off':
            try:
                answer: str = input(f'\n{self.bgreen}{self.square_emoji}{self.endc}'
                                    f'{self.bold} Proceed with {proceed}? [y/N] {self.endc}')
            except (KeyboardInterrupt, EOFError):
                sys.exit(1)
            if answer not in ['Y', 'y']:
                sys.exit(0)

    def _print_packages_message(self, count: int, message: str) -> None:
        """Print 'Packages' message.

        Args:
            count (int): The number of the packages.
        """
        color: str = self.bcyan
        if self.command in ['-R', '--remove']:
            color = self.bred

        if self._is_extra_options(['-o', '--no-deps']) and message == 'Dependencies':
            pass
        if count == 0 and message == 'Dependencies':
            pass
        elif not self._is_extra_options(['-Q', '--quite']):
            print(f'\n{color}{message} {self.grey}({count}){self.endc}:')

    def _print_found_message(self, count: int) -> None:
        """Print the found message.

        Args:
            count: The number of the packages.
        """
        if not self._is_extra_options(['-Q', '--quite']):
            print(f'\n{self.bcyan}Found packages {self.grey}({count}){self.endc}:\n')

    def _print_total_message(self, packages: int, download: int | None = None, size: str = '') -> None:
        """Print the total message depends on the command.

        Args:
            packages (int): The count of packages.
            download (int | None, optional): Description
            size (str, optional): The size of packages.
        """
        build_install_upgrade: list[str] = ['-b', '--build', '-i', '--install', '-U', '--upgrade']
        remove: list[str] = ['-R', '--remove']
        if self.command in build_install_upgrade and not self._is_extra_options(['-Q', '--quite']):
            print(f'\n{self.bold}Total packages to proceed: {packages}{self.endc}')
            print(f'{self.bold}Total sources to download: {download}{self.endc}')

        if self.command in remove and not self._is_extra_options(['-Q', '--quite']):
            print(f'\n{self.bold}Total packages to proceed: {packages}{self.endc}')
            print(f'{self.bold}Total packages size to remove: {size}{self.endc}')

    def _print_starts(self, count: int, message: str) -> None:
        """Print the message 'Starts the' with the proceeded message.

        Args:
            count (int): The count of packages.
            message (str): The proceeded message.
        """
        if not self._is_extra_options(['-Q', '--quite']):
            print(f'\n{self.bgreen}{self.square_emoji}{self.endc}{self.bold} Starts the {message} '
                  f'({count}):{self.endc}')

    def _print_resolving_message(self) -> None:
        """Print for resolving dependencies.
        """
        if not self._is_extra_options(['-o', '--resolve-deps', '-Q', '--quiet']):
            print('\rResolving dependencies ... ', end='')

    def _print_done_resolving_message(self) -> None:
        """Print the 'Done' message for resolving dependencies.
        """
        if not self._is_extra_options(['-o', '--resolve-deps', '-Q', '--quiet']):
            print('Done')

    def _print_complete_message(self) -> None:
        """Print the 'Complete' message.
        """
        if not self._is_extra_options(['-Q', '--quiet']):
            print(f'\nComplete{self.mark_emoji}')
        sys.exit(0)

    def _pkg_version(self, package: str) -> str:
        """Get the package version from the data.json file.

        Args:
            package (str): The name of the package.

        Returns:
            The version of the package.
        """
        if not self._is_extra_options(['-V', '--no-version']):
            return self.data[package]['version']
        return ''

    def _resolve_deps(self, package: str) -> tuple:
        """Resolve the package dependencies.

        Args:
            package (str): Package name to search for dependencies.

        Returns:
            Tuple with the package requires.
        """
        if not self._is_extra_options(['-o', '--no-deps']):
            requires: list[str] = self.data[package]['requires']
            for require in requires:
                sub_requires: list[str] = self.data[require]['requires']
                for sub in sub_requires:
                    if sub not in requires:
                        requires.append(sub)

            requires.reverse()

            requires = self._skip_installed_packages(requires)

            return tuple(dict.fromkeys(requires))
        return ()

    def _set_makeflags(self) -> None:
        """Set makeflags by config.
        """
        if self.makeflags:
            os.environ['MAKEFLAGS'] = self.makeflags

    def _set_output(self) -> None:
        """Set the build output path.
        """
        os.environ['OUTPUT'] = str(self.build_path)

    @staticmethod
    def _set_permissions(package: str, destination_dir: Path) -> None:
        """Change the access permissions to the .SlackBuild file.

        Args:
            package (str): Description
            destination_dir (Path): Description
        """
        os.chmod(Path(destination_dir, f'{package}.SlackBuild'), 0o755)

    def _delete_log_file(self) -> None:
        """Delete the old log file before starts the new one."""
        if self.log_file.is_file():
            self.log_file.unlink()

    def _edit_the_sbo(self, package: str, destination_dir: Path) -> None:
        """Print the README file.

        Args:
            package (str): Package name.
            destination_dir (Path): Path to the slackbuild file.
        """
        prgnam_slackbuild: Path = Path(destination_dir, f'{package}.SlackBuild')
        if self._is_extra_options(['-E', '--edit-sbo']) and prgnam_slackbuild.is_file():
            self.utils.run_process(f'{self.editor} {prgnam_slackbuild}')
            if not self._is_extra_options(['-n', '--no-confirm']) and self.no_confirm == 'off':
                try:
                    answer: str = input(f'\n{self.bred}{self.square_emoji}{self.endc}'
                                        f'{self.bold} Do you want to apply changes to the repository? [y/N] {self.endc}')
                except (KeyboardInterrupt, EOFError):
                    sys.exit(1)
                if answer in ['Y', 'y']:
                    location: str = self.data[package]['location']
                    edited_sbo: Path = Path(self.build_path, package, f'{package}.SlackBuild')
                    repo_sbo: Path = Path(self.lib_path, self.repo_name, self.repo_branch, location, package)
                    shutil.copy(edited_sbo, repo_sbo)

    def _view_readme(self, package: str, destination_dir: Path) -> None:
        """Print the README file.

        Args:
            package (str): Package name.
            destination_dir (Path): Path to the README file.
        """
        readme: Path = Path(destination_dir, 'README')
        if self._is_extra_options(['-a', '--view-readme']) and readme.is_file():
            title: str = f"Display 'README' for file {package}:"
            print(79 * '=')
            print(f"{self.bold}{title}{self.endc}")
            print(79 * '=')
            print(readme.read_text(encoding='utf-8'))
            print(79 * '=')
            self._question_proceed('building')
            print()

    def _depends_on(self, package: str) -> list:
        """Search for packages that depend on a package.

        Args:
            package (str): Package name.

        Returns:
            List with the package depends on.
        """
        depends_on: list = []
        for pkg, deps in self.data.items():
            if package in deps['requires']:
                depends_on.append(pkg)
        return depends_on

    def _is_package_exist(self, packages: list[str]) -> None:
        """Check if the package exist.

        Args:
            packages (list[str]): Packages name to check.
        """
        not_match: list[str] = []
        for pkg in packages:
            try:
                self.data[pkg]
            except KeyError:
                not_match.append(pkg)

        if not_match:
            print(f"\nNo matching packages were found for: {', '.join(not_match)}\n")
            sys.exit(1)

    def _is_extra_options(self, extra_options: list[str]) -> bool:
        """Check if an option exists in flags.

        Args:
            extra_options (list[str]): Extra options for check.

        Returns:
            bool
        """
        for flag in self.flags:
            if flag in extra_options:
                return True
        return False

    def _installpkg(self, package: str) -> None:
        """Install packages.

        Args:
            package (str): Package to install.
        """
        self._delete_log_file()
        command: str = f'{self.package_install} {package}'
        self._process_and_log(command)

    def _skip_installed_packages(self, packages: list) -> list:
        """Skip for installed packages.

        Args:
            packages (list): Packages for install or build.

        Returns:
            list: Packages.
        """
        if self._is_extra_options(['-k', '--skip-installed']):
            skip_packages: list = []
            for package in packages:
                if self.utils.is_installed(package):
                    skip_packages.append(package)
            new_packages: list = [p for p in packages if p not in skip_packages]

            return new_packages
        return packages

    def _load_data(self) -> None:
        """Check for data file and load it.
        """
        loading_message: str = '\rLoading packages data ... '
        if not self._is_extra_options(['-Q', '--quite']):
            print(loading_message, end='')
        if not self.json_data_file.is_file():
            print('Failed')
            print(f"\nFile '{self.json_data_file}' not found.\n")
            print('Did you update the repository?')
            print(f'\n  $ {self.prgnam} --update\n')
            sys.exit(1)

        self.data = self.utils.read_json_file(self.json_data_file)

        self.blacklist_packages = list(self.utils.read_packages_list(self.blacklist_file))

        if self.exclude_pkgs:
            self.blacklist_packages.extend(self.exclude_pkgs)

        if self.blacklist_packages:
            blacklist_packages: list = self.utils.ignore_packages(self.blacklist_packages,
                                                                  list(self.data.keys()))
            # Remove blacklist packages from main.
            for pkg in blacklist_packages:
                if pkg in self.data.keys():
                    del self.data[pkg]

            deps: list[str]
            # Remove blacklist packages from dependencies.
            for pkg, dep in self.data.items():
                if isinstance(dep, dict):
                    deps = dep['requires']
                for blk in blacklist_packages:
                    if blk in deps:
                        deps.remove(blk)
                        self.data[pkg]['requires'] = deps  # type: ignore
        if not self._is_extra_options(['-Q', '--quite']):
            print('Done')

    def options(self) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Manage the arguments.
        """
        args: list[Any] = sys.argv
        args.pop(0)

        options1: dict[str, Any] = {
            '-u': self.repo_update, '--update': self.repo_update,
            '-C': self.clean_tmp, '--clean-tmp': self.clean_tmp,
            '-h': self.cli_help.print_help, '--help': self.cli_help.print_help,
            '-v': self.print_version, '--version': self.print_version,
        }

        options2: dict[str, Callable[..., Any]] = {
            '-L': self.repo_changelog, '--repo-clog': self.repo_changelog,
            '-U': self.upgrade_packages, '--upgrade': self.upgrade_packages,
            '-b': self.build_install_packages, '--build': self.build_install_packages,
            '-i': self.build_install_packages, '--install': self.build_install_packages,
            '-q': self.view_package_requires, '--requires': self.view_package_requires,
            '-R': self.remove_packages, '--remove': self.remove_packages,
            '-e': self.view_package_dependees, '--dependees': self.view_package_dependees,
            '-s': self.search_packages, '--search': self.search_packages,
            '-f': self.find_installed_packages, '--find-installed': self.find_installed_packages,
            '-w': self.download_packages, '--download-only': self.download_packages,
            '-p': self.package_information, '--pkg-info': self.package_information,
            '-d': self.display_files, '--display': self.display_files
        }

        merged_options: list = []
        extra_options: list = [
            '-n', '--no-confirm',
            '-P', '--parallel',
            '-k', '--skip-installed',
            '-r', '--reinstall',
            '-V', '--no-version',
            '-Q', '--quiet',
            '-c', '--check-deps',
            '-E', '--edit-sbo',
            '-a', '--view-readme',
            '-o', '--no-deps',
            '-B', '--progress-bar',
            '-l', '--rows-list',
            '-g', '--gpg-off',
            '-m', '--checksum-off',
            '-x', '--exclude-pkgs='
        ]
        all_commands: list = list(itertools.chain(options1.keys(), options2.keys()))
        all_options: list = list(itertools.chain(options1.keys(), options2.keys(), extra_options))

        # If no arguments are invalid.
        if not args or '' in args[1:]:
            self.cli_help.invalid_options()

        # Choices for options 1.
        if len(args) == 1 and args[0] in options1:
            options1[args[0]]()

        # START TO MANAGE THE FLAGS.
        # Grab exclude packages and remove extra options from args.
        for arg in args:
            xpkgs: list = arg.split('=')
            if len(xpkgs) > 1:
                if xpkgs[0] == '--exclude-pkgs':
                    self.exclude_pkgs = xpkgs[1].split(',')
                    args.remove(arg)
            if arg == '-x':
                x_index: int = args.index(arg)
                xpkgs = args[x_index + 1:]
                self.exclude_pkgs = xpkgs[0].split(',')
                del args[x_index:len(args)]

        # Add extra options to flags.
        for arg in args:
            if arg in extra_options:
                self.flags.append(arg)

        # Add merged options to a list.
        for arg in args:
            if arg[0] == '-' and len(arg) > 2 and arg[1].isalpha():
                merged_options.append(arg)

        # Split merged options by individual flag etc ['-k', '-n', '-r'].
        if merged_options:
            for arg in merged_options[0][1:]:
                opt = f'-{arg}'
                if opt in extra_options:
                    self.flags.append(opt)
                if opt in all_commands:
                    args.append(opt)
                if opt not in all_options:
                    self.cli_help.invalid_options()

        # Clean args from extra options and merged options.
        for opt in merged_options + extra_options:
            if opt in args:
                args.remove(opt)
        # END TO MANAGE THE FLAGS.

        for arg in args:
            if arg.startswith('-') and arg not in all_options:
                self.cli_help.invalid_options()

        # Keep the command and clear the args.
        for arg in args:
            if arg in all_commands:
                self.command = arg
                args.remove(self.command)
                break

        # Delete the commands and left only the packages.
        args = [arg for arg in args if not arg.startswith('-')]

        if not self.command:
            self.cli_help.invalid_options()

        if self._is_extra_options(['-r', '--reinstall']):
            self.package_install = self.reinstall_command

        if self.command in ['-U', '--upgrade']:
            options2[self.command]()

        # Choices for options 2.
        if self.command in options2:
            packages: list = list(set(args))

            # Getting binaries ('.tgz', '.txz') or filelist.
            files: list = []
            install_binaries: list = []
            for package in packages:
                if package.endswith((self.pkgtype, self.slack_pkgtype)):
                    self._installpkg(package)
                    install_binaries.append(package)
                if package.endswith(self.pkglist_suffix):
                    files.append(package)
                    packages.extend(self.utils.read_packages_list(Path(package)))

            # Keep the slackbuilds and remove the files and packages ends in ('.pkgs', '.tgz', '.txz').
            packages = [pkg for pkg in packages if pkg not in files + install_binaries]

            # Exit when try to install local binaries packages
            # without any other packages.
            if not packages and install_binaries:
                sys.exit(0)

            if self.command in ['-L', '--repo-clog'] and not packages:
                options2[self.command]()

            if not packages:
                self.cli_help.invalid_options()

            # Load data before call the methods.
            self._load_data()

            if self.command in ['-R', '--remove',
                                '-f', '--find-installed',
                                '-s', '--search',
                                '-L', '--repo-clog']:
                options2[self.command](packages)

            if '*' in packages:
                # Remove '*' from packages.
                packages = [item for item in packages if item != '*']
                # Check if the packages exist to the repository.
                self._is_package_exist(packages)
                # Load all repository packages to the package list.
                packages.extend(list(self.data.keys()))
            else:
                self._is_package_exist(packages)

            options2[self.command](packages)

        else:
            self.cli_help.invalid_options()


def run() -> None:
    """Run the app.
    """
    if not os.geteuid() == 0:
        raise SystemExit('Must run as root.')

    sbpkg = SBpkg()
    sbpkg.options()


if __name__ == '__main__':
    run()

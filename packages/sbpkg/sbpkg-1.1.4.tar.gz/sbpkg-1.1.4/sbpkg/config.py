#!/bin/python3
# -*- coding: utf-8 -*-

import configparser
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class Config:  # pylint: disable=[R0902]
    """General configurations settings.
    """

    try:
        config = configparser.ConfigParser()
        config.read('/etc/sbpkg/sbpkg.conf')

        # [REPOSITORY]
        repo_name: str = config['REPOSITORY']['name']
        repo_branch: str = config['REPOSITORY']['branch']
        local_repo: Path = Path(config['REPOSITORY']['local_repo'])
        changelog_txt: str = config['REPOSITORY']['changelog']

        # [MIRRORS]
        repo_mirror: str = config['MIRRORS']['mirror']

        if '.git' in repo_mirror:
            parsed_url = urlparse(repo_mirror)
            path_parts = parsed_url.path.strip("/").split("/")
            owner = path_parts[0]
            repository_name: str = path_parts[1].replace('.git', '')
            repo_branch = repo_branch

            if 'github.com' in repo_mirror:
                repo_git_mirror: str = f'https://raw.githubusercontent.com/{owner}/{repository_name}/{repo_branch}/'

            if 'gitlab.com' in repo_mirror:
                repo_git_mirror = f'https://gitlab.com/{owner}/{repository_name}/-/raw/{repo_branch}/'

        slackbuilds_txt: str = config['REPOSITORY']['slackbuilds']
        repo_tag: str = config['REPOSITORY']['tag']
        pkgtype: str = config['REPOSITORY']['pkgtype']
        compressed: str = config['REPOSITORY']['compressed']
        gpg_archive: str = config['REPOSITORY']['gpg_archive']

        # [PATH]
        tmp: Path = Path(config['PATH']['tmp'])
        tmp_sbpkg_path: Path = Path(config['PATH']['tmp_sbpkg'])
        build_path: Path = Path(config['PATH']['build'])
        lib_path: Path = Path(config['PATH']['library'])
        log_path: Path = Path(config['PATH']['log'])
        log_pkgs_path: Path = Path(config['PATH']['packages'])
        etc_path: Path = Path(config['PATH']['etc'])
        download_path: Path = Path(config['PATH']['download'])

        # [RSYNC]
        rsync: str = 'rsync'
        rsync_options: str = config['RSYNC']['options']

        # [LFTP]
        lftp: str = 'lftp'
        lftp_options: str = config['LFTP']['options']

        # [GIT]
        git: str = 'git clone --depth 1'

        # [WGET]
        wget: str = 'wget'
        wget_options: str = config['WGET']['options']

        # [SLACKWARE]
        install_command: str = config['SLACKWARE']['install']
        reinstall_command: str = config['SLACKWARE']['reinstall']
        remove_command: str = config['SLACKWARE']['remove']
        slack_pkgtype: str = config['SLACKWARE']['pkgtype']

        # [MISC]
        colors: str = config['MISC']['colors'].lower()
        progress_bar: str = config['MISC']['progress_bar'].lower()
        parallel_downloads: str = config['MISC']['parallel_downloads'].lower()
        maximum_parallel: int = int(config['MISC']['maximum_parallel'])
        makeflags: str = config['MISC']['makeflags']
        pkglist_suffix: str = config['MISC']['pkglist_suffix']
        editor: str = config['MISC']['editor']
        gpg_verification: str = config['MISC']['gpg_verification'].lower()
        checksum_md5: str = config['MISC']['checksum_md5'].lower()
        kernel_version: str = config['MISC']['kernel_version'].lower()
        no_confirm: str = config['MISC']['no_confirm'].lower()

    except KeyError as e:
        print(f'\nsbpkg: Error in the configuration file: {e}')
        if Path('/etc/sbpkg/sbpkg.conf.new').is_file():
            print('Check for sbpkg.conf.new configuration file.')
        print()
        raise SystemExit(1) from e

    # Settings outside to configparser.
    arch: str = platform.machine().lower()
    arch_os: str = platform.architecture()[0]
    json_data_file: Path = Path(lib_path, repo_name, repo_branch, 'data.json')
    log_file: Path = Path(log_path, 'sbpkg.log')
    deps_log_file: Path = Path(log_path, 'deps.log')
    upgrade_log_file: Path = Path(log_path, 'upgrade.log')
    blacklist_file: Path = Path(etc_path, 'blacklist')

    if not editor:
        editor = os.environ['EDITOR']

    # Setting the colors.
    bold: str = ''
    black: str = ''
    green: str = ''
    cyan: str = ''
    red: str = ''
    yellow: str = ''
    grey: str = ''
    bgreen: str = ''
    bcyan: str = ''
    bred: str = ''
    byellow: str = ''
    white_bg: str = ''
    endc: str = ''

    if colors == 'on':
        bold = '\x1b[1m'
        black = '\x1b[30m'
        green = '\x1b[32m'
        cyan = '\x1b[96m'
        red = '\x1b[91m'
        yellow = '\x1b[93m'
        grey = '\x1b[38;5;247m'
        bgreen = f'{bold}{green}'
        bcyan = f'{bold}{cyan}'
        bred = f'{bold}{red}'
        byellow = f'{bold}{yellow}'
        white_bg = '\x1b[107m'
        endc = '\x1b[0m'

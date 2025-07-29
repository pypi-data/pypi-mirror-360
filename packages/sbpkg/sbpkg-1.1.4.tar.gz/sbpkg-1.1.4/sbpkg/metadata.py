#!/bin/python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass
class Metadata:
    """Metadata values.
    """

    __prgnam__: str = 'sbpkg'
    __version__: str = '1.1.4'
    __description__: str = 'Simple, fast and full-featured SBo package manager.'
    __license__: str = 'GNU General Public License v3 or later (GPLv3+)'
    __year__: str = '2024-2025'
    __author__: str = 'dslackw'
    __email__: str = 'dslackw@gmail.com'

#!/bin/python3
# -*- coding: utf-8 -*-


from dataclasses import dataclass

from sbpkg.support import is_ascii_compatible_terminal, is_unicode_supported


@dataclass
class Chars:
    """ASCII characters.
    """

    # ASCII chars.
    ascii_line: str = '_'
    ascii_ldc: str = '|'
    ascii_var: str = '|'

    # Emojis chars.
    mark_emoji: str = '!'
    square_emoji: str = ':'

    if is_ascii_compatible_terminal():
        ascii_line = '─'
        ascii_ldc = '└'
        ascii_var = '├'

    if is_unicode_supported():
        mark_emoji = '！'
        square_emoji = '◼'

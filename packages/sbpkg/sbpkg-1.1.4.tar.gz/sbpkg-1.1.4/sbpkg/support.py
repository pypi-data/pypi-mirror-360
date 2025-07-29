#!/bin/python3
# -*- coding: utf-8 -*-

import sys


def is_unicode_supported() -> bool:
    """Check for Unicode characters support.

    Returns:
        bool: True or False
    """
    try:
        # Check if sys.stdout.encoding is set and supports Unicode
        return sys.stdout.encoding.lower() in ["utf-8", "utf-16", "utf-32", "utf-8-sig"]
    except AttributeError:
        # sys.stdout.encoding might not be available in some environments
        return False


def is_ascii_compatible_terminal() -> bool:
    """Check for ascii terminal compatible.

    Returns:
        bool: True or False
    """
    try:
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding is None:
            return False

        "A".encode(sys.stdout.encoding)
        return True
    except (LookupError, UnicodeEncodeError):
        return False
    except Exception:  # pylint: disable=[W0718]
        return False

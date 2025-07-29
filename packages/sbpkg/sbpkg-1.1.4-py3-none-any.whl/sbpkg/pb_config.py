#!/bin/python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass
class PbConfig:
    """Progress bar configs.
    """

    # Progress bar configs.
    pb_left: str = '['
    pb_right: str = ']'
    pb_move: str = '<=>'
    pb_max_width: int = 18
    pb_position: int = 0
    pb_direction: int = 1

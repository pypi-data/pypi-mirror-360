"""
Common utilities for RZ-CI Robot Framework
"""

from .board_config import Board, get_config, set_board_type, get_board_config

__all__ = [
    'Board',
    'get_config',
    'set_board_type',
    'get_board_config',
]

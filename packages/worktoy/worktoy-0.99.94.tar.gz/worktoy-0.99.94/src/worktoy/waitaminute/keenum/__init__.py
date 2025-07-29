"""The 'worktoy.waitaminute.keenum' module provides custom exceptions used
by the 'worktoy.keenum' module."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._duplicate_kee_num import DuplicateKeeNum
from ._empty_kee_num_error import EmptyKeeNumError
from ._kee_num_type_exception import KeeNumTypeException

__all__ = [
    'DuplicateKeeNum',
    'EmptyKeeNumError',
    'KeeNumTypeException',
]

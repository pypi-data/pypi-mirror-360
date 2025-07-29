"""
The 'worktoy.keenum' module provides the enumerating KeeNum class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._keenum_base import _KeeNumBase  # Private
from ._auto import auto
from ._auto import _AutoMember
from ._kee_hook import KeeSpaceHook
from ._kee_space import KeeSpace
from ._kee_meta import KeeMeta
from ._keenum import KeeNum

__all__ = [
    'auto',
    'KeeSpaceHook',
    'KeeSpace',
    'KeeMeta',
    'KeeNum',
]

"""The 'worktoy.static' module provides low level parsing and casting
utilities. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from ._type_cast import typeCast
from ._pre_class import PreClass
from ._type_sig import TypeSig
from ._dispatch import Dispatch
from ._overload import overload

__all__ = [
    'typeCast',
    'PreClass',
    'TypeSig',
    'Dispatch',
    'overload',
]

"""
The 'worktoy.waitaminute.dispatch' module provides custom exceptions
specifically related to the overload control flow.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._dispatch_exception import DispatchException
from ._hash_mismatch import HashMismatch
from ._cast_mismatch import CastMismatch
from ._flex_mismatch import FlexMismatch
from ._type_cast_exception import TypeCastException

___all__ = [
    'DispatchException',
    'HashMismatch',
    'CastMismatch',
    'FlexMismatch',
    'TypeCastException',
]

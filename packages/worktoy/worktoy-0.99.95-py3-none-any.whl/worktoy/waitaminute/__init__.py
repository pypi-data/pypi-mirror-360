"""
The 'worktoy.waitaminute' package provides the custom exceptions used
across the 'worktoy' library.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import desc
from . import meta
from . import dispatch
from ._attribute_error_factory import attributeErrorFactory
from ._type_exception import TypeException
from ._write_once_error import WriteOnceError
from ._missing_variable import MissingVariable
from ._variable_not_none import VariableNotNone
from ._unpack_exception import UnpackException
from ._path_syntax_exception import PathSyntaxException
from ._subclass_exception import SubclassException

___all__ = [
    'desc',
    'meta',
    'dispatch',
    'attributeErrorFactory',
    'TypeException',
    'WriteOnceError',
    'MissingVariable',
    'VariableNotNone',
    'UnpackException',
    'PathSyntaxException',
    'SubclassException',
]

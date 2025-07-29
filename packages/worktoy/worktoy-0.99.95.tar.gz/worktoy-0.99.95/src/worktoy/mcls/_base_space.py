"""
BaseSpace provides the namespace class used by worktoy.mcls.BaseMeta
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from types import FunctionType as Func
from typing import TYPE_CHECKING

from ..waitaminute import VariableNotNone
from ..static import TypeSig
from . import AbstractNamespace, AbstractMetaclass
from .space_hooks import OverloadSpaceHook, PreClassSpaceHook

if TYPE_CHECKING:  # pragma: no cover
  from typing import TypeAlias, Callable, Any

  OverloadMap: TypeAlias = dict[str, dict[TypeSig, Callable[..., Any]]]


class BaseSpace(AbstractNamespace):
  """
  BaseSpace is the namespace used by BaseMeta. It enables function
  overloading and related features via hook registration.

  Classes defined using this namespace support method overloading through
  hooks installed automatically in the class body. These hooks handle
  overload collection, dispatch construction, and support for 'THIS' as a
  placeholder during class creation.

  The overload mechanism and other behavior are defined in
  `worktoy.mcls.hooks`. This namespace is returned from BaseMeta.__prepare__.
  """

  __overload_map__ = None

  def _buildOverloadMap(self, ) -> None:
    """Build the overload map for the namespace."""
    if self.__overload_map__ is not None:
      raise VariableNotNone('__overload_map__', self.__overload_map__)
    mcls = self.getMetaclass()
    bases = self.getBases()
    baseSpaces = []
    self.__overload_map__ = {}
    for base in bases:
      if isinstance(base, AbstractMetaclass):
        baseSpaces.append(base.getNamespace())
    while baseSpaces:
      space = baseSpaces.pop()
      baseOverloadMap = space.getOverloadMap()
      for key, overloads in baseOverloadMap.items():
        existing = self.__overload_map__.get(key, {})
        for sig, func in overloads.items():
          existing[sig] = func
        self.__overload_map__[key] = existing

  def getOverloadMap(self, **kwargs) -> OverloadMap:
    """Get the overload map for the namespace."""
    if self.__overload_map__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError  # pragma: no cover
      self._buildOverloadMap()
      return self.getOverloadMap(_recursion=True)
    return self.__overload_map__

  def addOverload(self, key: str, sig: TypeSig, func: Func) -> None:
    """Add an overload to the overload map."""
    overloadMap = self.getOverloadMap()
    existingMap = overloadMap.get(key, {})
    existingMap[sig] = func
    overloadMap[key] = existingMap
    self.__overload_map__ = overloadMap

  preClassHook = PreClassSpaceHook()
  overloadHook = OverloadSpaceHook()

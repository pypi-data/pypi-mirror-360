"""
KeeHook provides the namespace hook for the KeeSpace namespace class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls.space_hooks import AbstractSpaceHook
from . import _AutoMember
from ..waitaminute.keenum import KeeNumTypeException, DuplicateKeeNum

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class KeeSpaceHook(AbstractSpaceHook):
  """
  KeeHook provides the namespace hook for the KeeSpace namespace class.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _addMember(self, name: str, value: Any = None, **kwargs) -> None:
    """
    Add a member to the KeeSpace namespace.
    """
    if isinstance(value, _AutoMember):
      value = value.getValue()
    if value is None:
      if kwargs.get('_recursion2', False):
        raise RecursionError  # pragma: no cover
      return self._addMember(name, name, _recursion2=True)
    valueType = self._getValueType()
    if valueType is None:
      if kwargs.get('_recursion', False):
        raise RecursionError  # pragma: no cover
      self._setValueType(type(value))
      return self._addMember(name, value, _recursion=True)
    else:
      if not isinstance(value, valueType):
        raise KeeNumTypeException(name, value, valueType)
    existing = self.space.get('__future_entries__', {})
    if name in existing:
      raise DuplicateKeeNum(name, value)
    existing[name] = value
    self.space['__future_entries__'] = existing

  def _setValueType(self, valueType: type, ) -> None:
    """
    Set the value type for the KeeSpace namespace.
    """
    self.space['__future_value_type__'] = valueType

  def _getValueType(self) -> type:
    """
    Get the value type for the KeeSpace namespace.
    """
    return self.space.get('__future_value_type__', None)

  def setItemPhase(self, key: str, value: Any, oldValue: Any, ) -> bool:
    """
    The setItemHook method is called when an item is set in the
    namespace.
    """
    if key.startswith('__') and key.endswith('__'):
      # Skip special keys
      return False
    if callable(value):
      return False
    self._addMember(key.upper(), value)
    return False

  def preCompilePhase(self, compiledSpace: dict) -> dict:
    """Hook for preCompile. This is called before the __init__ method of
    the namespace object is called. The default implementation does nothing
    and returns the contents unchanged. """
    compiledSpace['__future_entries__'] = dict()
    return compiledSpace

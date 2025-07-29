"""DataField represents an entry in the EZData classes. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.waitaminute import TypeException


class DataField:
  """DataField represents an entry in the EZData classes. """
  __slots__ = ('key', 'type_', 'val')

  def __init__(self, key: str, type_: type, val: object = None) -> None:
    """Initialize the DataField object."""
    if not isinstance(key, str):
      raise TypeException('key', key, str)
    if not isinstance(type_, type):
      raise TypeException('type_', type_, type)
    if not isinstance(val, type_):
      if val is None:
        try:
          val = type.__call__(type_, )
        except (TypeError, ValueError) as exc:
          raise TypeException('val', val, type_) from exc
      else:
        raise TypeException('val', val, type_)
    self.key = key
    self.type_ = type_
    self.val = val

  def __str__(self) -> str:
    """Get the string representation of the DataField object."""
    infoSpec = """%s: %s = %s(%s)"""
    clsName = type(self).__name__
    typeName = self.type_.__name__
    return infoSpec % (self.key, typeName, clsName, self.val)

  def __repr__(self) -> str:
    """
    Get the code that would create this DataField object.
    """
    infoSpec = """%s(%r, %r, %r)"""
    clsName = type(self).__name__
    typeName = self.type_.__name__
    return infoSpec % (clsName, self.key, typeName, self.val)

  def __eq__(self, other: object) -> bool:
    """
    Compares other against self.val or if other is also a 'DataField'
    object, compares against self.key, self.type_, and self.val.
    """
    if type(self) is type(other):
      if TYPE_CHECKING:  # pragma: no cover
        assert isinstance(other, DataField)
      if self is other:
        return True
      if self.key != other.key:
        return False
      if self.type_ != other.type_:
        return False
      if self.val != other.val:
        return False
      return True
    if isinstance(other, self.type_):
      return True if self.val == other else False
    return NotImplemented

  def __hash__(self) -> int:
    """
    Returns the hash of the DataField object.
    """
    return hash((self.key, self.type_.__name__, self.val))

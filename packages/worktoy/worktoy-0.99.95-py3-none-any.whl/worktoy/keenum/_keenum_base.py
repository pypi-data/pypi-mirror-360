"""
The _KeeNumBase class provides a base for the KeeNum class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..desc import Field
from ..core import Object
from ..waitaminute import MissingVariable, TypeException
from ..waitaminute.meta import IllegalInstantiation

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class _KeeNumBase(Object):
  """
  The _KeeNumBase class provides a base for the KeeNum class.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __member_name__ = None  # Future name of the enumeration member
  __member_value__ = None  # Future value of the enumeration member
  __member_index__ = None  # Future index of the enumeration member
  __value_type__ = None  # Future type of the enumeration member values

  #  Public Variables
  name = Field()
  value = Field()
  index = Field()
  valueType = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  @name.GET
  def _getName(self) -> str:
    """Get the name of the enumeration member."""
    if self.__member_name__ is None:
      raise MissingVariable('__member_name__', str)
    if isinstance(self.__member_name__, str):
      return self.__member_name__
    raise TypeException('__member_name__', self.__member_name__, str)

  @value.GET
  def _getValue(self) -> Any:
    """Get the value of the enumeration member."""
    if self.__member_value__ is None:
      return self.__member_name__.upper()
    return self.__member_value__

  @index.GET
  def _getIndex(self) -> int:
    """Get the index of the enumeration member."""
    if self.__member_index__ is None:
      raise MissingVariable('__member_index__', int)
    if isinstance(self.__member_index__, int):
      return self.__member_index__
    raise TypeException('__member_index__', self.__member_index__, int)

  @valueType.GET
  def _getValueType(self) -> type:
    """Get the type of the enumeration member values."""
    if self.__value_type__ is None:
      raise MissingVariable('__value_type__', type)
    if isinstance(self.__value_type__, type):
      return self.__value_type__
    raise TypeException('__value_type__', self.__value_type__, type)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __str__(self) -> str:
    """
    String representation of the enumeration member.
    """
    clsName = type(self).__name__
    return """%s.%s""" % (clsName, self.name.upper())

  def __repr__(self) -> str:
    """
    Representation of the enumeration member.
    """
    typeName = self.valueType.__name__
    infoSpec = """<%s[%s]: %s>"""
    info = infoSpec % (str(self), typeName, repr(self.value))
    if len(info) > 77:
      return '%s...' % info[:74]
    return info

  def __hash__(self) -> int:
    """
    Hash representation of the enumeration member.
    """
    clsName = type(self).__name__
    baseNames = 'Object',
    mclsName = 'type'
    clsHash = hash((clsName, *baseNames, mclsName))
    return hash((clsHash, self.name, self.value, self.index))

  def __eq__(self, other: Any) -> bool:
    """
    Equality check for the enumeration member.
    """
    if self is other:
      return True
    cls = type(self)
    if not isinstance(other, cls):
      return NotImplemented
    return True if self.value == other.value else False

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, *args, **kwargs) -> None:
    """
    The control flow instantiates and initializes the members
    automatically. Do not reimplement or change this function. Developers
    of 'worktoy' considers this function guaranteed to remain unchanged.
    Changing it causes undefined behavior. For this reason, future
    versions are planned to specifically raise RuntimeError if this
    function is reimplemented or changed.

    As of development version 0.99.85, this function could be
    reimplemented by setting the '_root' keyword argument to True,
    but a much better method of preventing instantiation is in the works.
    This new prevention scheme will be backwards compatible, ensuring
    that libraries depending on 'worktoy.keenum' can safely upgrade,
    provided they do not reimplement this function!
    """
    if not kwargs.get('_root', False):
      raise IllegalInstantiation(type(self))

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

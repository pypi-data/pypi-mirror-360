"""
KeeMeta provides the metaclass creating the KeeNum enumeration class.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls import AbstractMetaclass
from ..utilities import textFmt
from ..waitaminute import TypeException
from ..waitaminute.meta import IllegalInstantiation
from ..waitaminute.keenum import EmptyKeeNumError
from . import KeeSpace, _KeeNumBase

if TYPE_CHECKING:  # pragma: no cover
  from typing import Self, TypeAlias, Any, Iterator

  Bases: TypeAlias = tuple[type, ...]
  MTypes: TypeAlias = dict[str, type]


class KeeMeta(AbstractMetaclass):
  """
  KeeMeta provides the metaclass creating the KeeNum enumeration class.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __core_keenum__ = None  # Future KeeNum base class

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def _createCoreKeeNum(mcls, ) -> Self:
    """
    Creator function for the core KeeNum class.
    """

    class KeeNum(_KeeNumBase, metaclass=mcls):
      """
      KeeNum provides the base class for enumerating classes with
      restricted and predefined instances called members.
      """
      pass

    setattr(mcls, '__core_keenum__', KeeNum)

  @classmethod
  def getCoreKeeNum(mcls, **kwargs) -> type:
    """
    Get the core KeeNum class.
    """
    if mcls.__core_keenum__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError  # pragma: no cover
      mcls._createCoreKeeNum()
      return mcls.getCoreKeeNum(_recursion=True)
    return mcls.__core_keenum__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases, **kwargs) -> KeeSpace:
    """
    Prepare the class namespace.
    """
    return KeeSpace(mcls, name, bases, **kwargs)

  def __new__(mcls, name: str, bases: Bases, space: KeeSpace, **kw) -> Self:
    """
    Create a new instance of the KeeMeta metaclass.
    """
    if name == 'KeeNum' or kw.get('_root', False):
      return super().__new__(mcls, name, bases, space, **kw)
    coreKeeNum = mcls.getCoreKeeNum()
    return super().__new__(mcls, name, (coreKeeNum,), space, **kw)

  def __init__(cls, name: str, bases: Bases, space: KeeSpace, **kw) -> None:
    """
    Initialize the KeeMeta metaclass.
    """
    super().__init__(name, bases, space, **kw)
    if name == 'KeeNum':
      return
    futureEntries = getattr(cls, '__future_entries__', )
    actualEntries = dict()
    valueType = getattr(cls, '__future_value_type__', None)
    if valueType is None:
      raise EmptyKeeNumError(name)
    memberValues = []
    memberNames = []
    for i, (name, value) in enumerate(futureEntries.items()):
      entry = cls(_root=True)
      entry.__member_name__ = name
      entry.__member_value__ = value
      entry.__member_index__ = i
      memberValues.append(value)
      memberNames.append(name)
      actualEntries[name] = entry
      setattr(cls, name, entry)

    setattr(cls, '__value_type__', valueType)
    setattr(cls, '__member_entries__', actualEntries)
    delattr(cls, '__future_entries__')
    delattr(cls, '__future_value_type__')

  def __call__(cls, *args, **kwargs) -> Any:
    """
    Only the _addMember method is allowed to create instances of the
    KeeNum class.
    """
    if not kwargs.get('_root', False):
      try:
        member = cls.__getitem__(args[0])
      except Exception as exception:
        raise IllegalInstantiation(cls) from exception
      else:
        return member
    self = super().__call__(**kwargs)
    return self

  def __len__(cls) -> int:
    """
    Get the number of members in the KeeNum class.
    """
    out = 0
    for _ in cls:
      out += 1
    else:
      return out

  def __iter__(cls, ) -> Iterator:
    """
    Iterate over the members of the KeeNum class.
    """
    yield from getattr(cls, '__member_entries__', ).values()

  def __getitem__(cls, key: str) -> Any:
    """
    Get a member by its name.
    """
    valueType = getattr(cls, '__value_type__', None)
    if isinstance(key, int):
      return cls._getFromIndex(key)
    if isinstance(key, str):
      return cls._getFromName(key)
    if isinstance(key, valueType):
      return cls._getFromValue(key)
    raise TypeException('key', key, int, str, valueType)

  def _getFromIndex(cls, index: int) -> Any:
    """
    Get a member by its index. If the value type is 'int' and the index is
    negative, this method assumes that the index does not match any value
    type.
    """
    if index < 0:
      return cls._getFromIndex(len(cls) + index)
    for entry in cls:
      if entry.index == index:
        return entry
    infoSpec = """Index %d out of range for %s"""
    info = infoSpec % (index, cls.__name__)
    raise IndexError(textFmt(info))

  def _getFromName(cls, name: str, **kwargs) -> Any:
    """
    Get a member by its name. If the value type is 'str', this method
    assumes that the identifier does not match any value type.
    """
    for entry in cls:
      if entry.name == name:
        return entry
    for entry in cls:
      entryName = entry.name.lower().replace('_', '')
      lookupName = name.lower().replace('_', '')
      if entryName == lookupName:
        return entry
    raise KeyError(name)

  def _getFromValue(cls, value: Any, **kwargs) -> Any:
    """
    Get a member by its value.
    """
    for entry in cls:
      if entry.value == value:
        return entry
    raise ValueError(value)

  def __str__(cls) -> str:
    """
    String representation of the KeeMeta metaclass.
    """
    if cls.__name__ == 'KeeNum':
      return """<class 'KeeNum'>"""
    valueType = getattr(cls, '__value_type__', )
    typeName = '' if valueType is str else valueType.__name__
    clsName = cls.__name__
    infoSpec = """%s(KeeNum)[%s]"""
    return infoSpec % (clsName, typeName)

  __repr__ = __str__

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

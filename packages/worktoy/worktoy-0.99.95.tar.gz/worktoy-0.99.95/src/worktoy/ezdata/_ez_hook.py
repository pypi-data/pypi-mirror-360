"""EZHook collects the field entries in EZData class bodies. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from types import FunctionType
from typing import TYPE_CHECKING

from ..mcls.space_hooks import AbstractSpaceHook, ReservedNames
from ..waitaminute.meta import ReservedName

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Iterator
  from worktoy.ezdata import EZData


class EZSpaceHook(AbstractSpaceHook):
  """EZHook collects the field entries in EZData class bodies. """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class Variables
  __auto_names__ = """__slots__, __init__, __eq__, __str__, __repr__,
    __iter__, __getitem__, __setitem__, __getattr__"""

  #  Public Variables
  reservedNames = ReservedNames()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Hook methods

  def preCompilePhase(self, compiledSpace: dict) -> dict:
    """The preCompileHook method is called before the class is compiled."""
    dataFields = self.space.getDataFields()
    compiledSpace['__slots__'] = (
        *[dataField.key for dataField in dataFields],)
    return compiledSpace

  def postCompilePhase(self, compiledSpace: dict) -> dict:
    """The postCompileHook method is called after the class is compiled."""
    dataFields = self.space.getDataFields()
    initMethod = self.initFactory(*dataFields)
    eqMethod = self.eqFactory(*dataFields)
    hashMethod = self.hashFactory(*dataFields)
    strMethod = self.strFactory(*dataFields)
    reprMethod = self.reprFactory(*dataFields)
    iterMethod = self.iterFactory(*dataFields)
    lenMethod = self.lenFactory(*dataFields)
    getItemMethod = self.getItemFactory(*dataFields)
    setItemMethod = self.setItemFactory(*dataFields)
    compiledSpace['__init__'] = initMethod
    compiledSpace['__eq__'] = eqMethod
    compiledSpace['__hash__'] = hashMethod
    compiledSpace['__str__'] = strMethod
    compiledSpace['__repr__'] = reprMethod
    compiledSpace['__iter__'] = iterMethod
    compiledSpace['__len__'] = lenMethod
    compiledSpace['__getitem__'] = getItemMethod
    compiledSpace['__setitem__'] = setItemMethod
    return compiledSpace

  def setItemPhase(self, key: str, value: Any, oldValue: Any, ) -> bool:
    """The setItemHook method is called when an item is set in the
    enumeration."""
    if key in self.__auto_names__:
      if not hasattr(value, '__is_root__'):
        raise ReservedName(key)
    if key in self.reservedNames:
      return False  # Already handled by ReservedNameHook
    if callable(value):
      return False
    self.space.addField(key, type(value), value)
    return True

  # \_____________________________________________________________________/ #
  #  Method factories
  # /¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨\ #
  @staticmethod
  def initFactory(*dataFields) -> FunctionType:
    """
    Creates the '__init__' method for the EZData class.
    """

    slotKeys = [dataField.key for dataField in dataFields]
    defVals = [dataField.val for dataField in dataFields]

    def __init__(self, *args, **kwargs) -> None:
      """
      The generated '__init__' method sets attributes on the instance
      based on given arguments. Keyword arguments take precedence.
      Positional arguments are applied in order.
      """
      posArgs = [*args, ]
      while len(posArgs) < len(slotKeys):
        posArgs.append(None)
      for key, defVal in zip(slotKeys, defVals):
        setattr(self, key, defVal)
      for key, arg in zip(slotKeys, posArgs):
        if arg is not None:
          setattr(self, key, arg)
      for key in slotKeys:
        if key in kwargs:
          setattr(self, key, kwargs[key])

    return __init__

  @staticmethod
  def eqFactory(*dataFields) -> FunctionType:
    """
    Creates the '__eq__' method for the EZData class.
    """

    def __eq__(self, other: EZData) -> bool:
      """
      Instances of EZData are equal if each of their data fields are equal.
      """
      if type(self) is not type(other):
        return NotImplemented
      for dataField in dataFields:
        key = dataField.key
        if getattr(self, key) != getattr(other, key):
          return False
      return True

    return __eq__

  @staticmethod
  def hashFactory(*dataFields) -> FunctionType:
    """
    Creates the '__hash__' method for the EZData class.
    """

    def __hash__(self) -> int:
      """
      The hash of an EZData instance is the hash of its data fields.
      """
      hashVal = 0
      for dataField in dataFields:
        key = dataField.key
        val = getattr(self, key)
        hashVal ^= hash(val)
      return hashVal

    return __hash__

  @staticmethod
  def strFactory(*dataFields) -> FunctionType:
    """The strFactory method is called when the class is created."""

    def __str__(self) -> str:
      """The __str__ method is called when the class is created."""
      clsName = type(self).__name__
      keys = [dataField.key for dataField in dataFields]
      vals = [str(getattr(self, key)) for key in keys]
      keyVals = ['%s=%s' % (key, val) for key, val in zip(keys, vals)]
      return """%s(%s)""" % (clsName, ', '.join(keyVals))

    return __str__

  @staticmethod
  def reprFactory(*dataFields) -> FunctionType:
    """The reprFactory method is called when the class is created."""

    def __repr__(self) -> str:
      """The __repr__ method is called when the class is created."""
      clsName = type(self).__name__
      keys = [dataField.key for dataField in dataFields]
      vals = [str(getattr(self, key)) for key in keys]
      return """%s(%s)""" % (clsName, ', '.join(vals))

    return __repr__

  @staticmethod
  def iterFactory(*dataFields) -> FunctionType:
    """The iterFactory method is called when the class is created."""

    def __iter__(self, ) -> Iterator:
      """
      Implementation of the iteration protocol
      """
      for key in self.__slots__:
        yield getattr(self, key)

    return __iter__

  @staticmethod
  def lenFactory(*dataFields) -> FunctionType:
    """The lenFactory method is called when the class is created."""

    def __len__(self) -> int:
      """The __len__ method is called when the class is created."""
      return len(self.__slots__)

    return __len__

  @staticmethod
  def getItemFactory(*dataFields) -> FunctionType:
    """The getItemFactory method is called when the class is created."""

    def __getitem__(self, key: str) -> object:
      """The __getitem__ method is called when the class is created."""
      if key in self.__slots__:
        return getattr(self, key)
      raise KeyError(key)

    return __getitem__

  @staticmethod
  def setItemFactory(*dataFields) -> FunctionType:
    """The setItemFactory method is called when the class is created."""

    def __setitem__(self, key: str, value: object) -> None:
      """The __setitem__ method is called when the class is created."""
      if key in self.__slots__:
        return setattr(self, key, value)
      raise KeyError(key)

    return __setitem__

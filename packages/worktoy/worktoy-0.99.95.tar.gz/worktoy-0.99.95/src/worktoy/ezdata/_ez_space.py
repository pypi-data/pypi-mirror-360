"""EZSpace provides the namespace for the EZData class. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import DataField, EZSpaceHook
from ..mcls import BaseSpace
from ..utilities import maybe


class EZSpace(BaseSpace):
  """
  EZSpace provides the namespace for the EZData class.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private Variables
  __data_fields__ = None

  #  Public Variables
  ezHook = EZSpaceHook()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def getDataFields(self) -> list[DataField]:
    """Get the data fields."""
    out = maybe(self.__data_fields__, [])
    bases = [*self.getBases(), ]
    for base in bases:
      space = getattr(base, '__namespace__', None)
      fields = getattr(space, '__data_fields__', None)
      if fields is None:
        continue
      for field in fields:
        if field.key not in [f.key for f in out]:
          out.append(field)
    return out

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def addField(self, key: str, type_: type, val: object) -> None:
    """Add a field to the data fields."""
    if self.__data_fields__ is None:
      self.__data_fields__ = []
    dataField = DataField(key, type_, val)
    existing = self.getDataFields()
    self.__data_fields__ = [*existing, dataField]

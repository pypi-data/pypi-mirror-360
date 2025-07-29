"""MissingVariable exception should be raised when a variable is missing
and requires initialization. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
  pass


class MissingVariable(Exception):
  """MissingVariable exception should be raised when a variable is missing
  and requires initialization. """

  __slots__ = ('varName', 'varType')

  def __init__(self, name: str, type_: type) -> None:
    """Initialize the MissingVariable object."""
    self.varName = name
    self.varType = type_
    Exception.__init__(self, )

  def __str__(self) -> str:
    """Return the string representation of the MissingVariable."""
    infoSpec = """Missing variable at name: '%s' of type: '%s'!"""
    name = self.varName
    clscName = self.varType.__name__
    info = infoSpec % (name, clscName)
    from ..utilities import textFmt
    return textFmt(info)

  __repr__ = __str__

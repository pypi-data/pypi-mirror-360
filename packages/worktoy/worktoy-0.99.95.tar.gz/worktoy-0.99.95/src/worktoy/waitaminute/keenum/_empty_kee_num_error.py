"""
EmptyKeeNumError is a custom exception class raised to indicate that a
KeeNum class failed to provide any enumeration members.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  pass


class EmptyKeeNumError(Exception):
  """
  EmptyKeeNumError is a custom exception class raised to indicate that a
  KeeNum class failed to provide any enumeration members.
  """

  __slots__ = ('className',)

  def __init__(self, className: str) -> None:
    """Initialize the EmptyKeeNumError object."""
    self.className = className
    Exception.__init__(self, )

  def __str__(self, ) -> str:
    """Return the string representation of the EmptyKeeNumError object."""
    infoSpec = """KeeNum class '%s' has no members!"""
    info = infoSpec % self.className
    return textFmt(info)

  __repr__ = __str__

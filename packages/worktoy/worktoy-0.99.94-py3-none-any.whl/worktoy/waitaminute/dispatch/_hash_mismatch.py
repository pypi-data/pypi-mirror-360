"""HashMismatch is raised by the dispatcher system to indicate a hash
based mismatch between a type signature and a tuple of arguments. """
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from worktoy.static import TypeSig


class HashMismatch(Exception):
  """HashMismatch is raised by the dispatcher system to indicate a hash
  based mismatch between a type signature and a tuple of arguments. """

  __slots__ = ('typeSig', 'posArgs')

  def __init__(self, typeSig_: TypeSig, *args) -> None:
    """HashMismatch is raised by the dispatcher system to indicate a hash
    based mismatch between a type signature and a tuple of arguments. """
    self.typeSig = typeSig_
    self.posArgs = args

    Exception.__init__(self, )

  def __str__(self) -> str:
    """Get the string representation of the HashMismatch."""
    sigStr = str(self.typeSig)
    argTypes = [type(arg).__name__ for arg in self.posArgs]
    argStr = """(%s)""" % ', '.join(argTypes)
    sigHash = hash(self.typeSig)
    try:
      argHash = hash(self.posArgs)
    except TypeError:
      argHash = '<unhashable>'

    infoSpec = """Unable to match type signature: <br><tab>%s<br>with
    signature of arguments:<br><tab>%s<br>Received hashes: %d != %s"""
    info = infoSpec % (sigStr, argStr, sigHash, argHash)
    return textFmt(info)

  __repr__ = __str__

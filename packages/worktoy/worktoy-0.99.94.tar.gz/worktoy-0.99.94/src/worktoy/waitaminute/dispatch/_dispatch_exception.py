"""DispatchException provides a custom exception raised when an instance
of OverloadDispatcher fails to resolve the correct function from the
given arguments. Because the overload protocol relies on type matching,
this exception subclasses TypeError such that it can be caught by external
error handlers. """
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...utilities import textFmt

if TYPE_CHECKING:  # pragma: no cover
  from worktoy.static import Dispatch


class DispatchException(TypeError):
  """DispatchException provides a custom exception raised when an instance
  of OverloadDispatcher fails to resolve the correct function from the
  given arguments. Because the overload protocol relies on type matching,
  this exception subclasses TypeError such that it can be caught by external
  error handlers. """

  __slots__ = ('dispatchObject', 'receivedArguments')

  def __init__(self, dispatch: Dispatch, *args) -> None:
    self.dispatchObject = dispatch
    self.receivedArguments = args
    TypeError.__init__(self, )

  def __str__(self) -> str:
    """
    Return a string representation of the DispatchException.
    """
    ownerName = self.dispatchObject.getFieldOwner().__name__
    fieldName = self.dispatchObject.getFieldName()
    clsName = type(self.dispatchObject).__name__
    header = '%s object at %s.%s' % (clsName, ownerName, fieldName)
    typeArgs = [type(arg).__name__ for arg in self.receivedArguments]
    argStr = '%s' % ', '.join(typeArgs)
    typeSigs = self.dispatchObject.getTypeSigs()
    typeSigStr = [str(sig) for sig in typeSigs]
    sigStr = '<br><tab>'.join(typeSigStr)

    infoSpec = """%s received arguments with signature: <br><tab>%s
    <br>which does not match any of the expected signatures:<br><tab>%s"""
    return textFmt(infoSpec % (header, argStr, sigStr))

  __repr__ = __str__

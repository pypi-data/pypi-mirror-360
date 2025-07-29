"""Function objects decorated with the @overload decorator may have same
name but different signatures. The overload decorator is used to"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import TypeSig

if TYPE_CHECKING:  # pragma: no cover
  from typing import Callable


def overload(*types: object, **kwargs: object) -> Callable:
  """Function objects decorated with the @overload decorator may have same
  name but different signatures. The overload decorator is used to
  create a function object that can be called with different argument
  types. """

  typeSig = TypeSig(*types)

  def hereIsMyNumber(callMeMaybe: Callable) -> Callable:
    """Here is my number"""
    existing = getattr(callMeMaybe, '__type_sigs__', ())
    setattr(callMeMaybe, '__type_sigs__', (*[*existing, typeSig],))
    setattr(callMeMaybe, '__is_overloaded__', True)

    return callMeMaybe

  return hereIsMyNumber

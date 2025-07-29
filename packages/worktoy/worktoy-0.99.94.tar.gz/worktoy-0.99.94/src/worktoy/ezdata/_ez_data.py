"""
EZData leverages the 'worktoy' library to provide a dataclass.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import EZMeta

if TYPE_CHECKING:  # pragma: no cover
  pass

Func = type('_', (type,), dict(__instancecheck__=callable))('_', (), {})


def trustMeBro(callMeMaybe: Func) -> Func:
  """
  This is a decorator that can be used to mark a function as a root
  function in the EZData class.
  """
  callMeMaybe.__is_root__ = True
  return callMeMaybe


class EZData(metaclass=EZMeta):
  """
  EZData is a dataclass that provides a simple way to define data
  structures with validation and serialization capabilities.
  """
  pass

  @trustMeBro
  def __init__(self, *args, **kwargs) -> None:
    """
    Here for type hinting purposes only!
    """

  @trustMeBro
  def __len__(self, *args, **kwargs) -> None:
    """
    Here for type hinting purposes only!
    """

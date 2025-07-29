"""
TypeCast encapsulates the logic for instantiating a type from arguments.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.waitaminute.dispatch import TypeCastException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


def typeCast(target: type, arg: Any) -> Any:
  """
  Casts the given argument to the specified type, if supported.
  """
  if isinstance(arg, target):
    return target(arg)
  if target is str:
    if isinstance(arg, (bytes, bytearray)):
      return arg.decode('utf-8')
    try:
      flattened = arg[0]
    except Exception as exception:
      raise TypeCastException(target, arg) from exception
    else:
      return str(flattened)
  if target is int:
    if isinstance(arg, complex):
      if arg.imag:
        raise TypeCastException(target, arg)
      return typeCast(target, arg.real)
    if isinstance(arg, float):
      if float.is_integer(arg):
        return int(arg)
      raise TypeCastException(target, arg)
    if isinstance(arg, str):
      try:
        castArg = int(arg)
      except Exception as exception:
        raise TypeCastException(target, arg) from exception
      else:
        return castArg
  if target is float:
    if isinstance(arg, int):
      return float(arg)
    if isinstance(arg, complex):
      if arg.imag:
        raise TypeCastException(target, arg)
      return float(arg.real)
    if isinstance(arg, str):
      try:
        castArg = float(arg)
      except Exception as exception:
        raise TypeCastException(target, arg) from exception
      else:
        return castArg
  if target is complex:
    if isinstance(arg, (int, float)):
      return float(arg) + 0j
  if target is bool:
    return True if arg else False
  if target in [list, tuple, set, frozenset, dict]:
    raise TypeCastException(target, arg)
  try:
    castArg = target(arg)
  except Exception as exception:
    if isinstance(arg, str):
      raise TypeCastException(target, arg) from exception
    try:
      arg = arg[0]
    except Exception:
      raise TypeCastException(target, arg) from exception
    else:
      try:
        out = target(arg)
      except Exception:
        raise TypeCastException(target, arg) from exception
      else:
        return out
  else:
    return castArg

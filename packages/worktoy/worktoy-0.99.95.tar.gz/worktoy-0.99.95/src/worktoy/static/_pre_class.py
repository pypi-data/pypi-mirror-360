"""
PreClass provides a stateful class containing the name and hash of a class
about to be created.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..waitaminute import MissingVariable, TypeException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class PreClass(type):
  """PreClass provides a stateful class containing the name and hash of a
  class about to be created."""

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Fallback variables
  __private_fallback__ = '__pre_class__'

  #  Private variables
  __meta_class__ = None
  __hash_value__ = None

  #  Public variables

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __new__(mcls, *args, **kwargs) -> type:
    """
    PreClass instances are basically treated as classes, thus 'type' is
    a reasonable base.
    """
    _name, _hash, bases, _meta = None, None, [], None
    for arg in args:
      if isinstance(arg, str):
        _name = arg
        continue
      if isinstance(arg, int):
        _hash = arg
        continue
      if isinstance(arg, type):
        _meta = arg
        continue
      if isinstance(arg, (tuple, list)):
        bases = (*arg,)
        continue
      raise TypeException('arg', arg, str, int, type, tuple, list)

    cls = type.__new__(mcls, _name, (*bases,), {})
    setattr(cls, '__hash_value__', _hash)
    setattr(cls, '__meta_class__', _meta)
    return cls

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __instancecheck__(cls, instance: Any) -> bool:
    """
    Checks if the instance is an instance of the PreClass.
    """
    return True if hash(cls) == hash(instance) else False

  def __hash__(cls, ) -> int:
    """
    Returns the explicitly set hash value of the PreClass object.
    """
    if cls.__hash_value__ is None:
      raise MissingVariable('__hash_value__', int)
    if isinstance(cls.__hash_value__, int):
      return cls.__hash_value__
    name, value = '__hash_value__', cls.__hash_value__
    raise TypeException(name, value, int)

  def __getattribute__(cls, key: str, ) -> Any:
    """
    This reimplementation of __getattribute__ was done by a highly skilled
    professional, do not try this at home!
    """
    if key == '__class__':
      return object.__getattribute__(cls, '__meta_class__')
    return object.__getattribute__(cls, key)

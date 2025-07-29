"""
Nuthin much happenin here!
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import builtins

from worktoy.waitaminute.meta import MetaclassException

oldBuild = builtins.__build_class__


def _resolveMetaclass(func, name, *args, **kwargs) -> type:
  """
  Finds the metaclass in the given arguments.
  """
  mcls = type
  if 'metaclass' in kwargs:
    mcls = kwargs['metaclass']
  elif args:
    mcls = type(args[0])
  return mcls


def _resolveBases(func, name, *args, **kwargs) -> tuple[type, ...]:
  """
  Finds the bases in the given arguments.
  """
  return args


class _InitSub(object):
  """
  A chill object that does not raise any:
  'TypeError: Some.__init_subclass__() takes no keyword arguments'
  """

  def __init__(self, *args, **kwargs) -> None:
    """
    Why are we still here?
    """
    object.__init__(self)

  def __init_subclass__(cls, **kwargs) -> None:
    """
    Just to suffer?
    """
    object.__init_subclass__()


def newBuild(func, name, *args, **kwargs):
  """A new build function that does nothing."""
  mcls = _resolveMetaclass(func, name, *args, **kwargs)
  bases = _resolveBases(func, name, *args, **kwargs)
  try:
    cls = oldBuild(func, name, *args, **kwargs)
  except TypeError as typeError:
    if '__init_subclass__() takes no keyword arguments' in str(typeError):
      return newBuild(func, name, _InitSub, *args, **kwargs)
    if 'metaclass conflict' in str(typeError):
      raise MetaclassException(mcls, name, *bases)
    raise typeError
  else:
    return cls
  finally:
    pass


builtins.__build_class__ = newBuild

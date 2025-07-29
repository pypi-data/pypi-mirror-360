"""
LOCKED provides a sentinel object to indicate that an attribute may not be
retrieved in the current state of the object. Similar to 'DELETED',
but raises a 'RuntimeError', or subclass thereof, on access attempts.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import Sentinel


class LOCKED(Sentinel):
  """
  LOCKED is a sentinel object that indicates an attribute is locked and
  cannot be accessed in the current state of the object.
  """
  pass

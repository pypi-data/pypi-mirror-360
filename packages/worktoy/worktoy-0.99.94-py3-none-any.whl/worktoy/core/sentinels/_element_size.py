"""
ELEMENTSIZE provides a sentinel used by the AbstractTensor class to indicate
the location of the element size in bytes.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Sentinel

if TYPE_CHECKING:  # pragma: no cover
  pass


class ELEMENTSIZE(Sentinel):
  """
  ELEMENTSIZE provides a sentinel used by the AbstractTensor class to
  indicate the location of the element size in bytes.
  """

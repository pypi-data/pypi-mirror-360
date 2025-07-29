"""FlexMismatch is a custom exception indicating failure to flexible cast
positional arguments to a TypeSig object."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from . import CastMismatch


class FlexMismatch(CastMismatch):
  """
  FlexMismatch is a custom exception indicating failure to flexible cast
  positional arguments to a TypeSig object.
  """
  pass

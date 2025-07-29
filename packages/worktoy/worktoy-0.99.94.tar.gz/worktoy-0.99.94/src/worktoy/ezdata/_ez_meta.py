"""EZMeta provides the metaclass for the EZData class."""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..mcls import AbstractMetaclass, Base
from ..ezdata import EZSpace

if TYPE_CHECKING:  # pragma: no cover
  pass


class EZMeta(AbstractMetaclass):
  """EZMeta provides the metaclass for the EZData class."""

  @classmethod
  def __prepare__(mcls, name: str, bases: Base, **kwargs: dict) -> EZSpace:
    """Prepare the class namespace."""
    return EZSpace(mcls, name, bases, **kwargs)

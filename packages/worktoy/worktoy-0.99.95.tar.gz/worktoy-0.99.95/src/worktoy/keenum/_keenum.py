"""
The metaclass 'KeeMeta' automatically creates the KeeNum class for which
the class here is a placeholder of sorts.

"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import KeeMeta

if TYPE_CHECKING:  # pragma: no cover
  from typing import Iterator, Any


  class Member:
    """
    Is that enough, pycharm?
    """

    name: str
    value: Any


  class KeeNum(dict):
    """
    This is just so pycharm will chill out with warnings about KeeNum
    """

    name: str
    value: Any

    def __init__(self, *args, **kwargs) -> None:
      """KeeNum is a placeholder for the KeeMeta metaclass."""

    def __iter__(self) -> Iterator:
      pass

    def __getitem__(self, item) -> Member:
      pass

    def __setitem__(self, key, value) -> None:
      pass
else:
  KeeNum = KeeMeta.getCoreKeeNum()

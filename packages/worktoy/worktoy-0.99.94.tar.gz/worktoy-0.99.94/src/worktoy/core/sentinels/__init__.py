"""
Sentinels represent special situations. The sentinel itself provides no
information about its meaning or function. It is merely a stateless unique
object equal only to itself.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._sentinel import Sentinel
from ._deleted import DELETED
from ._owner import OWNER
from ._this import THIS
from ._desc import DESC
from ._locked import LOCKED
from ._element_size import ELEMENTSIZE

__all__ = [
    'Sentinel',
    'DELETED',
    'OWNER',
    'THIS',
    'DESC',
    'LOCKED',
    'ELEMENTSIZE',
]

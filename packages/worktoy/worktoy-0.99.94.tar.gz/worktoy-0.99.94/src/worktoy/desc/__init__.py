"""
The 'worktoy.desc' module provides the base descriptor classes. This
module introduces a novel concept: descriptor-context.

When a descriptor is accessed through the owning class, the descriptor
object itself returns. When through an instance, the descriptor usually
performs the relevant accessor function as appropriate for the instance
received. This module expands this concept by introducing the
descriptor-context.

Methods decorated with the '@WITH' decorator require an active context.
These methods should have the following signature:

@WITH
def foo(self, instance: Any, owner: Type[type], **kwargs) -> Any:
...

Descriptor classes that are not stateless, must reimplement the
'exitContext' such that it restores the descriptor instance to its
previous state. Stateless descriptor classes need not reimplement the
method inherited from the 'Object' class.



"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from ._alias import Alias
from ._field import Field
from ._attri_box import AttriBox

__all__ = [
    'Alias',
    'Field',
    'AttriBox',
]

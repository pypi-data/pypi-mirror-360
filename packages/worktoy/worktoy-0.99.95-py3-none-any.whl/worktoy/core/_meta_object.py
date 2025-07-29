"""
MetaObject provides the metaclass for the 'Object' class in the
'worktoy.core' package. It derives from MetaType, allowing subclasses of
derived classes to use other metaclass derived from MetaType.

Please note the difference between a metaclass and a baseclass. To
distinguish, this library proposes the following terminology:

 - A class 'derives from' the metaclass creating it. Ultimately,
 all derives from 'type', possibly with more metaclasses in between. The
 'worktoy' library provides 'MetaType' as the initial metaclass.

 - A class 'is based on' the baseclasses from which it inherits.
 Ultimately, all classes are based on 'object', possibly with more classes
 in between. The 'worktoy' library provides 'Object' as the initial
 baseClass.

with the following nomenclature:

 - class: (Traditional definition)
 - metaclass: A class whose instances are themselves classes.
 - meta-metaclass: A class whose instances are themselves metaclasses.
 - derive: The creation of a new class from a metaclass.
 - base: The extension of a class from a baseclass.

No distinction is necessary when class definition is considered
an implementation detail across object orientated programming
languages. Instead, the computer science field has extensively studied the
relationships between classes and baseclasses. By elevating classes to
first class citizens, Python introduces a concept semantically similar to
class inheritance, but fundamentally different.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import MetaType

if TYPE_CHECKING:  # pragma: no cover
  pass


class MetaObject(MetaType, metaclass=MetaType):
  """
  MetaObject provides the metaclass for the 'Object' class in the
  'worktoy.core' package. It derives from MetaType, meaning that a
  subclass of 'Object' can still use a custom metaclass, provided that
  metaclass also derives from 'MetaType'.
  """
  pass

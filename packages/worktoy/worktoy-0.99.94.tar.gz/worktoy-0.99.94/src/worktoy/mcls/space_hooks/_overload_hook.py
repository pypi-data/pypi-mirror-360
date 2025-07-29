"""
OverloadHook hooks into the namespace system and collects the overload
decorated methods replacing them with a dispatcher that calls the
correct method based on the arguments passed to it.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...static import Dispatch
from . import AbstractSpaceHook

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class OverloadSpaceHook(AbstractSpaceHook):
  """
 OverloadHook implements method overloading in the metaclass namespace
  system. It collects all functions decorated with `@overload` and
  compiles them into a single dispatcher per function name.

  ## Purpose

  During class definition, multiple functions with the same name may be
  decorated with `@overload`, each targeting a different type signature.
  These are temporarily stored with signature metadata (`__type_sigs__`)
  and marked using the `__is_overloaded__` flag.

  The OverloadHook intercepts these assignments and stores the overloads
  in a dispatch map indexed by function name and type signature.

  ## Behavior

  - **During setItemHook**:
    Detects overloaded functions and registers them with the namespace’s
    internal overload map. This stage only collects metadata.

  - **During postCompileHook**:
    Replaces each overloaded function with a `Dispatch` object that
    selects the correct overload at runtime based on argument types.
    Injects `__dispatch_names__` into the namespace for debugging or
    reflection.

  ## Usage
  To use OverloadHook, simply declare it in your namespace class:

  class Space(AbstractNamespace):  # Must inherit from AbstractNamespace
    #  Custom namespace class inheriting from AbstractNamespace
    overloadHook = OverloadHook()  # Register the hook
    preClassHook = PreClassHook()  # Register the pre-class hook

  ## Example

  The following example shows a ComplexNumber class supporting three
  constructor overloads. It uses the BaseMeta metaclass, which provides
  a namespace equipped with OverloadHook and PreClassHook for
  signature resolution and THIS substitution.

  Real and imaginary parts are declared using AttriBox, which provides
  lazy, type-enforced attribute slots. See the documentation for
  worktoy.mcls.BaseMeta and worktoy.attr.AttriBox for details.

  ___________________________________________________________________________
  ```python```
  from typing import Self

  from worktoy.mcls import BaseMeta
  from worktoy.attr import AttriBox
  from worktoy.static import overload
  from worktoy.static.zeroton import THIS

  class ComplexNumber(metaclass=BaseMeta):
    #  Custom metaclass with overload support
    #  Properties:
    REAL = AttriBox[float](0.0)
    IMAG = AttriBox[float](0.0)

    @overload(float, float)
    def __init__(self, real: float, imag: float) -> None:
      #  Initialize a complex number with real and imaginary parts.

      self.REAL = real
      self.IMAG = imag

    @overload(complex)
    def __init__(self, z: complex) -> None:
      self.__init__(z.real, z.imag)

    @overload(THIS)  # THIS is a placeholder for ComplexNumber itself
    def __init__(self, other: Self) -> None:
      self.__init__(other.REAL, other.IMAG)
  ¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
  After class creation, ComplexNumber.__init__ becomes a dispatcher
  object rather than any of the individual function definitions above.
  When the constructor is called, it matches the argument types against
  the registered signatures and invokes the correct implementation.

  This setup supports expressive, type-driven APIs while preserving
  clean class definitions — all enabled via hook-based metaclass
  composition.
  """

  def setItemPhase(self, key: str, value: Any, old: Any, ) -> bool:
    """
    Set the item hook for the namespace system. This method is called
    when an item is set in the namespace system. It collects the
    overload decorated methods and replaces them with a dispatcher that
    calls the correct method based on the arguments passed to it.
    """
    if getattr(value, '__is_overloaded__', None) is None:
      return False
    typeSigs = getattr(value, '__type_sigs__', None)
    for sig in typeSigs:
      self.space.addOverload(key, sig, value)
    return True

  def postCompilePhase(self, compiledSpace: dict) -> dict:
    """
    Post compile hook for the namespace system. This method is called
    after the namespace system is compiled. It collects the overload
    decorated methods and replaces them with a dispatcher that calls the
    correct method based on the arguments passed to it.
    """
    overloadMap = self.space.getOverloadMap()  # str: dict[TypeSig, Func]
    dispatchNames = []
    for key, sigMap in overloadMap.items():
      compiledSpace[key] = Dispatch(sigMap)
      dispatchNames.append(key)
    compiledSpace['__dispatch_names__'] = dispatchNames
    return compiledSpace

"""
'PreClassHook' replaces 'THIS' in the AbstractNamespace with 'PreClass'
objects having the hash and name of the future class ahead of class creation.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ...static import PreClass, TypeSig
from ...waitaminute import TypeException
from . import AbstractSpaceHook

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class PreClassSpaceHook(AbstractSpaceHook):
  """
  PreClassHook resolves the circular reference problem caused when a
  decorator or hook needs to refer to the class under construction —
  *before* that class exists.

  ## Purpose

  During class construction, decorators (such as those involved in
  overload resolution) may need to reference the class currently being
  defined. But this isn't possible with a literal reference, since the
  class object doesn’t exist yet.

  To solve this, a sentinel object named `THIS` is used as a placeholder.
  The PreClassHook intercepts assignments in the namespace and replaces
  any references to `THIS` found in function type signatures with a
  special `PreClass` proxy.

  The `PreClass` object mimics the identity of the future class:
  - It has the same `__hash__` as the future class will
  - It stores the intended class name and metaclass
  - It can be used in hash-based fast dispatch without knowing the class

  ## Behavior

  - **During setItemHook**:
    If a function assigned to the namespace contains one or more
    `TypeSig` objects (e.g. for overloads), each is scanned for
    references to `THIS`. These are replaced in-place with the
    appropriate `PreClass` object.

  - **During postCompileHook**:
    After the class body has executed, the overload map is scanned for
    type signatures that refer to known base classes. For each such
    signature, a new equivalent signature is created where the base class
    is replaced with the `PreClass` object. This allows overloads in
    parent classes referencing `THIS` to resolve correctly in subclasses.

  ## Usage

  This hook is registered inside a namespace like so:

      class MyNamespace(AbstractNamespace):
        preClassHook = PreClassHook()

  It cooperates with the OverloadHook to ensure that decorators using
  `THIS` for self-type references work reliably across complex inheritance
  hierarchies.

  ## Notes

  - The PreClass object is cached internally and created on demand.
  - It is only instantiated once per class construction.
  - It is safe to hash and compare, but is not a fully functional class.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private variables
  __pre_class__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _createPreClass(self, **kwargs) -> None:
    """
    Creates the unique 'PreClass' object for the namespace instance owning
    this hook instance.
    """
    _hash = self.space.getHash()
    _name = self.space.getClassName()
    _meta = self.space.getMetaclass()
    self.__pre_class__ = PreClass(_hash, _name, _meta)

  def _getPreClass(self, **kwargs) -> PreClass:
    """
    Getter-function for the 'PreClass' for the namespace instance owning
    this hook instance.
    """
    if self.__pre_class__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError  # pragma: no cover
      self._createPreClass()
      return self._getPreClass(_recursion=True)
    if isinstance(self.__pre_class__, PreClass):
      return self.__pre_class__
    raise TypeException('__pre_class__', self.__pre_class__, PreClass, )

  def setItemPhase(self, key: str, val: Any, old: Any, ) -> bool:
    """
    If key contains reference the class under construction by containing
    'THIS', replace with 'PreClass' object providing the hash and name of the
    future class.
    """
    preClass = self._getPreClass()
    typeSigs = getattr(val, '__type_sigs__', None)
    if typeSigs is None:
      return False
    for sig in typeSigs:
      if isinstance(sig, TypeSig):
        TypeSig.replaceTHIS(sig, preClass, )
        _ = hash(sig)
        continue
      raise TypeException('sig', sig, TypeSig, )
    else:
      return False

  def postCompilePhase(self, compiledSpace) -> dict:
    """
    Where a type signature in the overload map includes a base class,
    we create a new type signature pointing to the same function, but with
    the 'PreClass' object replacing the base class. This will allow 'THIS'
    defined in an overload in a parent to work in the child class with
    either an instance of the parent or the child.
    """
    overloadMap = self.space.getOverloadMap()  # str: dict[TypeSig, Func]
    preClass = self._getPreClass()
    bases = self.space.getBases()
    newLoadMap = dict()
    for key, sigMap in overloadMap.items():
      moreSigMap = dict()
      for sig, func in sigMap.items():
        newSig = []
        for type_ in sig:
          if type_ in bases:
            newSig.append(preClass)
            continue
          newSig.append(type_)
        else:
          if preClass in newSig:
            newTypeSig = TypeSig(*newSig)
            moreSigMap[newTypeSig] = func
          moreSigMap[sig] = func
      else:
        newLoadMap[key] = moreSigMap
    else:
      self.space.__overload_map__ = newLoadMap
    return compiledSpace

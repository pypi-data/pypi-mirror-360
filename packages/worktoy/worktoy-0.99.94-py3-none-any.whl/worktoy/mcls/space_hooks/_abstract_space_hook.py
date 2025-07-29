"""
AbstractSpaceHook provides an abstract baseclass for hooks used by the
namespaces in the metaclass system.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import SpaceDesc
from ...core import Object

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Callable, TypeAlias, Type
  from worktoy.mcls import AbstractNamespace as ASpace

  AccessorHook = Callable[[ASpace, str, Any], Any]
  CompileHook = Callable[[ASpace, dict], dict]
  Space: TypeAlias = Type[ASpace]
  Meta: TypeAlias = Type[type]


class AbstractSpaceHook(Object):
  """
  AbstractSpaceHook is the abstract base class for defining hook objects
  used in conjunction with AbstractNamespace. These hooks enable modular,
  stage-specific interception during class body evaluation and namespace
  compilation within the metaclass system.

  ## Purpose

  Hooks allow custom behavior to be injected into the class construction
  pipeline without modifying the namespace or metaclass core logic. They
  are used to observe and/or alter how names are accessed, assigned, or
  compiled into the final class definition.

  ## Integration

  To activate a hook, simply instantiate a subclass of AbstractSpaceHook
  inside the body of a namespace class (i.e., a subclass of
  AbstractNamespace). The descriptor protocol (`__set_name__`) ensures the
  hook registers itself with the namespace automatically at definition time.

  Example:

      class MyNamespace(AbstractNamespace):
        overloadHook = OverloadPhase()
        validationHook = ReservedNamePhase()

  ## Lifecycle Hook Methods

  Subclasses may override any of the following methods to participate in
  different stages of the namespace lifecycle. All are optional.

  - `setItemPhase(self, key, value, oldValue) -> bool`
    Called just before a name is set in the namespace.
    Returning True blocks the default behavior.

  - `getItemPhase(self, key, value) -> bool`
    Called just before a name is retrieved from the namespace.
    Returning True blocks the default behavior.

  - `preCompilePhase(self, compiled: dict) -> dict`
    Called after the class body finishes executing, but before the
    namespace is finalized. May transform or replace namespace contents.

  - `postCompilePhase(self, compiled: dict) -> dict`
    Called immediately before the finalized namespace is handed off to the
    metaclass. Can be used for final transformations or validation.

  ## Descriptor Behavior

  AbstractSpaceHook implements the descriptor protocol. When accessed via a
  namespace class, it is bound with the following attributes:

  - `self.space` refers to the active namespace instance.
  - `self.spaceClass` refers to the namespace class itself.

  These attributes can be used to introspect the environment the hook is
  participating in.

  ## Extension Notes

  Subclasses are expected to override only the relevant hook methods.
  If none are overridden, the hook has no effect.

  The `addPhase()` method of the namespace class is automatically invoked
  during registration. Hook authors do not need to call it manually.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private variables
  __space_object__ = None  # The owning namespace instance

  #  Public variables
  space = SpaceDesc()  # The namespace instance this hook is bound to

  #  TYPE_CHECKING
  if TYPE_CHECKING:  # pragma: no cover
    from . import AbstractSpaceHook
    from .. import AbstractNamespace
    assert isinstance(AbstractSpaceHook.space, AbstractNamespace)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  def getItemPhase(self, key: str, value: Any, ) -> bool:
    """Hook for getItem. This is called before the __getitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False. """

  def setItemPhase(self, key: str, value: Any, oldValue: Any, ) -> bool:
    """Hook for setItem. This is called before the __setitem__ method of
    the namespace object is called. The default implementation does nothing
    and returns False. """

  def preCompilePhase(self, compiledSpace: dict) -> dict:
    """Hook for preCompile. This is called before the __init__ method of
    the namespace object is called. The default implementation does nothing
    and returns the contents unchanged. """
    return compiledSpace

  def postCompilePhase(self, compiledSpace: dict) -> dict:
    """Hook for postCompile. This is called after the __init__ method of
    the namespace object is called. The default implementation does nothing
    and returns the contents unchanged. """
    return compiledSpace

  def newClassPhase(self, cls: Meta, ) -> Meta:
    """
    Final phase invoked by the metaclass after it has created the new
    class object, but before returning it. This phase occurs before the
    normal post class creation flow continues.
    """
    return cls

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __set_name__(self, owner: Space, name: str, **kwargs) -> None:
    """
    After the super call, adds one self to the namespace class as a hook
    class.
    """
    super().__set_name__(owner, name, )
    owner.addHook(self)

  def __get__(self, instance: ASpace, owner: Space, **kwargs) -> Any:
    """
    Descriptor protocol method. Returns the bound hook instance with
    `space` and `spaceClass` attributes set to the current namespace
    instance and its class.
    """
    self.__space_object__ = instance
    return self

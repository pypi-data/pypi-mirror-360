"""
The Dispatch class dispatches a function call to the appropriate
function based on the type of the first argument.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from types import FunctionType as Func
from typing import TYPE_CHECKING

from ..core import Object
from ..static import TypeSig
from ..utilities import textFmt
from ..waitaminute import attributeErrorFactory
from ..waitaminute.dispatch import HashMismatch, CastMismatch, FlexMismatch
from ..waitaminute.dispatch import DispatchException

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Callable, TypeAlias, Type

  Types: TypeAlias = tuple[type, ...]
  Hashes: TypeAlias = list[int]
  HashMap: TypeAlias = dict[int, Callable]
  TypesMap: TypeAlias = dict[Types, Callable]
  CastMap: TypeAlias = dict[Types, Callable]
  CallMap: TypeAlias = dict[TypeSig, Callable]


class Dispatch(Object):
  """
Dispatch replaces the usual bound method when overloaded function
objects are used. The Dispatch instance serves as a dynamic method
selector, attached to a class attribute in place of the original
function object.

Dispatch achieves this by subclassing Object, which provides
a full implementation of the descriptor protocol, including
__get__, __set__, and __delete__. This allows Dispatch to operate as
a descriptor that controls method binding and function dispatching.

When called, Dispatch attempts to match the provided arguments to one
of its registered TypeSig signatures. It proceeds in the following stages:

1. Fast dispatch:
   The most performant stage. Arguments must match the expected types
   exactly — even an int will not match a float. If an exact match is
   found, Dispatch immediately invokes the corresponding function.

2. Cast dispatch:
   If fast dispatch fails, Dispatch attempts to cast arguments to the
   required types, proceeding only if all casts succeed.

3. Flex dispatch:
   If casting also fails, Dispatch performs flexible matching. It may
   reorder arguments and unpack iterables as needed to satisfy the
   signature.

Classes derived from BaseMeta can decorate methods with @overload([TYPES])
to indicate that the decorated object should be dispatched when receiving
arguments matching the given types. The custom metaclass control flow then
instantiates Dispatch during class creation.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Class variables
  __latest_dispatch__ = None  # The latest dispatch that was made
  __overload_dispatcher__ = True  # Required flag for all dispatchers!

  #  Private variables
  __call_map__ = None

  # #  Public variables
  # __name__ = Field()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def getTypeSigs(self) -> list[TypeSig]:
    """Getter-function for the type signatures supported. """
    return [*self.__call_map__.keys(), ]

  @classmethod
  def getLatestDispatch(cls) -> Func:
    """Getter-function for the most recently successful dispatch. """
    return cls.__latest_dispatch__.__func__

  # @__name__.GET
  # def _getName(self, ) -> str:
  #   """Get the name of the function. """
  #   return self.getFieldName()

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  SETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @classmethod
  def _resetLatestDispatch(cls) -> None:
    """
    Reset the latest dispatch to None.
    """
    cls.__latest_dispatch__ = None

  @classmethod
  def _setLatestDispatch(cls, dispatch: Callable) -> None:
    """
    Set the latest dispatch to the given dispatch.
    """
    cls.__latest_dispatch__ = dispatch

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, callMap: CallMap) -> None:
    self.__call_map__ = callMap

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  Python API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __set_name__(self, owner: Type[Object], name: str, **kwargs) -> None:
    """
    When the owning class is created, Python calls this method to allowing
    the type signatures to be updated with the owner class. This is
    necessary as the type signatures are able to reference the owning
    class before it is created by using the 'THIS' token object in place
    of it.
    """
    Object.__set_name__(self, owner, name, )
    for sig, call in self.__call_map__.items():
      TypeSig.replaceTHIS(sig, owner)

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def _fastDispatch(self, ins: Any, *args, **kwargs) -> Any:
    """
    Fast dispatch the function call.
    """
    exceptions = []
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.fast(*args)
      except HashMismatch as hashMismatch:
        exceptions.append(hashMismatch)
        continue
      else:
        return call(ins, *posArgs, **kwargs)
    else:
      raise [RuntimeError, *exceptions][-1]

  def _castDispatch(self, ins: Any, *args, **kwargs) -> Any:
    """
    Dispatches the function call with arguments cast to the expected
    types.
    """
    exceptions = []
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.cast(*args)
      except CastMismatch as castMismatch:
        exceptions.append(castMismatch)
        continue
      else:
        return call(ins, *posArgs, **kwargs)
    else:
      raise [RuntimeError, *exceptions][-1]

  def _flexDispatch(self, ins: Any, *args, **kwargs) -> Any:
    """
    The most flexible attempt to dispatch the function call.
    """
    exceptions = []
    for sig, call in self.__call_map__.items():
      try:
        posArgs = sig.flex(*args)
      except Exception as exception:
        exceptions.append(exception)
        continue
      else:
        return call(ins, *posArgs, **kwargs)
    else:
      raise [RuntimeError, *exceptions][-1]

  def _dispatch(self, ins: Any, *args: Any, **kwargs: Any) -> Any:
    """
    Dispatches the function call by trying fast, cast and flex in that
    order.
    """
    self._setLatestDispatch(self._fastDispatch)
    exceptions = []
    try:
      out = self._fastDispatch(ins, *args, **kwargs)
    except HashMismatch as hashMismatch:
      exceptions.append(hashMismatch)
    else:
      return out
    try:
      out = self._castDispatch(ins, *args, **kwargs)
    except CastMismatch as castMismatch:
      exceptions.append(castMismatch)
    else:
      self._setLatestDispatch(self._castDispatch)
      return out
    try:
      out = self._flexDispatch(ins, *args, **kwargs)
    except FlexMismatch as flexMismatch:
      exceptions.append(flexMismatch)
    else:
      self._setLatestDispatch(self._flexDispatch)
      return out
    self._resetLatestDispatch()
    raise DispatchException(self, ins, *args, )

  def __str__(self, ) -> str:
    """Get the string representation of the function."""
    sigStr = [str(sig) for sig in self.getTypeSigs()]
    info = """%s object supporting type signatures: \n%s"""
    sigLines = '<br><tab>'.join(sigStr)
    return textFmt(info % (self.__field_name__, sigLines))

  __repr__ = __str__

  def __get__(self, instance: Any, owner: Type[Object]) -> Any:
    """
    Returns the Dispatch instance for the given instance.
    """
    if instance is None:
      return self

    def wrapped(*args: Any, **kwargs: Any) -> Any:
      """
      Wraps the call to the dispatch method with the instance as the
      first argument.
      """

      return self._dispatch(instance, *args, **kwargs)

    return wrapped

  def __getattr__(self, key: str, ) -> Any:
    fieldName = self.getFieldName()
    ownerName = self.getFieldOwner().__name__
    if key == '__name__':
      return fieldName
    if key == '__qualname__':
      return '%s.%s' % (ownerName, fieldName)
    attributeError = attributeErrorFactory(ownerName, fieldName, )
    raise attributeError

"""
TypeSig encapsulates type signatures and recognizes positional arguments
that match it.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from worktoy.waitaminute.dispatch import HashMismatch, TypeCastException
from worktoy.waitaminute.dispatch import CastMismatch, FlexMismatch
from worktoy.waitaminute import UnpackException
from worktoy.core.sentinels import THIS
from worktoy.utilities import unpack, bipartiteMatching
from . import PreClass, typeCast

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any, Iterator


class TypeSig:
  """
  #  DESCRIPTION
  'TypeSig' describes the types of an array of positional arguments
  analogous to how the 'type' function describes the 'type' of a single
  argument. The class supports both explicit types and the 'THIS'
  placeholder sentinel.

  #  NOMENCLATURE

  - 'Call arguments':  A tuple of objects. For example, the arguments
  received by a callable object.
  - 'type parsing':  The process by which the 'TypeSig' object determines
  how it best matches call arguments. If possible, the 'TypeSig' object
  will return a tuple of objects matching it. If not possible, a custom
  exception is raised. More details provided below.
  - 'type parser':  The 'TypeSig' instance method performing the 'type
  parsing'. The method receives 'call arguments' and returns 'processed
  arguments' (described below) or raises a custom exception specific to
  itself.
  - 'Processed arguments':  A tuple of objects returned by the 'TypeSig'
  object after parsing.
  - 'type casting':  same as 'type parsing' but emphasizes changes applied
  changing call arguments to processed arguments.

  #  USAGE
  #  #  Type Guarding and Casting
  A function requiring a very specific type signature, might use an
  instance of 'TypeSig' to type parse and possibly cast received arguments
  to match the required types. This allows the function more flexibility
  in what arguments it accepts while retaining the initial type
  specificity. Additionally, unsupported types are caught immediately and
  explicitly allowing for explicit and precise error handling.

  #  #  Hashable
  Since 'TypeSig' objects are hashable(*) they may be used as keys in
  'dict' objects. This facilitates dispatching of function calls to a type
  appropriate overload.

  #  IMPLEMENTATION DETAILS
  'TypeSig' provides multiple 'type parser' methods as listed below:

  - 'fast':  Strict, but fast hash-based parsing. This method will always
  return processed arguments identical to received call arguments when
  hashes match. Otherwise, it raises 'HashMismatch'.

  - 'cast'(**):  Applies type casting to each call argument not exactly
  matching the corresponding type. If any argument fails to cast,
  it raises 'CastMismatch' (a subclass of 'HashMismatch'). Otherwise,
  the type-casted arguments are passed to the 'fast' method described
  above to ensure type exactness. Please note that both this and 'flex'
  described below, are not appropriate for performance-sensitive
  applications, requiring substantial overhead compared to 'fast'.

  - 'flex'(**):  This method attempts to find a permutation of the call
  arguments that it might be able to cast. Additionally, if none of its
  raw types are 'list' or 'tuple', it will unpack any iterable call
  argument. If at all possible, the processed arguments will pass through
  the 'fast' method described above. Otherwise, it raises 'FlexMismatch' (
  a subclass of 'CastMismatch').

  (*) Note that 'TypeSig' objects are hashable only after the 'THIS'
  sentinel has been replaced with the appropriate class or a more specific
  hash-aware placeholder. 'worktoy' assigns to each class a hash value
  that depends only on names known ahead of actual class creation. This
  allows 'THIS' to be replaced with a 'PreClass' object having identical
  hash.

  (**) Note that 'TypeSig' parsing methods 'cast' and 'flex' do not
  support 'THIS', when used to overload the constructor of the class to
  which 'THIS' refers. The 'worktoy.static.Dispatch' class responsible for
  dispatching calls are meant to explicitly skip both 'cast' and 'flex'
  for this case. Since the 'TypeSig' object has no awareness of the
  broader context, it cannot detect and prevent this case. The 'cast' and
  'flex' methods will raise 'SignatureRecursion'

  #  ROLE IN LIBRARY
  The 'worktoy' library uses 'TypeSig' to provide function overloading.
  When the '@overload(...)' decorator receives types and decorates a
  function, it instantiates a 'TypeSig' object and associates the
  decorated function object with it. Please note that during class
  creation, methods created with 'def ...' begin as 'function' objects.
  They only become bound methods during the class creation process. Thus,
  any function decorator in Python is certain to receive a 'function
  object'. Even if this object later becomes a bound method.

  The 'worktoy' library leverages metaclass customization to facilitate
  function overloading. It uses the 'TypeSig' class when deciding which
  function object to dispatch. For more details, see the 'worktoy.mcls'
  documentation.

  # EXAMPLE
  from __future__ import annotations

  import sys
  from math import atan2

  def angle(*args, ) -> float:
    typeSig = TypeSig(float, float)  # Creates a float-float signature
    try:
      xp, yp = typeSig.fast(*args, )
    except HashMismatch as hashMismatch:
      pass
    else:
      if xp ** 2 + yp ** 2 > 1e-12:
        return atan2(yp, xp)
      raise ZeroDivisionError('Zero has no angle!')
    try:
      xp, yp = typeSig.cast(*args, )
    except CastMismatch as castMismatch:
      pass
    else:
      return angle(xp, yp)  # Recursive call
    try:
      xp, yp = typeSig.flex(*args, )
    except FlexMismatch as flexMismatch:
      raise
    else:
      return angle(xp, yp)  # Recursive call


  def main(*args) -> None:
    #  Main script entry point.
    try:
      res = angle(*args)
    except HashMismatch as hashMismatch:
      infoSpec = 'Unable to parse arguments: (%s), resulting in: %s'
      info = infoSpec % (str(args), hashMismatch)
      print(info)
      return 1
    except ZeroDivisionError as zeroDivisionError:
      infoSpec = 'Received origin point, resulting in: %s!'
      info = infoSpec % zeroDivisionError
      print(info)
      return 2
    except Exception as exception:
      infoSpec = 'Unexpected exception: %s'
      info = infoSpec % exception
      print(info)
      return 3
    else:
      infoSpec = 'Found angle: %.3f'
      info = infoSpec % res
      print(info)
      return 0
    finally:
      info = 'Exiting test of the TypeSig class!'
      print(info)


  if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private variables
  __raw_types__ = None
  __type_casts__ = None
  __hash_value__ = None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  CONSTRUCTORS   # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __init__(self, *types: Any) -> None:
    """Initialize the TypeSig instance."""
    self.__raw_types__ = types

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  PYTHON API   # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def __iter__(self, ) -> Iterator[type]:
    """
    Implementation of iteration
    """
    yield from (self.__raw_types__ or ())

  def __hash__(self, ) -> int:
    """Forwards the hash to the hash of the types. If the replaceTHIS
    method has not been called, this will raise RuntimeError."""
    if self.__hash_value__ is None:
      return hash(self.__raw_types__)
    return self.__hash_value__

  def __eq__(self, other: object) -> bool:
    """Check if the other object is a TypeSig and has the same types."""
    if type(self) is not type(other):
      return NotImplemented
    if TYPE_CHECKING:  # pragma: no cover
      assert isinstance(other, TypeSig)
    for selfType, otherType in zip(self.__raw_types__, other.__raw_types__):
      if selfType is not otherType:
        return False
    return True

  def __len__(self, ) -> int:
    """Get the length of the types."""
    return len(self.__raw_types__)

  def __contains__(self, type_: type) -> bool:
    """Check if the type is in the types."""
    for raw in self.__raw_types__:
      if raw is type_:
        return True
    return False

  def __str__(self, ) -> str:
    """String representation reflects the types. """
    typeStr = ', '.join([t.__name__ for t in self.__raw_types__])
    info = """%s: [%s]""" % (type(self).__name__, typeStr)
    return info

  def __repr__(self, ) -> str:
    """Code representation reflects the types. """
    typeStr = ', '.join([t.__name__ for t in self.__raw_types__])
    info = """%s(%s)""" % (type(self).__name__, typeStr)
    return info

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  def replaceTHIS(self, cls: type) -> None:
    """Replace the 'THIS' type with the class."""
    newTypes = []
    for type_ in self.__raw_types__:
      if type_ is THIS or isinstance(type_, PreClass):
        newTypes.append(cls)
        continue
      newTypes.append(type_)
    self.__raw_types__ = (*newTypes,)
    self.__hash_value__ = hash(self.__raw_types__)

  def fast(self, *args, ) -> tuple:
    """
    Hash-based type parsing. The method collects the types of the call
    arguments and compares the hash of the tuple containing them with the
    predicted hash. If hashes match, the call arguments are returned.
    Otherwise, raises 'HashMismatch'.

    This method is significantly faster than the 'cast' and 'flex'
    methods, but requires exact matching. Passing an 'int' object where a
    'float' object is expected, raises 'HashMismatch'.
    """
    if len(args) == len(self):
      if hash(self) == hash((*[type(arg) for arg in args],)):
        return (*args,)
    raise HashMismatch(self, *args)

  def cast(self, *args, **kwargs) -> tuple:
    """
    Iterates over the call arguments and the expected types:

    - If the argument at index 'i' is an instance of the type at 'i',
    the processed arguments will contain the argument at 'i'.
    - Otherwise, attempts to cast the argument to the type at 'i'. If
    successful, the processed arguments will contain the 'cast'
    argument at 'i'. If not, raises 'CastMismatch'.
    - If for every argument no 'CastMismatch' is raised, the
    processed arguments are returned as a tuple.
    """
    if len(args) != len(self):
      raise CastMismatch(self, *args)
    castArgs = []
    for type_, arg in zip(self.__raw_types__, args):
      if isinstance(arg, type_):
        castArgs.append(arg)
        continue
      try:
        castArg = typeCast(type_, arg)
      except TypeCastException as typeCastException:
        raise CastMismatch(self, *args) from typeCastException
      else:
        castArgs.append(castArg)
    else:
      return (*castArgs,)

  def flex(self, *args, **kwargs) -> tuple:
    """
    Attempts reordering of the call arguments to find a permutation
    that matches the types in the 'TypeSig'. If no permutation is found,
    raises 'FlexMismatch'. If a permutation is found, the processed
    arguments are returned as a tuple.
    """
    _ = hash(self)  # Ensure hash is set or raise RuntimeError immediately
    try:
      posArgs = unpack(*args, strict=True, shallow=True)
    except UnpackException as unpackException:
      pass
    else:
      return (*self.cast(*posArgs, **kwargs),)
    candidateMap = dict()
    candidateList = []
    for type_ in self:
      candidates = []
      for i, arg in enumerate(args):
        if isinstance(arg, type_):
          candidates.append(i)
      else:
        if not candidates:
          raise FlexMismatch(self, *args)
        candidateList.append((*candidates,))
    indices = bipartiteMatching(candidateList)
    if len(indices) != len(args):
      raise FlexMismatch(self, *args)
    return (*[args[i] for i in indices],)

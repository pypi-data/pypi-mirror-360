"""
AbstractMetaclass provides the baseclass for custom metaclasses.
"""
#  AGPL-3.0 license
#  Copyright (c) 2024-2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from . import Base
from . import AbstractNamespace as ASpace
from ..core import MetaType
from ..utilities import maybe

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any
else:
  pass


class AbstractMetaclass(MetaType, metaclass=MetaType):
  """
  Abstract base for custom metaclasses that separates concerns between
  class construction and class behavior.

  This design delegates the initial class namespace to a custom object
  returned by '__prepare__', while keeping class semantics within the
  metaclass itself.

  The namespace object may define a method called 'compile()', which
  should return the finalized dictionary to be passed to 'type.__new__'.

  This separation enables:
  - Customizing how the class body is assembled without affecting the
    resulting class behavior.
  - Modifying what it means to be a class, independently of how the
    class body is constructed.

  - CUSTOM NAMESPACE COMPILATION -

  This module also provides an 'AbstractNamespace' class intended to be
  used with '__prepare__'. It defines a 'compile()' method and an
  '__init__()' signature compatible with the arguments passed to
  '__prepare__'.

  from . import AbstractNamespace as ASpace  # For brevity

  Specifically, '__prepare__' is defined as:
    def __prepare__(mcls, name: str, bases: Base, **kwargs) -> ASpace

  And 'ASpace' ('AbstractNamespace') implements:
    def __init__(self, mcls: type, name: str, bases: Base, **kwargs)

  This allows the namespace object to be instantiated with full context
  about the class being defined, while remaining isolated from the
  behavior of the resulting class itself. For more information about the
  class body execution flow, see the 'AbstractNamespace' class
  documentation.

  - CUSTOM CLASS CREATION -

  After assembly and compilation of the namespace, the metaclass itself
  takes responsibility for validating and finalizing the class.

  This includes a pass over the namespace via the '_validateNamespace'
  static method. It performs checks for common mistakes such as typos
  in special method names—for example:
    - '__set_item__' instead of '__setitem__'
    - '__get_attr__' instead of '__getattr__'
    - '__setname__' instead of '__set_name__'

  If any such names are found, a 'QuestionableSyntax' error is raised
  to prompt correction.

    -  '__del__' or '__delete__' ? -
  The descriptor protocol allows classes to define what happens when an
  attribute is deleted from an instance. This is handled by the '__delete__'
  method. It is much less common than '__get__' and '__set__', which govern
  attribute access and assignment, respectively.

  Because of the naming similarity to '__del__'—a special method for object
  finalization—it's easy to accidentally implement '__del__' when one meant
  '__delete__'.

  Bugs caused by incorrect use of `__del__`—especially when accidentally
  used instead of `__delete__`—are notoriously difficult to trace. Since
  `__del__` is called only when the object is garbage collected (which may
  be delayed or never happen), the consequences of the mistake are often
  deferred until long after the original action that should have triggered
  cleanup. This makes it extremely hard to correlate the broken behavior
  with its source. Worse still, because `__del__` doesn’t raise errors if
  used in the wrong context, failures are often silent, leading to
  inconsistent state, memory leaks, or subtle bugs in object lifecycles that
  resist even thorough debugging.

  For the above reasons, the 'worktoy' library will raise 'SyntaxError'
  whenever '__del__' is found in the namespace. If an implementation of
  '__del__' is actually intended, the class creation must be invoked
  with the keyword argument 'trustMeBro=True'.

    - Standard Methods -
  While not implemented in this metaclass, the following pattern allows
  sub-metaclasses to implement automatically generated methods in certain
  cases. The 'worktoy.ezdata.EZMeta' dataclass implementation exemplifies
  this pattern. Derived classes can define properties directly in the
  class body, and 'EZMeta' will automatically generate the necessary
  methods, such as '__init__', allowing for instantiation with either
  positional, keyword or even mixed arguments.

  The sub-metaclass would implement factories as static methods:

  from types import FunctionType as Func

  Bases: TypeAlias = tuple[type, ...]
  Space: TypeAlias = dict[str, Any]

  @staticmethod
  def __init_factory__(name: str, bases: Bases, space: Space, **kw) -> Func

  @staticmethod
  def __new_factory__(name: str, bases: Bases, space: Space, **kw) -> Func

  @staticmethod
  def __str_factory__(name: str, bases: Bases, space: Space, **kw) -> Func

  Finally, the sub-metaclass would have to implement:

  @staticmethod
  def autoGenMethods(name: str, bases: Bases, space: Space, **kw) -> Space:
    This method would be invoked after the namespace has been validated
    and before the class is created. It would return a modified namespace
    with the necessary methods added.

    - Notifying Baseclasses -
  Having validated the namespace, the metaclass falls back to type.__new__
  and returns the newly created class. Finally, this class arrives in the
  '__init__' method where the metaclass notifies any baseclass that
  implements the '__subclasshook__' method of the class creation. This
  marks the end of the class creation process.

  - CUSTOM CLASS BEHAVIOR -

  Once a class has been created by the metaclass system, it may define
  its own runtime behavior by implementing special methods prefixed with
  `__class_`. These allow the class object itself to participate directly
  in common operations such as being called, iterated, or printed.

  These methods resemble `__class_getitem__` from standard Python but are
  more general. Each of them overrides a specific class-level behavior.

  The following hooks relate to common class-level operations:

  - __class_call__(cls, *args, **kwargs) -> Any
    Called when the class object is called like a function. Overrides the
    default behavior of constructing instances. Can be used to implement
    singletons, factories, registries, etc.

  - __class_instancecheck__(cls, obj: Any) -> bool
    Called during isinstance(obj, cls). Controls how instance membership
    is determined. Supersedes metaclass-level __instancecheck__.

  - __class_subclasscheck__(cls, sub: type) -> bool
    Called during issubclass(sub, cls). Controls dynamic subclass logic.
    Allows behavior similar to abstract base classes or trait systems.

  #  The following hooks allow classes to define how they are printed

  - __class_str__(cls) -> str
    Called when str(cls) is invoked. Provides human-readable string form
    for dynamically generated or aliased classes.

  - __class_repr__(cls) -> str
    Called when repr(cls) is invoked. Allows classes to override their
    debug representation.

  #  The following hooks relate to class-level iteration

  - __class_iter__(cls) -> Iterator
    Called when iter(cls) is invoked. Makes the class object iterable.
    Useful for registry-style classes, enums, and similar patterns.

  - __class_next__(cls) -> Any
    Called when next(cls) is invoked. Meaningful only if the class itself
    is its own iterator as returned by __class_iter__.

  - __class_bool__(cls) -> bool
    Called when bool(cls) is invoked. Allows classes to define their truth
    value. By default, every class is 'truthy'.

  - __class_contains__(cls, item: Any) -> bool
    Allows classes to define membership checks on the class level. By
    default, this checks if the item is an instance of the class itself.

  - __class_len__(cls) -> int
    Called when len(cls) is invoked.

  - __class_hash__(cls) -> int
    Called when hash(cls) is invoked. Allows classes to define their own
    hash value. Defaults to:
    mcls = type(cls)  # The metaclass of the class
    baseNames = [b.__name__ for b in cls.__bases__]
    return hash((cls.__name__, *baseNames, mcls.__name__))
    #  PLEASE NOTE: The 'overload' protocol provided by the 'worktoy'
    library expects this exact hash value. Reimplementing the hash value
    will make the dispatching of overloads unable to 'fast' recognize the
    class.

  - __class_eq__(cls, other: Any) -> bool
    Called to allow classes to equal each other. Please note that this
    inclusion is for completeness more than anything else. The '__eq__' in
    this metaclass does look for '__class_eq__' on the class, but falls
    back to __class_hash__.

  The following hooks allows dictionary-like access to the class.

  - __class_getitem__(cls, item: Any) -> Any
    Called when cls[item] is invoked. Please note that this is already
    implemented in Python 3.7+ as a standard class method. It is listed
    here only for completeness. This means that this metaclass does not
    need to implement '__getitem__' to look for the '__class_getitem__' on
    the class itself. In fact, the __getitem__ on the metaclass would only
    ever be invoked if Foo['bar'] is invoked on a class Foo that does not
    implement '__class_getitem__'.

  - __class_setitem__(cls, item: Any, value: Any) -> None
    Called when cls[item] = value is invoked. 
    
  - __class_delitem__(cls, item: Any) -> None
    Called when del cls[item] is invoked.

    - Class Attribute Hooks -

  - __class_getattr__(name: str, exception: Exception) -> Any
    If a non-existing attribute is attempted accessed on a class object,
    the '__getattr__' method on the metaclass is invoked. This method
    allows the class itself to handle this case. It is strongly advised
    that this method, and '__getattr__' in general, raises an
    AttributeError unless the key passed to it has a valid and sensible
    meaning in the context.

  The following hooks allow classes to define custom behavior for
  attribute assignment and deletion at the class level.

  - __class_setattr__(name: str, value: Any) -> None
  - __class_delattr__(name: str) -> None

  The following hooks would be relevant only for nested classes that
  implement the descriptor protocol. These class-level descriptor hooks
  remain unimplemented due to unresolved hazards in Python's class
  construction behavior. In particular, referencing other class objects
  while a metaclass is "awake" (i.e., inside its __prepare__, __new__,
  or __init__) can lead to context leakage. Python may interpret unrelated
  class references within the scope of the active metaclass, sometimes
  routing calls to the wrong metaclass entirely.

  - __class_get__(cls, instance: Any, owner: type) -> Any
  - __class_set__(cls, instance: Any, value: Any) -> None
  - __class_delete__(cls, instance: Any) -> None
  - __class_set_name__(cls, owner: type, name: str) -> None

  Finally, the following hooks are logically meaningless:

  - __class_init__(...)
    There is no sensible point at which this would be called. Class
    objects are constructed by metaclasses, and no outer context exists
    in which to simulate an “init” phase.

  - __class_new__(...)
    Similar to above, class creation is driven by the metaclass’s
    __new__, and there is no standard mechanism for a class to override
    or participate in that step on its own behalf.

  - __class_del__(...)
    This remains unimplemented for the same reason as why the namespace
    validator described above raises a SyntaxError when it encounters
    '__del__' in the namespace.

  - __class_getattribute__(...)
    [REDACTED: Cognito Hazard]
  """

  @classmethod
  def __prepare__(mcls, name: str, bases: Base, **kwargs) -> ASpace:
    """The __prepare__ method is invoked before the class is created. This
    implementation ensures that the created class has access to the safe
    __init__ and __init_subclass__ through the BaseObject class in its
    method resolution order."""
    return ASpace(mcls, name, bases, **kwargs)

  def __new__(mcls, name: str, bases: Base, space: ASpace, **kw) -> type:
    """The __new__ method is invoked to create the class."""
    if hasattr(space, 'compile'):
      namespace = space.compile()
    else:
      namespace = mcls.__prepare__(name, bases, **kw)
      namespace = namespace.compile(space)
    cls = MetaType.__new__(mcls, name, bases, namespace, **kw)
    if hasattr(space, 'getHooks'):
      for hook in space.getHooks():
        cls = maybe(hook.newClassPhase(cls), cls)
    return cls

  def __init__(cls, name: str, bases: Base, space: ASpace, **kwargs) -> None:
    """The __init__ method is invoked to initialize the class."""
    try:
      cls.__class_init__(name, bases, space, **kwargs)
    except NotImplementedError:
      pass
    cls._notifySubclassHook(cls, *bases)

  def __call__(cls, *args, **kwargs) -> Any:
    try:
      out = cls.__class_call__(*args, **kwargs)
    except NotImplementedError:
      return MetaType.__call__(cls, *args, **kwargs)  # NOQA
    else:
      return out

  def __instancecheck__(cls, obj: Any) -> bool:
    try:
      out = cls.__class_instancecheck__(obj)
    except NotImplementedError:
      return MetaType.__instancecheck__(cls, obj)  # NOQA
    else:
      return True if out else False

  def __subclasscheck__(cls, subclass: type) -> bool:
    try:
      out = cls.__class_subclasscheck__(subclass)
    except NotImplementedError:
      return MetaType.__subclasscheck__(cls, subclass)  # NOQA
    else:
      return True if out else False

  def __str__(cls) -> str:
    try:
      out = cls.__class_str__()
    except NotImplementedError:
      return MetaType.__str__(cls)  # NOQA
    else:
      return out

  def __repr__(cls) -> str:
    try:
      out = cls.__class_repr__()
    except NotImplementedError:
      return MetaType.__repr__(cls)  # NOQA
    else:
      return out

  def __iter__(cls) -> Any:
    try:
      out = cls.__class_iter__()
    except NotImplementedError:
      infoSpec = """type object '%s' is not iterable"""
      info = infoSpec % type(cls).__name__
      raise TypeError(info)
    else:
      return out

  def __next__(cls) -> Any:
    try:
      out = cls.__class_next__()
    except NotImplementedError:
      return MetaType.__next__(cls)  # NOQA
    else:
      return out

  def __bool__(cls) -> bool:
    """
    Here, too, I saw a nation of lost souls,
    far more than were above: they strained their chests
    against enormous weights, and with mad howls
    rolled them at one another. Then in haste
    they rolled them back, one party shouting out:
    "Why do you hoard?" and the other: "Why do you waste?"
    """
    try:
      out = cls.__class_bool__()
    except NotImplementedError:
      try:
        out = len(cls)  # NOQA
      except Exception as exception:
        return True
      else:
        return True if out else False
    else:
      return True if out else False

  def __contains__(cls, item: Any) -> bool:
    try:
      out = cls.__class_contains__(item)
    except NotImplementedError:
      out = None
      try:
        for clsItem in cls:
          if clsItem == item:
            out = True
            break
        else:
          out = False
      except Exception as exception:
        infoSpec = """argument of type '%s' is not iterable"""
        info = infoSpec % type(cls).__name__
        raise TypeError(info) from exception
      else:
        return True if out else False
    else:
      return True if out else False

  def __len__(cls) -> int:
    try:
      out = cls.__class_len__()
    except NotImplementedError:
      try:
        countingWithAsger = sum([1 for derp in cls])
      except Exception as exception:  # NOQA
        return len(MetaType)  # NOQA
      else:
        return countingWithAsger
    else:
      return out

  def __hash__(cls) -> int:
    try:
      out = cls.__class_hash__()
    except NotImplementedError:
      baseNames = [b.__name__ for b in cls.__bases__]
      metaName = type(cls).__name__
      nameTuple = (cls.__name__, *baseNames, metaName)
      return hash(nameTuple)  # NOQA
    else:
      return out

  #  DO NOT REMOVE THE FOLLOWING COMMENTED OUT METHODS
  # def __eq__(cls, other: Any) -> bool:
  #   """This method is disabled because of highly undefined behaviour!"""
  #
  #  def __ne__(cls, other: Any) -> bool:
  #    """See above"""

  #  DO NOT REMOVE THIS COMMENTED OUT METHOD  (not related to above)
  # def __getitem__(cls, item: Any) -> Any:
  #   """
  #   This method is intentionally commented out — not removed — to ensure
  #   discoverability and traceability.
  #   """
  #
  #   For an explanation, see the '__class_getitem__' note in the 'NameHook'
  #   class, located in 'worktoy.mcls.space_hooks'. In short, the interpreter
  #   handles '__class_getitem__' directly as of Python 3.7, making this
  #   override unnecessary and potentially conflicting.

  def __setitem__(cls, item: Any, value: Any) -> None:
    try:
      out = cls.__class_setitem__(item, value)
    except NotImplementedError:
      return MetaType.__setitem__(cls, item, value)  # NOQA
    else:
      return None

  def __delitem__(cls, item: Any) -> None:
    try:
      out = cls.__class_delitem__(item)
    except NotImplementedError:
      return MetaType.__delitem__(cls, item)  # NOQA
    else:
      return None

  def __getattr__(cls, name: str) -> Any:
    """Do not use the 'dot' operator to access class attributes during
    this method! Instead, the clunky 'object.__getattribute__' must be
    used to avoid infinite recursion. This is not an edge case, if you
    bring the 'dot' operator into an implementation here, it is recursion
    time!"""
    try:
      classGetAttr = object.__getattribute__(cls, '__class_getattr__')
      out = classGetAttr.__func__(cls, name)
    except NotImplementedError:
      raise AttributeError(name)
    else:
      return out

  def __setattr__(cls, name: str, value: Any) -> None:
    try:
      out = cls.__class_setattr__(name, value)
    except NotImplementedError:
      return MetaType.__setattr__(cls, name, value)  # NOQA
    else:
      return None

  def __delattr__(cls, name: str) -> None:
    try:
      out = cls.__class_delattr__(name)
    except NotImplementedError:
      return MetaType.__delattr__(cls, name)  # NOQA
    else:
      return None

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  DOMAIN SPECIFIC  # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  @staticmethod
  def _notifySubclassHook(cls, *bases) -> type:
    """The _notifySubclassHook method is invoked to notify each baseclass
    of the created class of the class creation."""
    for base in bases:
      hook = getattr(base, '__subclasshook__', None)
      hook(cls)
    return cls

  def getNamespace(cls) -> ASpace:
    """Get the namespace object for the class."""
    return getattr(cls, '__namespace__', )

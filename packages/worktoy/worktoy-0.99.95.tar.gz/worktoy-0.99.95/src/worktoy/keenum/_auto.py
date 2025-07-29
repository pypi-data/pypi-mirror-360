"""
The 'auto' function conveniently specifies a member of a KeeNum
enumeration right in the class body.

When subclasses of KeeNum are created, the 'auto' function collects
positional and keyword arguments later used to instantiate the member
type to create the enumeration member value.


"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING

from ..core import Object

if TYPE_CHECKING:  # pragma: no cover
  from typing import Any


class _AutoMember(Object):
  """
  _AutoMember encapsulates future enumeration member objects. The 'auto'
  function instantiates this class during the class body execution. The
  control flow collects these objects during compilation of the final
  namespace object. For this reason, _AutoMember is private to the
  'worktoy.keenum' module. Instances of _AutoMember are discarded during the
  class creation process.
  """

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  NAMESPACE  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  #  Private variables
  __auto_member__ = True

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #  GETTERS  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

  # getKeywordArgs = Object._getKeywordArgs  # Going public
  # getPositionalArgs = Object._getPositionalArgs  # Going public

  def getValue(self) -> Any:
    """
    Returns the first positional argument
    """
    return (self.getPosArgs() or [None, ])[0]


def auto(*args: Any, **kwargs: Any) -> Object:
  """
  The 'auto' function conveniently specifies a member of a KeeNum
  enumeration right in the class body.

  When subclasses of KeeNum are created, the 'auto' function collects
  positional and keyword arguments later used to instantiate the member
  type to create the enumeration member value.
  """

  return _AutoMember(*args, **kwargs, )

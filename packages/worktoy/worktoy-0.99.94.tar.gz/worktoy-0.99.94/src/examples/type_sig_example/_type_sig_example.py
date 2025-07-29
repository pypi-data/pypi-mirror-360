"""
Code example from 'TypeSig' documentation.
"""
#  AGPL-3.0 license
#  Copyright (c) 2025 Asger Jon Vistisen
from __future__ import annotations

import sys
from math import atan2

from worktoy.waitaminute import HashMismatch, CastMismatch, FlexMismatch
from worktoy.static import TypeSig


def angle(*args, ) -> float:
  """
  Computes the argument of the complex number: x + yJ
  """
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


def main(*args) -> int:  # NOQA: Pycharm, read up on 'finally'!
  """Main script entry point."""
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

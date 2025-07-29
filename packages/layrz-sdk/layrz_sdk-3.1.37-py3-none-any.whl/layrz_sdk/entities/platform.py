"""Platform"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class Platform(str, Enum):
  """
  Platform definition
  """

  WEB = 'WEB'
  """ Web browser """

  ANDROID = 'ANDROID'
  """ Google Android """

  IOS = 'IOS'
  """ Apple iOS """

  WINDOWS = 'WINDOWS'
  """ Microsoft Windows """

  MACOS = 'MACOS'
  """ Apple MacOS """

  LINUX = 'LINUX'
  """ GNU/Linux """

  LAYRZ_OS = 'LAYRZ_OS'
  """ Layrz OS for embedding systems """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'Platform.{self.name}'

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class MapCenterType(str, Enum):
  """Map Chart center type"""

  FIXED = 'FIXED'
  CONTAIN = 'CONTAIN'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'MapCenterType.{self.name}'

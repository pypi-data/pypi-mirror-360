"""Chart alignment"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ChartAlignment(str, Enum):
  """
  Chart Alignment
  """

  CENTER = 'center'
  LEFT = 'left'
  RIGHT = 'right'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartAlignment.{self.name}'

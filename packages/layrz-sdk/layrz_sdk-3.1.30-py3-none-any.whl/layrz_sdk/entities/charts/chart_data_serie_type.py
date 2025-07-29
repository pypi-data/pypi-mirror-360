"""Chart Serie type"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ChartDataSerieType(Enum):
  """
  Chart data serie type
  """

  NONE = None
  LINE = 'line'
  AREA = 'area'
  SCATTER = 'scatter'

  def __str__(self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self) -> str:
    """Readable property"""
    return f'ChartDataSerieType.{self.name}'

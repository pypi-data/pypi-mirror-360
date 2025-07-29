"""Chart Data type"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ChartDataType(str, Enum):
  """
  Chart Data Type
  """

  STRING = 'STRING'
  DATETIME = 'DATETIME'
  NUMBER = 'NUMBER'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartDataType.{self.name}'

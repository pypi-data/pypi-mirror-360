import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ReportDataType(str, Enum):
  """
  Report date type
  """

  STR = 'str'
  INT = 'int'
  FLOAT = 'float'
  DATETIME = 'datetime'
  BOOL = 'bool'
  CURRENCY = 'currency'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ReportDataType.{self.value}'

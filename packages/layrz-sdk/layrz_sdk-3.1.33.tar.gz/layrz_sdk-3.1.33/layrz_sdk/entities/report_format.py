"""Report formats"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ReportFormat(str, Enum):
  """
  Report format definition.
  """

  MICROSOFT_EXCEL = 'MICROSOFT_EXCEL'
  JSON = 'JSON'
  PDF = 'PDF'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ReportFormat.{self.value}'

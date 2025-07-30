"""Chart rendering technology / library"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ChartRenderTechnology(str, Enum):
  """
  Chart Alignment
  """

  CANVAS_JS = 'CANVAS_JS'
  GRAPHIC = 'GRAPHIC'
  SYNCFUSION_FLUTTER_CHARTS = 'SYNCFUSION_FLUTTER_CHARTS'
  FLUTTER_MAP = 'FLUTTER_MAP'
  APEX_CHARTS = 'APEX_CHARTS'
  FLUTTER = 'FLUTTER'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartRenderTechnology.{self.value}'

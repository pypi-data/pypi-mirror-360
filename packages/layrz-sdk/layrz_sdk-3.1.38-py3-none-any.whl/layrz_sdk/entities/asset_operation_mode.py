"""Asset Operation Mode"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class AssetOperationMode(str, Enum):
  """
  Asset Operation mode definition
  It's an enum of the operation mode of the asset.
  """

  SINGLE = 'SINGLE'
  MULTIPLE = 'MULTIPLE'
  ASSETMULTIPLE = 'ASSETMULTIPLE'
  DISCONNECTED = 'DISCONNECTED'
  STATIC = 'STATIC'
  ZONE = 'ZONE'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'AssetOperationMode.{self.name}'

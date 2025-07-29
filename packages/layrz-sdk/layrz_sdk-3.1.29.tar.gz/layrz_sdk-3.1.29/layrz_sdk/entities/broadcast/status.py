"""Broadcast result Status"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class BroadcastStatus(str, Enum):
  """Broadcast result status"""

  OK = 'OK'
  BADREQUEST = 'BADREQUEST'
  INTERNALERROR = 'INTERNALERROR'
  UNAUTHORIZED = 'UNAUTHORIZED'
  UNPROCESSABLE = 'UNPROCESSABLE'
  DISCONNECTED = 'DISCONNECTED'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'BroadcastStatus.{self.name}'

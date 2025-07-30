"""Action geofence ownership"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class ActionGeofenceOwnership(str, Enum):
  """
  Action geofence ownership definition
  """

  NONE = 'NONE'
  """ Not assigned to any owner (Orphan) """

  ASSET = 'ASSET'
  """ Assigns the geofence to the owner of the asset """

  ACTION = 'ACTION'
  """ Assigns the geofence to the owner of the action """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ActionGeofenceOwnership.{self.name}'

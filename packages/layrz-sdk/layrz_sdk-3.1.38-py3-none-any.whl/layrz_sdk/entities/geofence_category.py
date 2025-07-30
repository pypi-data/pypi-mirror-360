"""Geofence category"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class GeofenceCategory(str, Enum):
  """
  Geofence category definition
  """

  NONE = 'NONE'
  """ Classic or uncategorized geofence """

  CUSTOM = 'CUSTOM'
  """ Geofence with non-standard category """

  ADMINISTRATIVE = 'ADMINISTRATIVE'
  """ Geofence as administrative area """

  CUSTOMER = 'CUSTOMER'
  """ Geofence as customer location """

  PROSPECT = 'PROSPECT'
  """ Similar to customer location but not yet a customer """

  OTHER = 'OTHER'
  """ Other geofence category """

  POLYGON = 'POLYGON'
  """ Geofence as search geozone """

  LEAD = 'LEAD'
  """ Geofence as lead location, not yet a prospect or customer """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'GeofenceCategory.{self.name}'

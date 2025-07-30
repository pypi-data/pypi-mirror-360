"""Waypoint entity"""

from datetime import datetime

from pydantic import BaseModel, Field

from .geofence import Geofence


class Waypoint(BaseModel):
  """Waypoint entity definition"""

  pk: int = Field(description='Waypoint ID')
  geofence: Geofence = Field(description='Geofence object')
  start_at: datetime = Field(description='Waypoint start date')
  end_at: datetime = Field(description='Waypoint end date')
  sequence_real: int = Field(description='Real sequence number')
  sequence_ideal: int = Field(description='Ideal sequence number')

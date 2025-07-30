"""Geofence entity"""

from pydantic import BaseModel, Field


class Geofence(BaseModel):
  """Geofence entity"""

  pk: int = Field(description='Defines the primary key of the geofence')
  name: str = Field(description='Defines the name of the geofence')
  color: str = Field(description='Defines the color of the geofence')

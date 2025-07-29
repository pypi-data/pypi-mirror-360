"""Checkpoints entitites"""

from datetime import datetime

from pydantic import BaseModel, Field

from .waypoint import Waypoint


class Checkpoint(BaseModel):
  """Checkpoint entity definition"""

  pk: int = Field(description='Checkpoint ID')
  asset_id: int = Field(description='Asset ID')
  waypoints: list[Waypoint] = Field(description='List of waypoints', default_factory=list)
  start_at: datetime = Field(description='Checkpoint start date')
  end_at: datetime = Field(description='Checkpoint end date')

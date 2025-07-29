"""Event entity"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .geofence import Geofence
from .message import Message
from .presence_type import PresenceType
from .trigger import Trigger


class Event(BaseModel):
  """Event entity definition"""

  pk: int = Field(description='Event ID')
  trigger: Trigger = Field(description='Event trigger')
  asset_id: int = Field(description='Asset ID')
  message: Message = Field(description='Message')
  activated_at: datetime = Field(description='Event activation date')
  geofence: Optional[Geofence] = Field(default=None, description='Geofence object')
  presence_type: Optional[PresenceType] = Field(default=None, description='Presence type object')

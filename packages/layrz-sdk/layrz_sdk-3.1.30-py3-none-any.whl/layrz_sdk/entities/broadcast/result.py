"""Broadcast result"""

from datetime import datetime

from pydantic import BaseModel, Field

from .request import BroadcastRequest
from .response import BroadcastResponse
from .status import BroadcastStatus


class BroadcastResult(BaseModel):
  """Broadcast result data"""

  service_id: int = Field(description='Service ID')
  asset_id: int = Field(description='Asset ID')
  status: BroadcastStatus = Field(description='Broadcast status')
  request: BroadcastRequest = Field(description='Broadcast request')
  response: BroadcastResponse = Field(description='Broadcast response')
  submitted_at: datetime = Field(description='Broadcast submission date')

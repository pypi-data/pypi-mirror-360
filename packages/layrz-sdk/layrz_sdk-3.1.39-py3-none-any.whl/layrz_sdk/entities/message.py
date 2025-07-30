"""Message entity"""

from datetime import datetime
from typing import Any, TypeAlias

from pydantic import BaseModel, Field

from layrz_sdk.constants import UTC

from .position import Position

PayloadType: TypeAlias = dict[str, Any]


class Message(BaseModel):
  """Message definition"""

  pk: int
  asset_id: int
  position: Position = Field(default_factory=lambda: Position())
  payload: PayloadType = Field(default_factory=dict)
  sensors: PayloadType = Field(default_factory=dict)
  received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

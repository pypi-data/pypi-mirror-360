"""Service entity"""

from pydantic import BaseModel, Field


class OutboundService(BaseModel):
  """Outbound service definition"""

  pk: int = Field(description='Service ID')
  name: str = Field(description='Service name')

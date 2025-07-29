"""Timezone entity"""

from pydantic import BaseModel, Field


class Timezone(BaseModel):
  """Timezone entity"""

  pk: int = Field(..., description='Defines the primary key of the timezone', alias='id')
  name: str = Field(..., description='Defines the name of the timezone')
  color: str = Field(default='#2196F3', description='Defines the color of the timezone in hex format')

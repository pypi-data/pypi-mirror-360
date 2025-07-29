"""Trigger entity"""

from pydantic import BaseModel, Field


class Trigger(BaseModel):
  """Trigger entity"""

  pk: int = Field(description='Defines the primary key of the trigger')
  name: str = Field(description='Defines the name of the trigger')
  code: str = Field(description='Defines the code of the trigger')

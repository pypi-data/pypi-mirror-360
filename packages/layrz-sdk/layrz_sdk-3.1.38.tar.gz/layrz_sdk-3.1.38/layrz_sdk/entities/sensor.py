"""Sensor entity"""

from pydantic import BaseModel, Field


class Sensor(BaseModel):
  """Sensor entity"""

  pk: int = Field(description='Defines the primary key of the sensor')
  name: str = Field(description='Defines the name of the sensor')
  slug: str = Field(description='Defines the slug of the sensor')

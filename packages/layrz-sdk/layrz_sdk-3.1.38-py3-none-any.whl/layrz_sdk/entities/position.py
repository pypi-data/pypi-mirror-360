"""Position entity"""

import sys
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class Position(BaseModel):
  """Geographic position definition"""

  latitude: Optional[float] = Field(default=None, description='Defines the latitude of the position')
  longitude: Optional[float] = Field(default=None, description='Defines the longitude of the position')
  altitude: Optional[float] = Field(default=None, description='Defines the altitude of the position')
  hdop: Optional[float] = Field(default=None, description='Defines the horizontal dilution of precision')
  speed: Optional[float] = Field(default=None, description='Defines the speed of the position')
  direction: Optional[float] = Field(default=None, description='Defines the direction of the position')
  satellites: Optional[int] = Field(
    default=None,
    description='Defines the number of satellites used to calculate the position',
  )

  @field_validator('latitude', mode='before')
  def _validate_latitude(cls: Self, value: Any) -> None | float:
    """Validate latitude"""
    if value is None:
      return None

    if not isinstance(value, (int, float)):
      return None

    if isinstance(value, int):
      value = float(value)

    if -90 <= value <= 90:
      return value

    return None

  @field_validator('longitude', mode='before')
  def _validate_longitude(cls: Self, value: Any) -> None | float:
    """Validate longitude"""
    if value is None:
      return None

    if not isinstance(value, (int, float)):
      return None

    if isinstance(value, int):
      value = float(value)

    if -180 <= value <= 180:
      return value

    return None

  @field_validator('altitude', mode='before')
  def _validate_altitude(cls: Self, value: Any) -> None | float:
    """Validate altitude"""
    if value is None:
      return None

    if not isinstance(value, (float, int)):
      return None

    return value

  @field_validator('hdop', mode='before')
  def _validate_hdop(cls: Self, value: Any) -> None | float:
    """Validate hdop"""
    if value is None:
      return None

    if not isinstance(value, (int, float)):
      return None

    if isinstance(value, int):
      value = float(value)

    return value

  @field_validator('speed', mode='before')
  def _validate_speed(cls: Self, value: Any) -> None | float:
    """Validate speed"""
    if value is None:
      return None

    if not isinstance(value, (float, int)):
      return None

    if isinstance(value, int):
      value = float(value)

    return abs(value)

  @field_validator('direction', mode='before')
  def _validate_direction(cls: Self, value: Any) -> None | float:
    """Validate direction"""
    if value is None:
      return None

    if not isinstance(value, (float, int)):
      return None

    if isinstance(value, int):
      value = float(value)

    if 0 <= value <= 360:
      return value

    return None

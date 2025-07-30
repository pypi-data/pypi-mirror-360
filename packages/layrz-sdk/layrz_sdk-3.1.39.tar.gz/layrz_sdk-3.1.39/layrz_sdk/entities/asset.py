"""Asset Entity"""

import sys
from typing import Any

from pydantic import BaseModel, Field, model_validator

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from .asset_operation_mode import AssetOperationMode
from .custom_field import CustomField
from .device import Device
from .sensor import Sensor
from .static_position import StaticPosition


class Asset(BaseModel):
  """Asset entity definition"""

  pk: int = Field(description='Defines the primary key of the asset')
  name: str = Field(description='Defines the name of the asset')
  vin: str | None = Field(
    default=None,
    description='Defines the serial number of the asset, may be an VIN, or any other unique identifier',
  )
  plate: str | None = Field(default=None, description='Defines the plate number of the asset')
  asset_type: int | None = Field(description='Defines the type of the asset', alias='kind_id', default=None)
  operation_mode: AssetOperationMode = Field(description='Defines the operation mode of the asset')
  sensors: list[Sensor] = Field(default_factory=list, description='Defines the list of sensors of the asset')
  custom_fields: list[CustomField] = Field(
    default_factory=list, description='Defines the list of custom fields of the asset'
  )
  devices: list[Device] = Field(default_factory=list, description='Defines the list of devices of the asset')
  children: list[Self] = Field(default_factory=list, description='Defines the list of children of the asset')

  static_position: StaticPosition | None = Field(
    default=None,
    description='Static position of the asset',
  )

  points: list[StaticPosition] = Field(
    default_factory=list,
    description='List of static positions for the asset. The altitude of StaticPosition is not used in this case.',
  )

  primary_id: int | None = Field(
    default=None,
    description='Defines the primary device ID of the asset',
  )

  @model_validator(mode='before')
  def _validate_model(cls: Self, data: dict[str, Any]) -> dict[str, Any]:
    """Validate model"""
    operation_mode: str | None = data.get('operation_mode')
    if operation_mode == AssetOperationMode.ASSETMULTIPLE.name:
      data['devices'] = []

    else:
      data['children'] = []

    return data

  @property
  def primary(self: Self) -> Device | None:
    """Get primary device"""
    if self.operation_mode not in [AssetOperationMode.SINGLE, AssetOperationMode.MULTIPLE]:
      return None

    for device in self.devices:
      if device.is_primary:
        return device

    return None

  contacts: list[str] = Field(
    default_factory=list,
    description='Defines the list of contacts of the asset, used for notifications',
  )

  owner_id: int | None = Field(
    default=None,
    description='Owner ID',
  )

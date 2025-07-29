"""Geofence entity"""

from datetime import timedelta
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, constr

from .asset import Asset


class Function(BaseModel):
  """Function entity"""

  pk: int = Field(description='Defines the primary key of the Function')
  name: str = Field(description='Name of the function')

  maximum_time: Optional[timedelta] = None  # DurationField → timedelta
  minutes_delta: Optional[timedelta] = None

  external_identifiers: List[constr(max_length=255)] = Field(default_factory=list)  # type: ignore

  credentials: Dict[str, Any] = Field(default_factory=dict)

  # Many-to-manys  ➜  list of nested DTOs
  assets: List[Asset] = Field(default_factory=list)

  # Foreign keys – normally expose only the FK id to keep the payload small.
  owner_id: Optional[int] = None
  algorithm_id: int

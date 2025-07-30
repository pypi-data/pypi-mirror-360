"""Custom Field entitiy"""

from pydantic import BaseModel, Field


class CustomField(BaseModel):
  """Custom field definition"""

  name: str = Field(description='Defines the name of the custom field')
  value: str = Field(description='Defines the value of the custom field')

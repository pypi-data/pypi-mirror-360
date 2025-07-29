from enum import Enum


class ModbusSchema(str, Enum):
  """Modbus schema enumeration"""

  SINGLE = 'SINGLE'
  """ Defines a single Modbus request. """
  MULTIPLE = 'MULTIPLE'
  """ Defines multiple Modbus requests. """

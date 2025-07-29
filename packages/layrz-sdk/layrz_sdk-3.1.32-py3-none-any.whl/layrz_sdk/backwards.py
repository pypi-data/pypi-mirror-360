"""Backwards compatibility"""

from enum import Enum


class StrEnum(str, Enum): ...

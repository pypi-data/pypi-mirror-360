"""Twilio Notification Type Enum"""

import sys
from enum import Enum

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class TwilioNotificationType(str, Enum):
  """
  Twilio Notification Type Enum definition
  """

  SMS = 'SMS'
  """ Short Message Service (SMS) notification type, used for sending text messages. """

  VOICE = 'VOICE'
  """ Voice notification type, used for making phone calls. """

  WHATSAPP = 'WHATSAPP'
  """ WhatsApp notification type, used for sending messages via WhatsApp. """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'TwilioNotificationType.{self.name}'

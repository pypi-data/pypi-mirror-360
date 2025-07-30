"""Operation entity"""

from datetime import time, timedelta
from typing import Any

from pydantic import BaseModel, Field

from .notification_type import TwilioNotificationType
from .operation_type import OperationType
from .platform import Platform
from .request_type import HttpRequestType
from .sound_effect import SoundEffect
from .timezone import Timezone


class Operation(BaseModel):
  """Operation entity"""

  model_config = {
    'json_encoders': {
      timedelta: lambda v: v.total_seconds(),
      OperationType: lambda v: v.value,
      HttpRequestType: lambda v: v.value,
      TwilioNotificationType: lambda v: v.value,
      SoundEffect: lambda v: v.value,
      Platform: lambda v: v.value,
    },
  }

  pk: int = Field(description='Defines the primary key of the trigger', alias='id')
  name: str = Field(description='Defines the name of the trigger')

  cooldown_time: timedelta = Field(
    default_factory=lambda: timedelta(seconds=0),
    description='Defines the cooldown time of the trigger',
  )

  kind: OperationType = Field(
    ...,
    description='Defines the kind of the operation',
    alias='operation_type',
  )

  http_method: HttpRequestType | None = Field(
    default=None,
    description='Defines the HTTP method of the operation',
    alias='request_type',
  )

  url: str | None = Field(
    default=None,
    description='Defines the URL of the operation',
  )

  headers: list[dict[str, Any]] = Field(
    default_factory=list,
    description='Defines the headers of the operation',
  )

  reception_emails: list[str] = Field(
    default_factory=list,
    description='Defines the reception emails of the operation',
  )

  language_id: int = Field(
    default=2,
    description='Defines the language ID of the operation',
  )

  payload: str = Field(
    default='',
    description='Defines the payload of the operation',
  )

  timezone_id: int | None = Field(
    default=None,
    description='Defines the timezone ID of the operation',
  )

  email_subject: str = Field(
    default='',
    description='Defines the email subject of the operation',
  )

  color: str = Field(
    default='#2196F3',
    description='Defines the color of the operation',
  )

  external_account_id: int | None = Field(
    default=None,
    description='Defines the external account ID of the operation',
    alias='account_id',
  )

  twilio_notification_type: TwilioNotificationType = Field(
    default=TwilioNotificationType.SMS,
    description='Defines the Twilio notification type of the operation',
    alias='notification_type',
  )

  host_phone: str | None = Field(
    default=None,
    description='Defines the host phone number for Twilio notifications',
  )

  username: str | None = Field(
    default=None,
    description='Defines the username for the operation, used for authentication in some cases',
  )

  token: str | None = Field(
    default=None,
    description='Defines the token for the operation, used for authentication in some cases',
  )

  destination_phones: list[str] = Field(
    default_factory=list,
    description='Defines the destination phone numbers for Twilio notifications',
  )

  attach_image: bool = Field(
    default=False,
    description='Defines if the operation should attach an image',
  )

  use_asset_contacts_instead: bool = Field(
    default=False,
    description='Defines if the operation should use asset contacts instead of reception emails',
  )

  email_template_id: int | None = Field(
    default=None,
    description='Defines the email template ID of the operation',
  )

  push_platforms: list[Platform] = Field(
    default_factory=list,
    description='Defines the platforms for push notifications',
  )

  push_title: str = Field(
    default='',
    description='Defines the title for push notifications',
  )

  requires_bhs_validation: bool = Field(
    default=False,
    description='Defines if the operation requires BHS validation',
  )

  bhs_tier_id: int | None = Field(
    default=None,
    description='Defines the BHS tier ID for the operation',
  )

  sound_effect: SoundEffect = Field(
    default=SoundEffect.NONE,
    description='Defines the sound effect for the operation',
  )

  sound_effect_uri: str | None = Field(
    default=None,
    description='Defines the URI for the sound effect of the operation. Only when sound_effect is set to CUSTOM.',
  )

  duration: timedelta = Field(
    default_factory=lambda: timedelta(seconds=5),
    description='Defines the duration of the operation',
  )

  credentials: dict[str, Any] = Field(
    default_factory=dict,
    description='Defines the credentials for the operation',
  )

  timezone: Timezone | None = Field(
    default=None,
    description='Defines the timezone of the operation',
  )

  icon: str | None = Field(
    default=None,
    description='Defines the icon for the operation',
  )

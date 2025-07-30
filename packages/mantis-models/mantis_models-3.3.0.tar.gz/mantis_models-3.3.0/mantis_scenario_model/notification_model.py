# -*- coding: utf-8 -*-
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class NotificationStage(str, Enum):
    platform = "Platform"
    it_simulation = "IT simulation"
    user_activity = "User activity"
    provisioning = "Provisioning"
    redteam = "Redteam"


class Notification(BaseModel):
    event_datetime: Optional[str] = None
    event_data: str
    stage: NotificationStage

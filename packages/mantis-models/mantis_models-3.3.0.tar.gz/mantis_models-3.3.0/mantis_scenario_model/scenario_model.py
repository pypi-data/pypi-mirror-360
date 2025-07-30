# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict

from .common import Timestamps
from .common import WorkerMitreData
from .lab_config_model import ScenarioProfile


class Steps(BaseModel):
    skip_deploy: bool = False
    skip_all_preparations: bool = False
    skip_provisioning_os_set_time: bool = False
    skip_provisioning_os_set_hostname: bool = False
    skip_provisioning_attack: bool = False
    skip_provisioning_os_monitoring: bool = False
    skip_user_activity: bool = False
    skip_compromise: bool = False
    skip_attack: bool = False
    skip_create_dataset: bool = False


class Scenario(BaseModel):
    name: str = "default scenario name"
    keywords: List[str] = []
    description: str = ""
    description_fr: str = ""
    long_description: List[str] = []
    long_description_fr: List[str] = []
    unit_attacks: List[str] = []
    attacks: List[str] = []
    mitre_tags: Optional[List[WorkerMitreData]] = []
    steps: Optional[Steps] = Steps()
    timestamps: Optional[Timestamps] = None
    scenario_profiles: List[ScenarioProfile] = []
    creation_date: datetime
    last_update: datetime
    learning_context: str = ""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

# -*- coding: utf-8 -*-
import re
from datetime import datetime
from enum import Enum
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator

from .common import Timestamps
from .common import mitre_attack_data
from .common import MitreIdName
from .common import WorkerMitreData
from .lab_config_model import ScenarioProfile


class SideEffect(str, Enum):
    network_connection = "NETWORK_CONNECTION"
    artifacts_on_disk = "ARTIFACTS_ON_DISK"
    config_changes = "CONFIG_CHANGES"
    ioc_in_logs = "IOC_IN_LOGS"
    account_lockouts = "ACCOUNT_LOCKOUTS"
    screen_effects = "SCREEN_EFFECTS"


class Topics(str, Enum):
    attack_session = "attack_session"
    host = "host"
    credential = "credential"
    file = "file"
    network = "network_interface"
    payload = "payload"
    service = "service"
    software = "software"
    infrastructure = "infrastructure"


class AttackMode(str, Enum):
    direct = "DIRECT"
    indirect = "INDIRECT"
    offline = "OFFLINE"
    infrastructure = "INFRASTRUCTURE"


class UnitAttack(BaseModel):
    name: str
    worker_id: str
    title: Optional[str] = ""
    title_fr: Optional[str] = ""
    description: str
    description_fr: str
    links: List[str] = []
    version: str
    side_effects: List[SideEffect] = []
    repeatable: bool
    topics: List[Topics] = []
    attack_mode: AttackMode = AttackMode.indirect
    cve: List[str] = []
    mitre_data: WorkerMitreData = None  # type: ignore
    options: List[Any] = []
    scenario_profiles: List[ScenarioProfile] = []
    timestamps: Optional[Timestamps] = None
    creation_date: datetime
    last_update: datetime

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @field_validator("worker_id")
    def valid_worker_id(cls, v: str) -> str:
        pattern = r"^\d{4}_\d{3}_\d{3}$"
        if not re.match(pattern, v):
            raise ValueError("not match")
        return v

    @field_validator("links")
    def set_empty_list_for_links(cls, v: Union[None, List[str]]) -> List[str]:
        if v is None:
            return []
        else:
            return v

    @field_validator("side_effects")
    def set_empty_list_for_side_effects(cls, v: List[str]) -> List[str]:
        return v or []

    @field_validator("topics")
    def set_empty_list_for_side_topics(cls, v: List[str]) -> List[str]:
        return v or []

    def model_post_init(self, __context) -> None:
        if self.mitre_data is None:
            if self.worker_id is not None:
                ids = self.worker_id.split("_")
                technique_id = f"T{ids[0]}"
                subtechnique_id = ids[1]
                implementation_id = ids[2]

                if subtechnique_id != "000":
                    mitre_id = f"{technique_id}.{subtechnique_id}"
                else:
                    mitre_id = f"{technique_id}"

                mitre_technique = None
                mitre_subtechnique = {}
                mitre_tactic = []

                implementation = {"id": implementation_id}

                technique_name = None
                for technique in mitre_attack_data["techniques"]:
                    if technique["id"] == technique_id:
                        technique_name = technique["name"]
                        mitre_technique = MitreIdName(
                            **{"id": technique_id, "name": technique_name}
                        )
                        for subtechnique in technique["subtechniques"]:
                            if subtechnique["id"] == mitre_id:
                                mitre_subtechnique = MitreIdName(
                                    **{"id": mitre_id, "name": subtechnique["name"]}
                                )
                                break
                        for tactic in technique["tactics"]:
                            mitre_tactic.append(
                                MitreIdName(
                                    **{
                                        "id": tactic["id"],
                                        "name": tactic["name"],
                                    }
                                )
                            )
                        break

                if (
                    technique_name is None
                    or mitre_technique is None
                    or len(mitre_tactic) == 0
                    or implementation is None
                ):
                    raise Exception(f"Error getting information about {mitre_id}.")

                self.mitre_data = WorkerMitreData(
                    **{
                        "technique": mitre_technique,
                        "subtechnique": mitre_subtechnique,
                        "tactics": mitre_tactic,
                        "implementation": implementation,
                    }
                )

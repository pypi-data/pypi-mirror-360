# -*- coding: utf-8 -*-
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from mantis_scenario_model.scenario_model import Scenario
from mantis_scenario_model.unit_attack_model import UnitAttack
from mantis_scenario_model.unit_attack_model import WorkerMitreData
from pydantic import BaseModel
from pydantic import ConfigDict


class ResourceType(str, Enum):
    """
    Enum for the resource type
    """

    log = "log"
    pcap = "pcap"
    memory_dump = "memory_dump"
    redteam_report = "redteam_report"
    life_report = "life_report"
    assets_report = "assets_report"
    forensic = "forensic"


class ResourceFile(BaseModel):
    """
    Model representing a file within a resource
    """

    size: int
    file_url: Path

    # Ensures Model Validation is performed when a member is set after the creation of the object
    model_config = ConfigDict(validate_assignment=True)


class ResourceBase(BaseModel):
    """
    Base model for all resource types
    """

    type: ResourceType
    files: List[ResourceFile]

    # Ensures Model Validation is performed when a member is set after the creation of the object
    model_config = ConfigDict(validate_assignment=True)


class ResourceLog(ResourceBase):
    machine: str
    log_format: str


class ResourceForensic(ResourceBase):
    machine: str
    forensic_tool: str


class ResourcePcap(ResourceBase):
    date_start: datetime
    date_end: datetime
    relationship_probe_nodes: Optional[List[dict]] = None


class ResourceMemoryDump(ResourceBase):
    date: datetime
    node_id: int
    dump_failure: bool


class ResourceLifeReport(ResourceBase):
    date: datetime


class ResourceAssetsReport(ResourceBase):
    date: datetime


class Manifest(BaseModel):
    """
    Model for a manifest.

    Corresponds to the contents of the manifest.json file
    from version 0.4:
        - removed dataset_analysis field
    """

    manifest_version: str = "0.5"
    simu_id: int
    topology: str
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    mitre_tags: Optional[List[WorkerMitreData]] = []
    date_dataset_created: datetime
    date_dataset_modified: Optional[datetime] = None
    logs: Dict[str, ResourceLog] = {}
    pcaps: Dict[str, ResourcePcap] = {}
    memory_dumps: Dict[str, ResourceMemoryDump] = {}
    redteam_reports: Dict[str, ResourceBase] = {}
    life_reports: Dict[str, ResourceLifeReport] = {}
    assets_reports: Dict[str, ResourceAssetsReport] = {}
    scenario: Optional[Union[Scenario, UnitAttack]] = None
    forensics: Optional[Dict[str, ResourceForensic]] = {}
    unit_attacks_played: List[str] = []
    scenario_profile: Optional[str] = ""

    # Ensures Model Validation is performed when a member is set after the creation of the object
    model_config = ConfigDict(validate_assignment=True)


class PartialManifest(BaseModel):
    name: str
    date_dataset_created: datetime
    date_dataset_modified: Optional[datetime] = None
    tags: List[str] = []
    mitre_tags: Optional[List[WorkerMitreData]] = []
    description: Optional[str] = None
    scenario_profile: Optional[str] = ""

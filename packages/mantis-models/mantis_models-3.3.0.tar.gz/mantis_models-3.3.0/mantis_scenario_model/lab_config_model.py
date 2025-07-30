# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from pydantic import BaseModel
from pydantic import NonNegativeInt

from .log_collector_model import LogCollectorLocation
from .log_collector_model import LogCollectorType


class CompromissionOs(str, Enum):
    windows10 = "windows10"
    windows7 = "windows7"
    ubuntu_gnome = "ubuntu_gnome"


class CompromissionBeacon(str, Enum):
    exe_reverse_api = "exe_reverse_api"
    win_reverse_api = "win_reverse_api"
    powershell_reverse_api = "powershell_reverse_api"
    linux_python_reverse_api = "linux_python_reverse_api"


class CompromissionVector(str, Enum):
    simple = "simple"  # user_activity + provisioning
    webmail = "webmail"


class CompromissionInfras(str, Enum):
    legacy = "legacy"  # api_control + nginx


class CompromissionProtocol(str, Enum):
    http = "http"
    https = "https"


class CompromissionPrivilege(int, Enum):
    user = 0
    admin = 1
    system = 2


class CompromissionConfig(BaseModel):
    auto_compromission: bool
    target_name: str
    beacon: Optional[CompromissionBeacon] = (
        None  # mandatory if auto_compromission = true
    )
    vector: Optional[CompromissionVector] = (
        None  # mandatory if auto_compromission = true
    )
    infras: Optional[CompromissionInfras] = (
        None  # mandatory if auto_compromission = true
    )
    communication_protocol: Optional[CompromissionProtocol] = (
        None  # mandatory if auto_compromission = true
    )
    privilege_level: Optional[CompromissionPrivilege] = (
        None  # mandatory if auto_compromission = true
    )


class ScenarioProfile(BaseModel):
    name: str
    topology_name: str
    compromission: CompromissionConfig
    production: bool


class LogCollectorInstanceLocation(BaseModel):
    location_type: LogCollectorLocation  # e.g. LogCollectorLocation.node_name
    value: str  # e.g. "Client1"


class LogCollectorInstanceOutput(BaseModel):
    instance_name: str  # e.g. logstash01
    collector_name: str  # e.g. logstash
    collector_type: LogCollectorType  # e.g. LogCollectorType.aggregator


class LogCollectorInstance(BaseModel):
    instance_name: str  # e.g. winlogbeat_windows10
    collector_name: str  # e.g. winlogbeat
    collector_type: LogCollectorType
    location: List[LogCollectorInstanceLocation]
    # input: List[LogCollectorInput] = []  # Currently not activated
    output: List[LogCollectorInstanceOutput] = []
    user_config: Dict = (
        {}
    )  # Where keys correspond to user config names (e.g. {"collector_ip_address": "172.16.0.1"})
    user_config_expert_mode: Dict = {}
    cpe_os_constraints: List[str] = []


class ContentType(str, Enum):
    KILLCHAIN = "KILLCHAIN"
    ATTACK = "ATTACK"
    TOPOLOGY = "TOPOLOGY"
    BASEBOX = "BASEBOX"
    BAS = "BAS"


class ScenarioExecutionMode(str, Enum):
    automatic = "automatic"
    step_by_step = "step_by_step"
    custom = "custom"  # Need step_waiting_list


class CompromissionConfigOverload(BaseModel):
    auto_compromission: Optional[bool] = None  # None = use scenario defaults
    target_name: Optional[str] = None  # None = use scenario defaults
    beacon: Optional[CompromissionBeacon] = None  # None = use scenario defaults
    vector: Optional[CompromissionVector] = None  # None = use scenario defaults
    infras: Optional[CompromissionInfras] = None  # None = use scenario defaults
    communication_protocol: Optional[CompromissionProtocol] = (
        None  # None = use scenario defaults
    )
    privilege_level: Optional[CompromissionPrivilege] = (
        None  # None = use scenario defaults
    )


class PublicAccessConfig(BaseModel):
    available: bool = False  # if a public link is available, false by default
    access_token: Optional[str] = None  # the access token from the lab creator
    refresh_token: Optional[str] = None  # the refresh token from the lab creator
    base_url: Optional[str] = None  # the url of the endpoint for the public app (eg public.mantis.local)


class LabConfig(BaseModel):
    config_name: str = "default"

    # --------------------- #
    # Content configuration #
    # --------------------- #
    content_type: Optional[ContentType] = None
    content_name: Optional[str] = None
    scenario_profile: Optional[str] = None

    # ----------------------- #
    # Execution configuration #
    # ----------------------- #
    random_waiting_minutes: Tuple[NonNegativeInt, NonNegativeInt] = (
        0,
        0,
    )  # Waiting range in minutes
    scenario_execution_mode: ScenarioExecutionMode = ScenarioExecutionMode.automatic
    step_waiting_list: List[str] = []
    # Define max duration of a simulation in seconds (55 minutes by
    # default). If set to 0, this means no timeout for the simulation.
    max_duration: int = 55 * 60

    # ----------------------- #
    # Defensive configuration #
    # ----------------------- #
    net_capture: Optional[bool] = (
        False  # Tells if PCAP will be generated in datasets and traffic mirrored to potential probes
    )
    forensic_artifacts: Optional[bool] = (
        False  # Tells if forensic artifacts will be generated in datasets
    )
    create_dataset: Optional[bool] = False  # Tells if a dataset will be created
    log_collectors: List[LogCollectorInstance] = []

    # --------------------------- #
    # Public access configuration #
    # --------------------------- #
    public_access: PublicAccessConfig = (
        PublicAccessConfig(available=False)  # By default, it should be at False
    )

    # ------------------ #
    # Misc configuration #
    # ------------------ #
    internet_connectivity: Optional[bool] = False
    user_activity_background: Optional[bool] = (
        False  # Tells to produce background random user activities on desktops
    )
    compromission_overload: Optional[CompromissionConfigOverload] = (
        None  # None = use default compromission in scenario.yaml
    )

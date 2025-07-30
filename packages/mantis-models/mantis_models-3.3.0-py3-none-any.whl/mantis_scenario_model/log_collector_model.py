# -*- coding: utf-8 -*-
from enum import Enum
from pathlib import Path
from typing import List
from typing import Optional

import yaml
from mantis_common_model.cpe import CpeListModel
from pydantic import BaseModel


class LogCollectorStatus(str, Enum):
    development = "development"
    production = "production"


class LogCollectorLocation(str, Enum):
    node_name = "node_name"  # Allows to deploy a collector on specific node names (e.g. "Client1")
    new_node = "new_node"  # Allows to deploy a collector on a new node (e.g. a dedicated 'logstash' node)
    system_type = "system_type"  # Allows to deploy a collector on a specific system (e.g. "windows")
    operating_system = "operating_system"  # Allows to deploy a collector on a specific Windows version (e.g. "Windows 10")
    external = "external"  # Describes an external SIEM, XDR or log collector


class LogCollectorType(str, Enum):
    agent = "agent"
    aggregator = "aggregator"
    probe = "probe"
    visualization = "visualization"
    external = "external"
    # custom = "custom"  # Not yet supported


class LogCollectorIntConstraints(BaseModel):
    """
    Additional constraints for a log collector user config with an int type
    """

    min_value: int  # used to specify the minimum allowed value
    max_value: int  # used to specify the maximum allowed value


class LogCollectorUserConfig(BaseModel):
    name: str  # e.g. "collector_ip_address"
    description: str  # e.g. "IP address of the log collector."
    type: str  # Python primary type: either "str", "int", or "bool"
    constraints: Optional[LogCollectorIntConstraints] = (
        None  # Constraints linked to the type, None by default
    )
    default: str  # Default value
    required: bool  # Tells if the config variable is mandatory


class LogCollector(BaseModel):
    collector_name: str  # e.g. winlogbeat
    displayed_name: str  # e.g. "Winlogbeat"
    collector_type: LogCollectorType
    description: str

    documentation_link: Optional[str] = None  # Documentation link

    status: LogCollectorStatus

    available_locations: List[LogCollectorLocation]
    available_output_collectors: List[str]  # A list of collector_name is expected here

    mandatory_inputs: List[str]  # A list of collector_name is expected here
    # This is the list of inputs needed in order for this log collector to work

    cpe_os_constraints: CpeListModel
    user_config: List[LogCollectorUserConfig]
    user_config_expert_mode: List[LogCollectorUserConfig]

    @staticmethod
    def from_yaml(collector_name: str) -> "LogCollector":
        """
        Return all the cpes for the current log collector
        """
        log_collectors_path = (
            Path("/cyber-range-catalog") / "provisioning" / "log_collectors"
        )
        if log_collectors_path.exists() is False:
            raise Exception(f"The folder {log_collectors_path} does not exist")
        if log_collectors_path.is_dir() is False:
            raise Exception(f"The folder {log_collectors_path} is not a folder")

        log_collector_config_path: Path = (
            log_collectors_path / collector_name / "config.yaml"
        )
        if log_collector_config_path.is_file() is False:
            raise Exception(
                f"The log collector YAML config file '{log_collector_config_path}' is missing"
            )

        log_collector_config_dict: dict = {}
        with log_collector_config_path.open("r") as file:
            log_collector_config_dict = yaml.safe_load(file)

        return LogCollector(**log_collector_config_dict)

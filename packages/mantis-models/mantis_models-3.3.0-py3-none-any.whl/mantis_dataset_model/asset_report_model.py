# -*- coding: utf-8 -*-
from enum import Enum
from typing import List
from typing import Optional

from mantis_scenario_model.common import RoleEnum
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class OSFamily(str, Enum):
    LINUX = "linux"
    WINDOWS = "windows"


class MachineType(str, Enum):
    virtual_machine = "virtual_machine"
    docker = "docker"


class NetworkInterfaceInfos(BaseModel):
    ipv4: str
    ipv4_runtime: str = Field(pattern=r"[0-9]+(.[0-9]+){3}")  # 192.168.44.11 for example
    mac: str = Field(
        pattern=r"[a-zA-Z0-9]+(:[a-zA-Z0-9]+){5}"
    )  # 00:60:52:eb:40:0c for example
    fqdn_list: List[str]


class AssetNode(BaseModel):
    """
    AssetNode
    We specify constraints about different fields so that the validation fails early
    if the nodes are not valid.
    """

    name: str = Field(min_length=1)
    type: MachineType
    roles: List[RoleEnum]
    network_interfaces: List[NetworkInterfaceInfos]
    os: Optional[str] = Field(default=None, min_length=1)
    os_family: Optional[OSFamily] = Field(default=None, min_length=1)
    os_version: Optional[str] = Field(default=None, min_length=1)
    cpe: Optional[str] = Field(default=None, min_length=3)
    base_image: Optional[str] = Field(
        default=None, pattern=r"[\w\-\.]+:[\w\-\.]+"
    )  # 1587_000_004-nginx_server:latest for example

    model_config = ConfigDict(use_enum_values=False)


class AssetReportModel(BaseModel):
    asset_nodes: List[AssetNode]

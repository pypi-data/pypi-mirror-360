# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
from enum import Enum
import json
import os
from typing import List
from typing import TypeVar
from typing import Optional
from typing import Union
from datetime import datetime
from datetime import timedelta

from pydantic import ConfigDict
from pydantic import BaseModel
from pydantic import Field
from pydantic.types import StringConstraints
from ruamel.yaml import YAML
from ruamel.yaml import yaml_object
from typing_extensions import Annotated

yaml = YAML

PositiveEqualInt = Annotated[int, Field(ge=0)]

NotEmptyStr = Annotated[str, StringConstraints(min_length=1)]

T = TypeVar("T")

NotEmptyList = Annotated[List[T], Field(min_length=1)]

yaml = YAML()  # type: ignore


@yaml_object(yaml)
class RoleEnum(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"
    ANALYST = "analyst"
    AD = "ad"
    ADCS = "adcs"  # Windows ADCS role
    DFS = "dfs"  # Windows DFS role
    FILE_SERVER = "file_server"
    WEB_SERVER = "web_server"
    INTERNET = "internet"
    SQUID = "squid"
    MAIL_SERVER = "mail_server"
    MONITORING = "monitoring"
    LOG_COLLECTOR = "log_collector"
    PROBE = "probe"
    REDTEAM_INFRASTRUCTURE = "redteam_infrastructure"
    ROUTER = "router"
    FIREWALL = "firewall"
    ROUTER_FIREWALL = "router_firewall"
    DNS = "dns"
    DATABASE = "database"
    OTHER = "other"

    @staticmethod
    def from_str(label: str) -> str:  # noqa: C901
        if label == "client":
            return RoleEnum.CLIENT
        if label == "admin":
            return RoleEnum.ADMIN
        if label == "analyst":
            return RoleEnum.ANALYST
        if label == "ad":
            return RoleEnum.AD
        if label == "adcs":
            return RoleEnum.ADCS
        if label == "dfs":
            return RoleEnum.DFS
        if label == "file_server":
            return RoleEnum.FILE_SERVER
        if label == "web_server":
            return RoleEnum.WEB_SERVER
        if label == "internet":
            return RoleEnum.INTERNET
        if label == "squid":
            return RoleEnum.SQUID
        if label == "mail_server":
            return RoleEnum.MAIL_SERVER
        if label == "monitoring":
            return RoleEnum.MONITORING
        if label == "log_collector":
            return RoleEnum.LOG_COLLECTOR
        if label == "probe":
            return RoleEnum.PROBE
        if label == "redteam_infrastructure":
            return RoleEnum.REDTEAM_INFRASTRUCTURE
        if label == "router":
            return RoleEnum.ROUTER
        if label == "firewall":
            return RoleEnum.FIREWALL
        if label == "router_firewall":
            return RoleEnum.ROUTER_FIREWALL
        if label == "dns":
            return RoleEnum.DNS
        if label == "database":
            return RoleEnum.DATABASE
        if label == "other":
            return RoleEnum.OTHER
        raise NotImplementedError

    @classmethod
    def to_yaml(cls, representer, node):  # noqa: ANN001, ANN206
        return representer.represent_scalar("!Role", "{}".format(node._value_))


class Timestamps(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None

    model_config = ConfigDict(ser_json_timedelta="float")


##
##  MITRE ATT&CK related data
##


# Load techniques and tactics
mitre_json_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mitre", "mitre.json"
)
mitre_attack_data = {}
with open(mitre_json_file_path, "r") as f:
    mitre_attack_data = json.load(f)

if not mitre_attack_data:
    raise Exception("File mitre.json was not found.")


class Empty(BaseModel):
    ...

    # Do not allow extract inputs
    model_config = ConfigDict(extra="forbid")


class MitreIdName(BaseModel):
    id: str
    name: str


class Implementation(BaseModel):
    id: str


class WorkerMitreData(BaseModel):
    technique: MitreIdName
    subtechnique: Union[MitreIdName, Empty]
    tactics: List[MitreIdName]
    implementation: Optional[Implementation] = None

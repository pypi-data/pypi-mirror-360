# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
import re
from enum import Enum
from ipaddress import ip_address
from ipaddress import ip_interface
from ipaddress import IPv4Address
from ipaddress import IPv4Interface
from ipaddress import IPv6Address
from ipaddress import IPv6Interface
from typing import Any
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import PositiveInt
from pydantic_core import core_schema
from ruamel.yaml import YAML
from ruamel.yaml import yaml_object

from .common import NotEmptyStr
from .common import RoleEnum

# from .common import NotEmptyList

yaml = YAML()


@yaml_object(yaml)
class TypeEnum(str, Enum):
    VIRTUAL_MACHINE = "virtual_machine"
    DOCKER = "docker"
    PHYSICAL_MACHINE = "physical_machine"
    HOST_MACHINE = "host_machine"
    ROUTER = "router"
    SWITCH = "switch"
    PHYSICAL_GATEWAY = "physical_gateway"

    @staticmethod
    def from_str(label: str) -> str:
        if label == "@yaml_object(yaml)":
            return TypeEnum.VIRTUAL_MACHINE
        if label == "docker":
            return TypeEnum.DOCKER
        if label == "physical_machine":
            return TypeEnum.PHYSICAL_MACHINE
        if label == "host_machine":
            return TypeEnum.HOST_MACHINE
        if label == "router":
            return TypeEnum.ROUTER
        if label == "switch":
            return TypeEnum.SWITCH
        if label == "physical_gateway":
            return TypeEnum.PHYSICAL_GATEWAY
        raise NotImplementedError

    @classmethod
    def to_yaml(cls, representer, node):  # noqa: ANN001, ANN206
        return representer.represent_scalar("!TypeEnum", "{}".format(node._value_))


def check_roles(roles: Optional[Set[RoleEnum]]) -> Optional[Set[RoleEnum]]:
    if roles is not None and len(roles) == 0:
        raise ValueError("'roles' field must not be empty")
    return roles


@yaml_object(yaml)
class RouteType:
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler) -> core_schema.CoreSchema:
        return core_schema.with_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(
            cls, value: str, info  # noqa: ANN101, ANN102 N805 TODO
    ) -> Tuple[Union[IPv4Interface, IPv6Interface], Union[IPv4Address, IPv6Address]]:
        if not isinstance(value, str):
            raise TypeError("string required")
        m = re.fullmatch("(.+) -> (.+)", value)
        if not m:
            raise ValueError("invalid route format")
        return ip_interface(m[1].strip()), ip_address(m[2].strip())


@yaml_object(yaml)
class Node(BaseModel):
    type: TypeEnum
    name: NotEmptyStr
    active: bool = True
    hidden: bool = False

    model_config = ConfigDict(use_enum_values=True)


@yaml_object(yaml)
class VirtualMachine(Node):
    basebox_id: Optional[NotEmptyStr] = None
    basebox_vagrant: Optional[NotEmptyStr] = None
    memory_size: Optional[PositiveInt] = 1024
    nb_proc: Optional[PositiveInt] = 1
    roles: Set[RoleEnum]

    # validators
    _check_roles = field_validator("roles")(check_roles)

    @field_validator("basebox_id")
    def check_id_or_vagrant(
        cls, basebox_id: str, values  # noqa: ANN101, N805, ANN001 TODO
    ) -> str:
        if 'active' in values.data is True:
            if "basebox_vagrant" not in values.data and not basebox_id:
                raise ValueError("either basebox_id or basebox_vagrant is required")
        return basebox_id

    @field_validator("basebox_id")
    def check_id_and_vagrant(
        cls, basebox_id: str, values  # noqa: ANN101, N805, ANN001 TODO
    ) -> str:  # noqa: ANN101, N805 TODO
        if "basebox_vagrant" in values.data and basebox_id:
            raise ValueError(
                "basebox_id and basebox_vagrant can not be present together"
            )
        return basebox_id


@yaml_object(yaml)
class Volumes(BaseModel):
    host_path: str
    bind: str
    writable: bool


@yaml_object(yaml)
class Docker(Node):
    base_image: NotEmptyStr
    memory_size: Optional[PositiveInt] = 1024
    nb_proc: Optional[PositiveInt] = 1
    roles: Set[RoleEnum]
    volumes: Optional[List[Volumes]] = None

    # validators
    _check_roles = field_validator("roles")(check_roles)


@yaml_object(yaml)
class PhysicalMachine(Node):
    roles: Optional[Set[RoleEnum]] = None

    # validators
    _check_roles = field_validator("roles")(check_roles)


@yaml_object(yaml)
class HostMachine(Node):
    pass


@yaml_object(yaml)
class Router(Node):
    # routes: Optional[NotEmptyList[RouteType]]
    # TODO does not work as if, so we put ANY
    routes: Optional[Any] = None


@yaml_object(yaml)
class Switch(Node):
    pass


@yaml_object(yaml)
class PhysicalGateway(Node):
    pass

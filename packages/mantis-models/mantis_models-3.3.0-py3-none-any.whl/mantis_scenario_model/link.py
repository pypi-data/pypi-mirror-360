# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
from typing import Literal
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic import IPvAnyInterface
from pydantic import model_validator
from ruamel.yaml import YAML
from ruamel.yaml import yaml_object

from .node import Node
from .node import TypeEnum

yaml = YAML()


@yaml_object(yaml)
class NetworkConfig(BaseModel):
    ip: Optional[Union[IPvAnyInterface, Literal["dynamic"]]] = None
    # If the ip is not provided it should be dynamic, however it can be left empty in
    # the yaml file
    mac: Optional[str] = Field(pattern="^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$", default=None)
    dhcp: Optional[bool] = None
    dhcp_nameserver: Optional[str] = None
    dhcp_lease: Optional[int] = None
    dhcp_router: Optional[str] = None

    @classmethod
    def to_yaml(cls, representer, node):  # noqa: ANN001, ANN206
        return representer.represent_scalar("!NetworkConfig", "u{.ip}".format(node))


@yaml_object(yaml)
class Link(BaseModel):
    switch: Node
    node: Node
    params: NetworkConfig

    @field_validator("switch")
    def check_is_switch(cls, v: Node) -> Node:  # noqa: ANN101, N805 TODO
        if v.type != TypeEnum.SWITCH:
            raise ValueError(f"must be of {TypeEnum.SWITCH} type")
        return v

    @field_validator("node")
    def check_is_not_switch(cls, v: Node) -> Node:  # noqa: ANN101, N805 TODO
        if v.type == TypeEnum.SWITCH:
            raise ValueError(f"must not be of {TypeEnum.SWITCH} type")
        return v

    @model_validator(mode="after")
    def check_nodes_consistency(
            self
    ) -> 'Link':
        switch = self.switch
        node = self.node
        if (
            switch.type == TypeEnum.VIRTUAL_MACHINE
            and node.type == TypeEnum.VIRTUAL_MACHINE
        ):
            raise ValueError("It is not possible to link two virtual machine nodes")
        return self

# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
import tempfile
from pathlib import Path
from typing import Dict
from typing import List
from typing import Union

from pydantic import BaseModel
from pydantic import field_validator
from ruamel.yaml import YAML
from ruamel.yaml import yaml_object

from .common import NotEmptyList
from .common import NotEmptyStr
from .link import Link
from .node import Docker
from .node import HostMachine
from .node import Node
from .node import PhysicalGateway
from .node import PhysicalMachine
from .node import Router
from .node import Switch
from .node import VirtualMachine

yaml = YAML()

NodeTypes = Union[
    VirtualMachine,
    Docker,
    Router,
    Switch,
    PhysicalGateway,
    PhysicalMachine,
    HostMachine,
]


@yaml_object(yaml)
class Topology(BaseModel):
    name: NotEmptyStr
    nodes: List[NodeTypes]
    links: NotEmptyList[Link]

    @field_validator("nodes")
    def check_nodes(cls, v: List[Node]) -> List[Node]:  # noqa: ANN101, N805 TODO
        names = [node.name for node in v]
        if len(names) != len(set(names)):
            raise ValueError("Names of the node list must be unique")
        return v

    @staticmethod
    def from_yaml_string(value: str) -> "Topology":
        loader = YAML(typ="safe")
        return Topology(**loader.load(value))

    @staticmethod
    def from_yaml_file(path: Path) -> "Topology":
        return Topology.from_yaml_string(path.read_text())

    def to_yaml_string(self) -> str:
        """
        Transform a topology to a yaml string
        """
        # Convert to dict and exclude null values
        topo_as_dict: Dict = self.dict(exclude_none=True)

        # Convert the ips into string
        for link in topo_as_dict["links"]:
            if "params" in link:
                if "ip" in link["params"]:
                    link["params"]["ip"] = str(link["params"]["ip"])

        # Convert the roles from set to list
        for node in topo_as_dict["nodes"]:
            if "roles" in node:
                node["roles"] = list(node["roles"])  # type: ignore  # noqa: F821

        # dump it to a temp file and reload it as yaml
        yaml = YAML(typ="rt")
        with tempfile.TemporaryFile() as fp:
            yaml.dump(topo_as_dict, fp)
            fp.seek(0)
            topo_yaml = yaml.load(fp)

        # Set anchor in nodes
        for node in topo_yaml["nodes"]:
            node.anchor.value = node["name"]
            node.anchor.always_dump = True

        # Add anchors in links
        for link in topo_yaml["links"]:
            if "switch" in link:
                # find node
                for node in topo_yaml["nodes"]:
                    if node["name"] == link["switch"]["name"]:
                        link["switch"] = node
                        break
            if "node" in link:
                # find node
                for node in topo_yaml["nodes"]:
                    if node["name"] == link["node"]["name"]:
                        link["node"] = node
                        break

        # dump to file to read it
        with tempfile.NamedTemporaryFile() as fp:
            yaml.dump(topo_yaml, fp)
            fp.seek(0)
            yaml_str = Path(fp.name).read_text()

        return yaml_str

    def to_yaml_file(self, filename: str) -> None:
        """
        Write the topology to a file with a yaml format
        """
        yaml_str = self.to_yaml_string()
        with open(filename, "w") as output_file:
            output_file.write(yaml_str)

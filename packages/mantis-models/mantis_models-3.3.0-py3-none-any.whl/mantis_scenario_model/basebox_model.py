# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from mantis_common_model.cpe import CpeListModel
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import conint
from pydantic import Field
from ruamel.yaml import YAML
from ruamel.yaml import yaml_object

from .common import NotEmptyStr
from .common import RoleEnum

yaml = YAML()


@yaml_object(yaml)
class Basebox(BaseModel):
    """
    Description of a basebox
    """

    id: Optional[NotEmptyStr] = Field(default=None)
    description: NotEmptyStr
    operating_system: NotEmptyStr
    system_type: NotEmptyStr
    language: NotEmptyStr
    installation_date: datetime
    role: RoleEnum
    username: Optional[NotEmptyStr] = Field(default=None)
    password: Optional[NotEmptyStr] = Field(default=None)
    admin_username: Optional[NotEmptyStr] = Field(default=None)
    admin_password: Optional[NotEmptyStr] = Field(default=None)
    nb_proc: conint(ge=1)  # type: ignore
    memory_size: conint(ge=256)  # type: ignore
    cpes: Optional[CpeListModel] = Field(default=None)
    sha256sum: NotEmptyStr
    changelog: Optional[List[Dict[NotEmptyStr, NotEmptyStr]]] = Field(default=None)
    storage_bus: Optional[NotEmptyStr] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)  # mandatory to use "model_validate" class methode

    @staticmethod
    def from_yaml_string(value: str) -> "Basebox":
        """
        Create a basebox from a yaml description in string
        :param value: the yaml representation
        :return: the Basebox
        """
        loader = YAML(typ="rt")
        return Basebox(**loader.load(value))

    @staticmethod
    def from_yaml_file(path: Path) -> "Basebox":
        """
        Create a basebox from a yaml file
        :param path: the path of the file to read
        :return: the Basebox
        """
        return Basebox.from_yaml_string(path.read_text())

    @staticmethod
    def from_yaml(value: Dict[str, Any]) -> "Basebox":
        """
        Create a basebox from a yaml description in a dict (obtained from a call to YAML().load())

        :param value: the yaml representation
        :return: the Basebox
        """
        return Basebox(**value)

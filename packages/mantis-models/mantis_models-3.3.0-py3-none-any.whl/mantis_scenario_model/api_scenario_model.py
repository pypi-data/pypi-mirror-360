# -*- coding: utf-8 -*-
from typing import List
from typing import Optional

from mantis_common_model.pagination import BaseListReply
from mantis_scenario_model.lab_model import Lab
from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Annotated


## Data structure to hold lab list
class LabListFilter(BaseModel):
    """Field parameters for labs filtering"""

    owner: Annotated[
        Optional[str], Field(description="The user who created the lab")
    ] = None
    type: Annotated[Optional[str], Field(description="The type of lab")] = None
    status: Annotated[Optional[str], Field(description="The status of the lab")] = (
        None
    )


class LabListReply(BaseListReply):
    data: List[Lab] = []


## Data structure to hold paused status API response
class PausedStatus(BaseModel):
    step: Optional[str] = None  # The current step in the scenario where the pause occurs
    is_before_step: Optional[bool] = None  # Indicates if the paused occurs before (True) or after the step (False)


## Data structure to hold remote access info API response
class CredentialRemoteAccess(BaseModel):
    login: str
    password: str
    privilege: str


class NodeRemoteAccess(BaseModel):
    name: str
    http_url: Optional[str] = None
    spice_config: Optional[str] = None
    credentials: List[CredentialRemoteAccess] = []


class RemoteAccess(BaseModel):
    nodes: List[NodeRemoteAccess] = []

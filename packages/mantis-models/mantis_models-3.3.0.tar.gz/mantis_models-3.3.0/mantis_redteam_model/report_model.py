# -*- coding: utf-8 -*-
from enum import Enum
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import field_validator

from .unit_attack_model import UserActivity
from .unit_attack_model import Worker


class BaseNodeInfo(BaseModel):
    pass


class TargetNodeInfo(BaseNodeInfo):
    ip: str


class AttackNodeInfo(BaseNodeInfo):
    ip: str
    type_session: str
    privilege_level: str
    session_id: str
    username: str


class AttackReportType(str, Enum):
    ATTACK_REPORT = "ATTACK_REPORT"
    USER_ACTIVITY_REPORT = "USER_ACTIVITY_REPORT"


class NodeType(str, Enum):
    TARGET_NODE = "TARGET_NODE"
    ATTACK_SESSION = "ATTACK_SESSION"


class Command(BaseModel):
    encoded_command: str
    decoded_command: str
    binary: Optional[List[str]] = None


class AttackProcessGraph(BaseModel):
    powershell: Optional[Command] = None
    sh: Optional[Command] = None
    download: Optional[str] = None


class BaseNode(BaseModel):
    node_type: NodeType
    node_info: Union[AttackNodeInfo, TargetNodeInfo]

    class Config:
        use_enum_values = True  # Utilise directement les valeurs d'énumération pour les comparaisons
        smart_union = True  # Permet à Pydantic de gérer l'union correctement

    @field_validator("node_info", mode="before")
    @classmethod
    def validate_node_info(cls, value, info):
        if isinstance(value, (TargetNodeInfo, AttackNodeInfo)):
            return value  # La valeur est déjà une instance correcte

        node_type = info.data.get("node_type")  # Récupération du node_type

        if node_type == NodeType.TARGET_NODE:
            return TargetNodeInfo(**value)
        elif node_type == NodeType.ATTACK_SESSION:
            return AttackNodeInfo(**value)

        raise ValueError("Invalid node_type or node_info mismatch")


class TargetNode(BaseNode):
    node_info: TargetNodeInfo


class AttackNode(BaseNode):
    node_info: AttackNodeInfo
    attack_process_graph: Optional[List[AttackProcessGraph]] = None


class ReportModel(BaseModel):
    id: int
    source_ids: Optional[List[int]]
    attack_type: AttackReportType
    status: str
    started_date: str
    last_update: str
    target_nodes: List[BaseNode]
    output: List[
        dict
    ]  # TODO: Make a real output model with all possibles topic outputs

    @classmethod
    def create_node(
        cls,
        node_type: NodeType,
        attack_process_graph: List[AttackProcessGraph] = [],
        **kwargs
    ) -> dict:
        if node_type == NodeType.TARGET_NODE:
            resultTargetNode = TargetNode(node_type=node_type, node_info=TargetNodeInfo(**kwargs))
            return resultTargetNode.dict()
        elif node_type == NodeType.ATTACK_SESSION:
            resultAttackNode = AttackNode(
                node_type=node_type,
                node_info=AttackNodeInfo(**kwargs),
                attack_process_graph=attack_process_graph
            )
            return resultAttackNode.dict()

        else:
            raise ValueError("Invalid node type")


class AttackReport(ReportModel):
    worker: Worker


class UserActivityReport(ReportModel):
    user_activity: UserActivity

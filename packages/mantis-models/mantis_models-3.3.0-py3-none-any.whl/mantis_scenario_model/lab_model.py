# -*- coding: utf-8 -*-
from enum import Enum
from typing import Optional

from mantis_scenario_model.lab_config_model import ContentType
from pydantic import BaseModel


class ScenarioExecutionStatus(str, Enum):
    created = "CREATED"  # The task has been created but is not yet
    # totally initialized (some metadata still
    # need to be created)
    pending = "PENDING"  # The runner (Cyber Range) has not been found yet
    runner_setup = (
        "RUNNER_SETUP"  # Runner initialization (Cyber Range APIs waiting to be up)
    )
    scenario_creation = "SCENARIO_CREATION"  # Simulation is starting
    scenario_setup = (
        "SCENARIO_SETUP"  # Scenario provisioning and setup (network capture, etc.)
    )
    scenario_execution = (
        "SCENARIO_EXECUTION"  # Proper scenario exection (life and attacks)
    )
    scenario_teardown = "SCENARIO_TEARDOWN"  # After scenario execution (forensic, etc.)
    scenario_finished = "SCENARIO_FINISHED"  # Scenario has been successfully finished
    runner_teardown = "RUNNER_TEARDOWN"  # Runner is terminating
    completed = "COMPLETED"  # Scenario has been successfully finished and runner is not available anymore
    cancelled = "CANCELLED"  # Scenario has been cancelled
    error = "ERROR"  # Scenario triggered an internal error
    pause = "PAUSE"  # Scenario pause


class ScenarioExecutionStopped(Exception):
    pass


class Lab(BaseModel):
    runner_id: str
    """Lab UUID."""

    status: ScenarioExecutionStatus
    """Lab status."""

    lab_creation_timestamp: float
    """Timestamp of lab creation step."""

    lab_start_timestamp: Optional[float]
    """Timestamp of lab starting step."""

    lab_content_end_timestamp: Optional[float]
    """Timestamp of end of content execution within the lab."""

    lab_end_timestamp: Optional[float]
    """Timestamp of end of lab execution."""

    content_type: ContentType
    """Content executed inside the lab (basebox, topology, attack or killchain)."""

    name: str
    """Name of the lab."""

    created_by: str
    """UUID of the user that created the lab."""

    group_id: str
    """UUID of the group in which the lab is executed."""

    worker_id: str
    """UUID of the worker that executes the lab."""

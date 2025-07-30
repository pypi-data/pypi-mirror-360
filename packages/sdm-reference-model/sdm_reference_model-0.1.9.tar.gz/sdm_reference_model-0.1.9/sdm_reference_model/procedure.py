from __future__ import annotations
from typing import Literal, Optional, List

from enum import Enum

from aas_pydantic import (
    AAS,
    Submodel,
    SubmodelElementCollection,
)
from sdm_reference_model.processes import ProcessAttributes
from sdm_reference_model.distribution import (
    ABSTRACT_REAL_DISTRIBUTION,
    DistributionTypeEnum,
)

ProcessAttributes.model_rebuild()


class ProcedureTypeEnum(str, Enum):
    """
    Enum to describe the type of a procedure.
    """

    PRODUCTION = "Production"
    TRANSPORT = "Transport"
    LOADING = "Loading"
    SETUP = "Setup"
    BREAKDOWN = "Breakdown"
    MAINTENANCE = "Maintenance"
    STAND_BY = "StandBy"
    WAITING = "Waiting"
    OFF = "Off"
    NON_SCHEDULED = "NonScheduled"
    ORDER_RELEASE = "OrderRelease"
    ORDER_SHIPPING = "OrderShipping"


class ActivityTypeEnum(str, Enum):
    """
    Enum to describe the type of an activity.
    """

    START = "Start"
    END = "End"
    START_INTERUPT = "StartInterupt"
    END_INTERUPT = "EndInterupt"


class Event(SubmodelElementCollection):
    """
    The Event class represents an event in the execution of a procedure. It contains the time of the event, the resource that executed the event, the procedure that was executed, the activity that was executed, the product that was produced, and whether the event was successful or not.

    Args:
        time (float): The time of the event.
        resource_id (str): The id of the resource that executed the event.
        procedure_id (str): The id of the procedure that was executed.
        procedure_type (ProcedureTypeEnum): The type of the procedure that was executed.
        activity (str): The activity that was executed.
        product_id (Optional[str]): The id of the product that was produced.
        expected_end_time (Optional[float]): The expected end time of the event.
        actual_end_time (Optional[float]): The actual end time of the event.
        success (Optional[bool]): Whether the event was successful or not.
    """

    time: str
    resource_id: str
    procedure_id: str
    procedure_type: ProcedureTypeEnum
    activity: ActivityTypeEnum
    product_id: Optional[str] = None
    expected_end_time: Optional[str] = None
    actual_end_time: Optional[str] = None
    success: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "time": "2022-01-01T00:00:00Z",
                    "resource_id": "resource_1012",
                    "procedure_id": "procedure_1",
                    "procedure_type": "Production",
                    "activity": "Start",
                    "product_id": "product_1",
                    "expected_end_time": "2022-01-01T00:10:00Z",
                    "actual_end_time": "2022-01-01T00:09:00Z",
                    "success": True,
                },
            ]
        }
    }


class ExecutionModel(Submodel):
    """
    The ExecutionModel represents all planned (scheduled) and performed (executed) execution of a process. It contains the schedule of the process, and the execution log of the process.

    Args:
        id (str): The id of the execution model.
        description (Optional[str]): The description of the execution model.
        id_short (Optional[str]): The short id of the execution model.
        semantic_id (Optional[str]): The semantic id of the execution model.
        schedule (List[Event]): The schedule of the procedure.
        execution_log (List[Event]): The execution log of the procedure.
    """

    schedule: Optional[List[Event]] = None
    execution_log: Optional[List[Event]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "execution_model_1",
                    "description": "Execution model for procedure 1",
                    "id_short": "proc_1_exec_model",
                    "semantic_id": "proc_1_exec_model",
                    "schedule": [
                        {
                            "time": "2022-01-01T00:00:00Z",
                            "resource_id": "resource_1012",
                            "procedure_id": "procedure_1",
                            "procedure_type": "Production",
                            "activity": "Start",
                            "product_id": "product_1",
                            "expected_end_time": "2022-01-01T00:10:00Z",
                            "actual_end_time": "2022-01-01T00:09:00Z",
                            "success": True
                        }
                    ],
                    "execution_log": [
                        {
                            "time": "2022-01-01T00:00:00Z",
                            "resource_id": "resource_1012",
                            "procedure_id": "procedure_1",
                            "procedure_type": "Production",
                            "activity": "Start",
                            "product_id": "product_1",
                            "expected_end_time": "2022-01-01T00:10:00Z",
                            "actual_end_time": "2022-01-01T00:09:00Z",
                            "success": True
                        }
                    ]
                }
            ]
        }
    }


class TransportTime(SubmodelElementCollection):
    """
    This class represents a transport time where the required time for transport between and origin and a target is specified.

    Args:
        origin_id (str): Id of the resource where the transport starts
        target_id (str): Id of the resource where the transport ends
        transport_time (float): Time needed for the transport in seconds.
    """

    origin_id: str
    target_id: str
    transport_time: float

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "origin_id": "resource_1012",
                    "target_id": "resource_1013",
                    "transport_time": 10.0,
                }
            ]
        }
    }


class TimeModel(Submodel):
    """
    Submodel containing parameters to represent the timely duration of a procedure. All times are specified in minutes unless otherwise stated.

    Args:
        id (str): The id of the time model.
        description (Optional[str]): The description of the time model.
        id_short (Optional[str]): The short id of the time model.
        semantic_id (Optional[str]): The semantic id of the time model.
        type_ (Literal["sequential", "distribution", "distance_based"]): The type of the time model.
        sequence (Optional[List[float]]): The sequence of timely values (only for sequential time models).
        repeat (Optional[bool]): Whether the sequence is repeated or not (only for sequential time models).
        distribution_type (Optional[str]): The name of the distribution (e.g. "normal", "exponential", "weibull", "lognormal", "gamma", "beta", "uniform", "triangular", "discrete") (only for distribution time models).
        distribution_parameters (Optional[List[float]]): The parameters of the distribution (1: location, 2: scale, 3 and 4: shape) (only for distribution time models).
        speed (Optional[float]): The speed of the resource (only for distance-based time models) in m / s.
        rotation_speed (Optional[float]): The rotation speed of the resource (only for distance-based time models) in degree / s.
        reaction_time (Optional[float]): The reaction time of the resource (only for distance-based time models) in s.
        acceleration (Optional[float]): The acceleration of the resource (only for distance-based time models) in m^2/s.
        deceleration (Optional[float]): The deceleration of the resource (only for distance-based time models) in m^2/s.
    """

    type_: Literal["sequential", "distribution", "distance_based"]
    sequence: Optional[List[float]] = None
    repeat: Optional[bool] = None
    distribution_type: Optional[DistributionTypeEnum] = None
    distribution_parameters: Optional[ABSTRACT_REAL_DISTRIBUTION] = None
    speed: Optional[float] = None
    rotation_speed: Optional[float] = None
    reaction_time: Optional[float] = None
    acceleration: Optional[float] = None
    deceleration: Optional[float] = None
    transport_times: Optional[List[TransportTime]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "time_model_example",
                    "description": "Example of a time model submodel.",
                    "id": "time_model_example",
                    "type_": "sequential",
                    "sequence": [1.0, 2.0, 3.0],
                    "repeat": True,
                    "distribution_type": "normal",
                    "distribution_parameters": [0.0, 1.0],
                    "speed": 1.0,
                    "rotation_speed": 1.0,
                    "reaction_time": 1.0,
                    "acceleration": 1.0,
                    "deceleration": 1.0,
                },
                {
                    "id_short": "transport_procedure_time_model",
                    "description": "Time model of transport procedure",
                    "id": "transport_procedure_time_model",
                    "semantic_id": "",
                    "type_": "distance_based",
                    "sequence": None,
                    "repeat": None,
                    "distribution_type": None,
                    "distribution_parameters": None,
                    "speed": 1.0,
                    "rotation_speed": 30.0,
                    "reaction_time": 5.0,
                    "acceleration": -1.0,
                    "deceleration": None,
                    "transport_times": [
                        {
                            "id_short": "transport_procedure_transport_time_resource_3000_resource_resource_3000_resource",
                            "description": "",
                            "semantic_id": "",
                            "origin_id": "resource_3000_resource",
                            "target_id": "resource_3000_resource",
                            "transport_time": 0.0,
                        },
                        {
                            "id_short": "transport_procedure_transport_time_resource_3000_resource_resource_3001_resource",
                            "description": "",
                            "semantic_id": "",
                            "origin_id": "resource_3000_resource",
                            "target_id": "resource_3001_resource",
                            "transport_time": 35.0,
                        },
                    ],
                },
                {
                    "id_short": "task_1147_process_time_1218_time_model",
                    "description": "Time model of procedure of task task_1147 with name TTN01_H_Servodeckel_Montage of resource resource_1012 with process time process_time_1218",
                    "id": "task_1147_process_time_1218_time_model",
                    "semantic_id": "",
                    "type_": "distribution",
                    "sequence": None,
                    "repeat": None,
                    "distribution_type": "normal",
                    "distribution_parameters": {
                        "id_short": "task_1147_process_time_1218_distribution_parameters",
                        "description": "",
                        "semantic_id": "",
                        "type": "normal",
                        "mean": 36.0,
                        "std": 3.6,
                    },
                    "speed": None,
                    "rotation_speed": None,
                    "reaction_time": None,
                    "acceleration": None,
                    "deceleration": None,
                    "transport_times": None,
                },
            ]
        }
    }


class ProcedureInformation(Submodel):
    """
    Submodel containing general information about the procedure.

    Args:
        procedure_type (ProcedureTypeEnum): The type of the procedure.
        name (Optional[str]): The name of the procedure.
    """

    procedure_type: ProcedureTypeEnum
    name: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "procedure_information_example",
                    "description": "Example of a procedure information submodel.",
                    "id": "procedure_information_example",
                    "procedure_type": "Production",
                    "name": None,
                },
            ]
        }
    }


class ProcedureConsumption(Submodel):
    """
    Submodel containing the specification of a procedure.

    Args:
        power_consumption (Optional[float]): The power consumption of the procedure.
        water_consumption (Optional[float]): The water consumption of the procedure.

    """

    power_consumption: Optional[float] = None
    water_consumption: Optional[float] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "procedure_consumption_example",
                    "description": "Example of a procedure consumption submodel.",
                    "id": "procedure_consumption_example",
                    "power_consumption": 100.0,
                    "water_consumption": 50.0,
                },
            ]
        }
    }


class Procedure(AAS):
    """
    The Procedure class represents a procedure that is executed by a resource. It contains the process
    attributes, the execution model, and the time model of the procedure.

    Args:
        id (str): The id of the procedure.
        description (Optional[str]): The description of the procedure.
        id_short (Optional[str]): The short id of the procedure.
        process_attributes (processes.ProcessAttributes): Parameters that describe what the procedure does and how it does it.
        execution (ExecutionModel): The execution model of the procedure containing planned and performed executions of this procedure.
        time_model (TimeModel): The time model of the procedure containing parameters to represent the timely duration of the procedure.

    """

    procedure_information: ProcedureInformation
    process_attributes: Optional[ProcessAttributes] = None
    execution_model: Optional[ExecutionModel] = None
    time_model: Optional[TimeModel] = None
    procedure_consumption: Optional[ProcedureConsumption] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "task_1147_process_time_1218_procedure",
                    "description": "Procedure data of task task_1147 with name TTN01_H_Servodeckel_Montage of resource resource_1012 with process time process_time_1218",
                    "id": "task_1147_process_time_1218_procedure",
                    "procedure_information": {
                        "id_short": "task_1147_process_time_1218_procedure_information",
                        "description": "Procedure information of task task_1147 with name TTN01_H_Servodeckel_Montage of resource resource_1012 with process time process_time_1218",
                        "id": "task_1147_process_time_1218_procedure_information",
                        "semantic_id": "",
                        "procedure_type": "Production",
                        "name": None,
                    },
                    "process_attributes": {
                        "id_short": "task_1147_process_time_1218_process_attributes",
                        "description": "Process Attributes of task task_1147 and process time process_time_1218",
                        "id": "task_1147_process_time_1218_process_attributes",
                        "semantic_id": "",
                        "process_attributes": [
                            {
                                "id_short": "task_1147_process_time_1218_capability",
                                "description": "Capability of task task_1147 with process time process_time_1218",
                                "semantic_id": "",
                                "attribute_carrier": "Module",
                                "general_attribute": "Capability",
                                "predicate_type": "equals",
                                "attribute_value": "Servodeckel_Montage",
                            },
                            {
                                "id_short": "task_1147_process_time_1218_product_type",
                                "description": "Product type of task task_1147 with process time process_time_1218",
                                "semantic_id": "",
                                "attribute_carrier": "Module",
                                "general_attribute": "ProductType",
                                "predicate_type": "equals",
                                "attribute_value": "TTN01",
                            },
                        ],
                    },
                    "execution_model": {
                        "id_short": "task_1147_process_time_1218_execution_model",
                        "description": "Execution model of task task_1147 with name TTN01_H_Servodeckel_Montage of resource resource_1012 with process time process_time_1218",
                        "id": "task_1147_process_time_1218_execution_model",
                        "semantic_id": "",
                        "schedule": [
                            {
                                "id_short": "id_000121bd34d911f0bdd3845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-20T22:54:46+00:00",
                                "resource_id": "resource_1012_resource",
                                "procedure_id": "task_1147_process_time_1218_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1039_order_workplan_0_product_1",
                                "expected_end_time": "2025-04-20T22:55:22+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_000121c034d911f09cf5845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-20T22:58:40+00:00",
                                "resource_id": "resource_1012_resource",
                                "procedure_id": "task_1147_process_time_1218_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1041_order_workplan_0_product_1",
                                "expected_end_time": "2025-04-20T22:59:16+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_000121c334d911f083c9845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-20T23:02:34+00:00",
                                "resource_id": "resource_1012_resource",
                                "procedure_id": "task_1147_process_time_1218_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1047_order_workplan_0_product_1",
                                "expected_end_time": "2025-04-20T23:03:10+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_0001704734d911f09e7c845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-20T23:06:28+00:00",
                                "resource_id": "resource_1012_resource",
                                "procedure_id": "task_1147_process_time_1218_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1067_order_workplan_0_product_1",
                                "expected_end_time": "2025-04-20T23:07:04+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                        ],
                        "execution_log": [
                            {
                                "id_short": "id_000121c334d911f083c9845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-20T23:02:34+00:00",
                                "resource_id": "resource_1012_resource",
                                "procedure_id": "task_1147_process_time_1218_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1047_order_workplan_0_product_1",
                                "expected_end_time": "2025-04-20T23:03:10+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_0001704734d911f09e7c845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-20T23:06:28+00:00",
                                "resource_id": "resource_1012_resource",
                                "procedure_id": "task_1147_process_time_1218_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1067_order_workplan_0_product_1",
                                "expected_end_time": "2025-04-20T23:07:04+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                        ],
                    },
                    "time_model": {
                        "id_short": "task_1147_process_time_1218_time_model",
                        "description": "Time model of procedure of task task_1147 with name TTN01_H_Servodeckel_Montage of resource resource_1012 with process time process_time_1218",
                        "id": "task_1147_process_time_1218_time_model",
                        "semantic_id": "",
                        "type_": "distribution",
                        "sequence": None,
                        "repeat": None,
                        "distribution_type": "normal",
                        "distribution_parameters": {
                            "id_short": "task_1147_process_time_1218_distribution_parameters",
                            "description": "",
                            "semantic_id": "",
                            "type": "normal",
                            "mean": 36.0,
                            "std": 3.6,
                        },
                        "speed": None,
                        "rotation_speed": None,
                        "reaction_time": None,
                        "acceleration": None,
                        "deceleration": None,
                        "transport_times": None,
                    },
                    "procedure_consumption": None,
                },
            ]
        }
    }

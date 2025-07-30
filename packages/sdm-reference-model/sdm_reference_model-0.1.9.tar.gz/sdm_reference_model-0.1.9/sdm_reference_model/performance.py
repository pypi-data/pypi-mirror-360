from typing import List, Optional, Tuple, Literal

from enum import Enum

from aas_pydantic import AAS, Submodel, SubmodelElementCollection
from sdm_reference_model.procedure import Event

# TODO docstrings are missing


class KPIEnum(str, Enum):
    """
    Defines the KPIs that can be used in the system (based on DIN ISO 22400).
    """

    OUTPUT = "output"
    THROUGHPUT = "throughput"
    COST = "cost"
    WIP = "WIP"

    TRHOUGHPUT_TIME = "throughput_time"
    PROCESSING_TIME = "processing_time"

    PRODUCTIVE_TIME = "productive_time"
    STANDBY_TIME = "standby_time"
    SETUP_TIME = "setup_time"
    UNSCHEDULED_DOWNTIME = "unscheduled_downtime"

    DYNAMIC_WIP = "dynamic_WIP"
    DYNAMIC_THROUGHPUT_TIME = "dynamic_throughput_time"


class KPILevelEnum(str, Enum):
    """
    Defines the levels on which a KPI can be measured.
    """

    SYSTEM = "system"
    RESOURCE = "resource"
    ALL_PRODUCTS = "all_products"
    PRODUCT_TYPE = "product_type"
    PRODUCT = "product"
    PROCESS = "process"


class KPI(SubmodelElementCollection):
    """
    Defines a Key Performance Indicator (KPI) that can be used to describe the performance of the system.

    Args:
        name (KPIEnum): The name of the KPI.
        target (Literal["min", "max"]): The target of the KPI.
        weight (Optional[float], optional): The weight of the KPI. Defaults to 1.
        value (Optional[float], optional): The value of the KPI. Defaults to None.
        context (Optional[Tuple[KPILevelEnum, ...]], optional): The context of the KPI specified by KPI levels to which the KPI applies. Defaults to None.
        resource (Optional[str], optional): The resource to which the KPI applies. Defaults to None.
        product (Optional[str], optional): The product to which the KPI applies. Defaults to None.
        process (Optional[str], optional): The process to which the KPI applies. Defaults to None.
        start_time (Optional[float], optional): The start time of the KPI. Defaults to None.
        end_time (Optional[float], optional): The end time of the KPI. Defaults to None.
    """

    name: KPIEnum
    target: Literal["min", "max"]
    weight: float = 1.0
    value: Optional[float] = None
    context: Optional[Tuple[KPILevelEnum, ...]] = None
    resource: Optional[str] = None
    product: Optional[str] = None
    process: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "Throughput_Cells_Per_Hour_4",
                    "description": "Throughput of each manufacturing cell per hour",
                    "semantic_id": "",
                    "name": KPIEnum.THROUGHPUT,
                    "target": "max",
                    "weight": 1.0,
                    "value": 14.0,
                    "context": None,
                    "resource": "resource_5000_resource",
                    "product": None,
                    "process": None,
                    "start_time": 1744909200.0,
                    "end_time": 1744912800.0,
                },
                {
                    "id_short": "resource_0_resource_output_kpi",
                    "description": "",
                    "semantic_id": "",
                    "name": "output",
                    "target": "max",
                    "weight": 1.0,
                    "value": 1991.0,
                    "context": ["system", "all_products"],
                    "resource": "resource_0_resource",
                    "product": None,
                    "process": None,
                    "start_time": None,
                    "end_time": None,
                },
            ]
        }
    }


class KeyPerformanceIndicators(Submodel):
    """
    Defines a collection of Key Performance Indicators (KPIs) that can be used to describe the performance of the system.

    Args:
        kpis (List[KPI]): The list of KPIs.
    """

    kpis: List[KPI]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "KPIs_resource_5000_resource",
                    "description": "",
                    "id": "KPIs_resource_5000_resource",
                    "semantic_id": "",
                    "kpis": [
                        {
                            "id_short": "Throughput_Cells_Per_Hour_4",
                            "description": "Throughput of each manufacturing cell per hour",
                            "semantic_id": "",
                            "name": KPIEnum.THROUGHPUT,
                            "target": "max",
                            "weight": 1.0,
                            "value": 14.0,
                            "context": None,
                            "resource": "resource_5000_resource",
                            "product": None,
                            "process": None,
                            "start_time": 1744909200.0,
                            "end_time": 1744912800.0,
                        },
                    ],
                },
            ]
        }
    }


class EventLog(Submodel):
    """
    Defines a log of events that have occurred in the system.

    Args:
        event_log (List[Event]): The list of events that have occurred in the system.
    """

    event_log: List[Event]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "EventLog_resource_5000_resource",
                    "description": "Log of events that have occurred in the system",
                    "id": "EventLog_resource_5000_resource",
                    "semantic_id": "",
                    "event_log": [
                        {
                            "id_short": "id_ffef5f9c34d811f0a3a7845cf38935ae",
                            "description": "",
                            "semantic_id": "",
                            "time": "2025-04-17T19:02:00+00:00",
                            "resource_id": "resource_13_resource",
                            "procedure_id": "task_1144_process",
                            "procedure_type": "Production",
                            "activity": "Start",
                            "product_id": "job_1001_order: workplan_9_product #1",
                            "expected_end_time": "2025-04-17T19:05:15+00:00",
                            "actual_end_time": None,
                            "success": None,
                        },
                        {
                            "id_short": "id_ffef5f9f34d811f0a669845cf38935ae",
                            "description": "",
                            "semantic_id": "",
                            "time": "2025-04-17T19:05:15+00:00",
                            "resource_id": "resource_13_resource",
                            "procedure_id": "task_1144_process",
                            "procedure_type": "Production",
                            "activity": "Start",
                            "product_id": "job_1004_order: workplan_9_product #1",
                            "expected_end_time": "2025-04-17T19:08:30+00:00",
                            "actual_end_time": None,
                            "success": None,
                        },
                        {
                            "id_short": "id_ffef5f9d34d811f09add845cf38935ae",
                            "description": "",
                            "semantic_id": "",
                            "time": "2025-04-17T19:05:50+00:00",
                            "resource_id": "resource_2003_resource",
                            "procedure_id": "task_2009_process",
                            "procedure_type": "Production",
                            "activity": "Start",
                            "product_id": "job_1001_order: workplan_9_product #1",
                            "expected_end_time": "2025-04-17T19:06:50+00:00",
                            "actual_end_time": None,
                            "success": None,
                        },
                    ],
                },
            ]
        }
    }


class Performance(AAS):
    """
    AAS to describe the performance of a production system.

    Args:
        key_performance_indicators (KeyPerformanceIndicators): The Key Performance Indicators (KPIs) that describe the performance of the system.
        event_log (Optional[EventLog], optional): A log of events that have occurred in the system. Defaults to None.
    """

    key_performance_indicators: KeyPerformanceIndicators
    event_log: Optional[EventLog] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "Performance_resource_5000_resource",
                    "description": "Performance of the manufacturing cell",
                    "id": "Performance_resource_5000_resource",
                    "key_performance_indicators": {
                        "id_short": "KPIs_resource_5000_resource",
                        "description": "",
                        "id": "KPIs_resource_5000_resource",
                        "semantic_id": "",
                        "kpis": [
                            {
                                "id_short": "Throughput_Cells_Per_Hour_4",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 14.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744909200.0,
                                "end_time": 1744912800.0,
                            },
                            {
                                "id_short": "Throughput_Cells_Per_Hour_28",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 14.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744930800.0,
                                "end_time": 1744934400.0,
                            },
                            {
                                "id_short": "Throughput_Cells_Per_Hour_32",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 2.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744934400.0,
                                "end_time": 1744938000.0,
                            },
                            {
                                "id_short": "Throughput_Cells_Per_Hour_36",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 0.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744938000.0,
                                "end_time": 1744941600.0,
                            },
                            {
                                "id_short": "Throughput_Cells_Per_Hour_40",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 14.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744941600.0,
                                "end_time": 1744945200.0,
                            },
                            {
                                "id_short": "Throughput_Cells_Per_Hour_44",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 16.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744945200.0,
                                "end_time": 1744948800.0,
                            },
                            {
                                "id_short": "Throughput_Cells_Per_Hour_48",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 16.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744948800.0,
                                "end_time": 1744952400.0,
                            },
                            {
                                "id_short": "Throughput_Cells_Per_Hour_52",
                                "description": "Throughput of each manufacturing cell per hour",
                                "semantic_id": "",
                                "name": "throughput",
                                "target": "max",
                                "weight": 1.0,
                                "value": 12.0,
                                "context": None,
                                "resource": "resource_5000_resource",
                                "product": None,
                                "process": None,
                                "start_time": 1744952400.0,
                                "end_time": 1744956000.0,
                            },
                        ],
                    },
                    "event_log": {
                        "id_short": "EventLog_resource_5000_resource",
                        "description": "Log of events that have occurred in the system",
                        "id": "EventLog_resource_5000_resource",
                        "semantic_id": "",
                        "event_log": [
                            {
                                "id_short": "id_ffef5f9c34d811f0a3a7845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-17T19:02:00+00:00",
                                "resource_id": "resource_13_resource",
                                "procedure_id": "task_1144_process",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1001_order: workplan_9_product #1",
                                "expected_end_time": "2025-04-17T19:05:15+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_ffef5f9f34d811f0a669845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-17T19:05:15+00:00",
                                "resource_id": "resource_13_resource",
                                "procedure_id": "task_1144_process",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1004_order: workplan_9_product #1",
                                "expected_end_time": "2025-04-17T19:08:30+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_ffef5f9d34d811f09add845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-17T19:05:50+00:00",
                                "resource_id": "resource_2003_resource",
                                "procedure_id": "task_2009_process",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1001_order: workplan_9_product #1",
                                "expected_end_time": "2025-04-17T19:06:50+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                        ],
                    },
                },
                {
                    "id_short": "resource_0_resource_performance",
                    "description": "",
                    "id": "resource_0_resource_performance",
                    "key_performance_indicators": {
                        "id_short": "resource_0_resource_performance_kpis",
                        "description": "",
                        "id": "resource_0_resource_performance_kpis",
                        "semantic_id": "",
                        "kpis": [
                            {
                                "id_short": "resource_0_resource_output_kpi",
                                "description": "",
                                "semantic_id": "",
                                "name": "output",
                                "target": "max",
                                "weight": 1.0,
                                "value": 1991.0,
                                "context": ["system", "all_products"],
                                "resource": "resource_0_resource",
                                "product": None,
                                "process": None,
                                "start_time": None,
                                "end_time": None,
                            }
                        ],
                    },
                    "event_log": {
                        "id_short": "resource_0_resource_event_log",
                        "description": "Log of events that have occurred in the system",
                        "id": "resource_0_resource_event_log",
                        "semantic_id": "",
                        "event_log": [
                            {
                                "id_short": "id_ffef5f9c34d811f0a3a7845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-17T19:02:00+00:00",
                                "resource_id": "resource_13_resource",
                                "procedure_id": "task_1144_process",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1001_order: workplan_9_product #1",
                                "expected_end_time": "2025-04-17T19:05:15+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_ffef5f9f34d811f0a669845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-17T19:05:15+00:00",
                                "resource_id": "resource_13_resource",
                                "procedure_id": "task_1144_process",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1004_order: workplan_9_product #1",
                                "expected_end_time": "2025-04-17T19:08:30+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_ffef5f9d34d811f09add845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-17T19:05:50+00:00",
                                "resource_id": "resource_2003_resource",
                                "procedure_id": "task_2009_process",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_1001_order: workplan_9_product #1",
                                "expected_end_time": "2025-04-17T19:06:50+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                        ],
                    },
                },
            ],
        }
    }

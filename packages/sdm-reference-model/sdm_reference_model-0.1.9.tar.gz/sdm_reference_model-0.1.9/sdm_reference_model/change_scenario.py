from typing import Literal, Union, Optional, List

from enum import Enum

from aas_pydantic import AAS, Submodel, SubmodelElementCollection

from .distribution import (
    ABSTRACT_INTEGER_DISTRIBUTION,
    ABSTRACT_REAL_DISTRIBUTION,
)

from .performance import KPIEnum


class ChangeDriverInfluence(SubmodelElementCollection):
    """
    The ChangeDriverInfluence represents the influence of a change driver on a receptor key figure.

    Args:
        is_influenced (bool): True if the change driver influences the receptor key figure, False otherwise.
        influenecing_change_driver_id (str): The id of the change driver that influences the receptor key figure.
        influence_type (str): The type of the influence of the change driver on the receptor key figure.
        influence_time (float): The time of the influence of the change driver on the receptor key figure.
    """

    is_influenced: bool
    influenecing_change_driver_id: str  # ID of the change driver
    influence_type: str  # changed to type because boolean diddn't make sense
    influence_time: float  # changed to float because boolean didn't make sense for time


class ChangeDriver(SubmodelElementCollection):
    """
    The ChangeDriver represents a change driver of a change scenario.

    Args:
        id (str): The id of the change driver.
        description (Optional[str]): The description of the change driver.
        id_short (Optional[str]): The short id of the change driver.
        sematic_id (Optional[str]): The semantic id of the change driver.
        occurrence_distribution_function_over_time_horizon (ABSTRACT_REAL_DISTRIBUTION): The occurrence distribution function over the time horizon.
        occurrence_distribution_per_unit_of_time (ABSTRACT_INTEGER_DISTRIBUTION): The occurrence distribution per unit of time.
        frequency (float): The frequency of the change driver.
        change_driver_influences (List[ChangeDriverInfluence]): The influences of the change driver on the receptor key figures.
        influenced_receptor_key_figure_ids (List[str]): The ids of the receptor key figures that are influenced by the change driver.
    """

    distribution_function_over_time_horizon: Optional[ABSTRACT_REAL_DISTRIBUTION] = (
        None  # wann der Wandlungstreiber in einem vorgegebenen Zeitraum auftreten kann
    )
    occurrence_distribution_per_unit_of_time: Optional[
        ABSTRACT_INTEGER_DISTRIBUTION
    ] = None  # mit welcher Wahrscheinlichkeit der Wandlungstreiber insgesamt eintritt
    frequency: float
    change_driver_influences: List[ChangeDriverInfluence]
    influenced_receptor_key_figure_ids: List[
        str
    ]  # List of IDs of the receptor key figures


class ReceptorEnum(str, Enum):
    QUANTITY = "quantity"
    COST = "cost"
    TIME = "time"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    QUALITY = "quality"


class ModellingEnum(str, Enum):
    DISCRETE = "discrete"
    CONTINUOUS = "continuous"


class DiscreteRKF(SubmodelElementCollection):
    """
    The DiscreteRKF represents a discrete receptor key figure.

    Args:
        value_for_occurence (str): The value for the occurence of the receptor key figure.
        value_for_non_occurence (str): The value for the non-occurence of the receptor key figure.
        previous_value (str): The previous value of the receptor key figure.
    """

    value_for_occurence: str
    value_for_non_occurence: str
    previous_value: str


class ContinuousRKF(SubmodelElementCollection):
    """
    The ContinuousRKF represents a continuous receptor key figure.

    Args:
        absolute_influences_change_drivers (str): The absolute influences of the change drivers on the receptor key figure.
        relative_influences_change_drivers (str): The relative influences of the change drivers on the receptor key figure.
        slope_influences_change_drivers (str): The slope influences of the change drivers on the receptor key figure.
        previous_slope (float): The previous slope of the receptor key figure.
        previous_value (float): The previous value of the receptor key figure.
    """

    absolute_influences_change_drivers: str
    relative_influences_change_drivers: str
    slope_influences_change_drivers: str
    previous_slope: float
    previous_value: float


class ReceptorKeyFigure(SubmodelElementCollection):
    receptor_type: ReceptorEnum
    modelling_type: ModellingEnum
    unit: str
    value: Union[DiscreteRKF, ContinuousRKF]


class ScenarioModel(Submodel):
    change_drivers: List[ChangeDriver]
    receptor_key_figures: List[ReceptorKeyFigure]


class ProductSaleForecast(SubmodelElementCollection):
    """
    The ProductSaleForecast represents the forecast of the sale of a product.

    Args:
        product_id (str): The id of the product.
        quantity (float): The quantity of the product that is sold.
        forecast_start (str): The start of the forecast of the sale of the product.
        forecast_end (str): The end of the forecast of the sale of the product.
    """

    product_id: str
    quantity: float
    start: str
    end: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "product_0_product_sale_forecast",
                    "description": "Forecast of the sale of product with id product_0.",
                    "id": "product_0_product_sale_forecast",
                    "semantic_id": "",
                    "product_id": "product_0_product",
                    "quantity": 1000.0,
                    "start": "2023-01-01T00:00:00Z",
                    "end": "2023-12-31T23:59:59Z",
                }
            ]
        }
    }


class ScenarioForecasts(Submodel):
    """
    The ScenarioForecasts represents the forecasts of the change scenario.

    Args:
        product_sale_forecasts (List[ProductSaleForecast]): The forecasts of the sale of the products.
    """

    product_sale_forecasts: List[ProductSaleForecast]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "scenario_0_scenario_forecasts",
                    "description": "Forecasts of scenario with id scenario_0.",
                    "id": "scenario_0_scenario_forecasts",
                    "semantic_id": "",
                    "product_sale_forecasts": [
                        {
                            "product_id": "product_0_product",
                            "quantity": 1000.0,
                            "start": "2023-01-01T00:00:00Z",
                            "end": "2023-12-31T23:59:59Z",
                        },
                        {
                            "product_id": "product_1_product",
                            "quantity": 500.0,
                            "start": "2023-01-01T00:00:00Z",
                            "end": "2023-12-31T23:59:59Z",
                        },
                    ]
                }
            ]
        }
    }


class ReconfigurationConstraints(Submodel):
    """
    The ReconfigurationConstraints represents the constraints for the reconfiguration of the production system.

    Args:
        max_reconfiguration_cost (float): The maximum cost of reconfiguration of the production system.
        max_reconfiguration_time (float): The maximum time of reconfiguration of the production system.
        max_number_of_machines (int): The maximum number of machines of the production system.
        max_number_of_transport_resources (int): The maximum number of transport resources of the production system.
        max_number_of_process_model_per_resource (int): The maximum number of process models per resource of the production system.
    """

    max_reconfiguration_cost: float
    max_reconfiguration_time: float
    max_number_of_machines: int
    max_number_of_transport_resources: int
    max_number_of_process_modules_per_resource: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "scenario_0_reconfiguration_constraints",
                    "description": "Reconfiguration constraints of scenario with id scenario_0.",
                    "id": "scenario_0_reconfiguration_constraints",
                    "semantic_id": "",
                    "max_reconfiguration_cost": 500000.0,
                    "max_reconfiguration_time": -1.0,  # -1 means no limit
                    "max_number_of_machines": 24,
                    "max_number_of_transport_resources": 6,
                    "max_number_of_process_modules_per_resource": 2,
                }
            ]
        }
    }


class ReconfigurationEnum(str, Enum):
    """
    # from prodsys
    Enum that represents the different levels of reconfigurations that are possible.

    - ProductionCapacity: Reconfiguration of production capacity (number of machines and their configuration)
    - TransportCapacity: Reconfiguration of transport capacity (number of transport resources and their configuration)
    - Layout: Reconfiguration of layout (only position of resources)
    - SequencingLogic: Reconfiguration of sequencing logic (only the control policy of resources)
    - RoutingLogic: Reconfiguration of routing logic (only the routing heuristic of routers)
    """

    FULL = "full"
    PRODUCTION_CAPACITY = "production_capacity"
    TRANSPORT_CAPACITY = "transport_capacity"
    LAYOUT = "layout"
    SEQUENCING_LOGIC = "sequencing_logic"
    ROUTING_LOGIC = "routing_logic"


class ReconfigurationOptions(Submodel):
    """
    The ReconfigurationOptions represents the options for the reconfiguration of the production system.

    Args:
        id (str): The id of the reconfiguration option.
        description (Optional[str]): The description of the reconfiguration option.
        id_short (Optional[str]): The short id of the reconfiguration option.
        sematic_id (Optional[str]): The semantic id of the reconfiguration option.
        reconfiguration_type (ReconfigurationEnum): The type of reconfiguration that is possible.
        machine_controllers (List[Literal["FIFO", "LIFO", "SPT"]]): The machine controllers that are possible.
        transport_controllers (List[Literal["FIFO", "SPT_transport"]]): The transport controllers that are possible.
        routing_heuristics (List[Literal["shortest_queue", "random"]]): The routing heuristics that are possible.
    """

    reconfiguration_type: ReconfigurationEnum
    machine_controllers: List[Literal["FIFO", "LIFO", "SPT"]]
    transport_controllers: List[Literal["FIFO", "SPT_transport"]]
    routing_heuristics: List[Literal["shortest_queue", "random"]]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "scenario_0_reconfiguration_options",
                    "description": "Reconfiguration options of scenario with id scenario_0.",
                    "id": "scenario_0_reconfiguration_options",
                    "semantic_id": "",
                    "reconfiguration_type": "full",
                    "machine_controllers": ["FIFO", "LIFO", "SPT"],
                    "transport_controllers": ["FIFO", "SPT_transport"],
                    "routing_heuristics": ["shortest_queue", "random"],
                },
            ]
        }
    }


class Objective(SubmodelElementCollection):
    """
    The Objective represents an objective of the change scenario.

    Args:
        description (Optional[str]): The description of the objective.
        id_short (Optional[str]): The short id of the objective.
        sematic_id (Optional[str]): The semantic id of the objective.
        type (KPIEnum): The type of the objective.
        weight (float): The weight of the objective.
    """

    type: KPIEnum
    weight: float

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "scenario_0_reconfiguration_objective_1",  
                    "description": "Reconfiguration objective of scenario with id scenario_0.",
                    "semantic_id": "",
                    "type": "cost",
                    "weight": 0.1,
                },
                {
                    "id_short": "scenario_0_reconfiguration_objective_2",
                    "description": "Reconfiguration objective of scenario with id scenario_0.",
                    "semantic_id": "",
                    "type": "throughput",
                    "weight": 1000.0,
                },
            ]
        }
    }


class ReconfigurationObjectives(Submodel):
    """
    The ReconfigurationObjectives represents the objectives of the change scenario.

    Args:
        id (str): The id of the reconfiguration objectives.
        description (Optional[str]): The description of the reconfiguration objectives.
        id_short (Optional[str]): The short id of the reconfiguration objectives.
        sematic_id (Optional[str]): The semantic id of the reconfiguration objectives.
        objectives (List[Objective]): The objectives of the change scenario.
    """

    objectives: List[Objective]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "scenario_0_reconfiguration_objectives",
                    "description": "Reconfiguration objectives of scenario with id scenario_0.",
                    "id": "scenario_0_reconfiguration_objectives",
                    "semantic_id": "",
                    "objectives": [
                        {
                            "id_short": "scenario_0_reconfiguration_objective_1",
                            "description": "Reconfiguration objective of scenario with id scenario_0.",
                            "semantic_id": "",
                            "type": "cost",
                            "weight": 0.1,
                        },
                        {
                            "id_short": "scenario_0_reconfiguration_objective_2",
                            "description": "Reconfiguration objective of scenario with id scenario_0.",
                            "semantic_id": "",
                            "type": "throughput",
                            "weight": 1000.0,
                        },
                    ]
                }
            ]
        }
    }


class ScenarioResources(Submodel):
    """
    The ResourceReferenceSubmodel represents a reference to a resource.

    Args:
        id (str): The id of the resource reference.
        description (Optional[str]): The description of the resource reference.
        id_short (Optional[str]): The short id of the resource reference.
        sematic_id (Optional[str]): The semantic id of the resource reference.
        base_id (str): The id of the base production system.
        solution_ids (List[str]): The ids of the resources that are solutions of the optimization.
    """

    base_id: Optional[str] = None
    solution_ids: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "scenario_0_scenario_resources",
                    "description": "Resources of scenario with id scenario_0.",
                    "id": "scenario_0_scenario_resources",
                    "semantic_id": "",
                    "base_id": "resource_0_resource",
                    "solution_ids": None,
                }
            ]
        }
    }


class ChangeScenario(AAS):
    """
    The ChangeScenario represents a change scenario for the configuration of a production system. It contains the change drivers and the
    receptor key figures of the change scenario, thus describing how requirements on the production system change over time.

    Moreover, the change scenario holds constraints and options for reconfiguration of the production system, objectives of the change
    scenario and a list to found solutions.

    Args:
        id (str): The id of the change scenario.
        description (Optional[str]): The description of the change scenario.
        id_short (Optional[str]): The short id of the change scenario.
        semantic_id (Optional[str]): The semantic id of the change scenario.
        scenario_model (Optional[ScenarioModel]): The model of the change scenario, containing change drivers and receptor key figures.
        scenario_forecasts (Optional[ScenarioForecasts]): The forecasts of the change scenario, containing product sale forecasts.
        scenario_resources (Optional[ScenarioResources]): The resources of the change scenario, containing references to the resources of the production system.
        reconfiguration_constraints (Optional[ReconfigurationConstraints]): The constraints for the reconfiguration of the production system.
        reconfiguration_options (Optional[ReconfigurationOptions]): The options for the reconfiguration of the production system.
        reconfiguration_objectives (Optional[ReconfigurationObjectives]): The objectives of the change scenario, containing the objectives for the reconfiguration of the production system.
    """

    scenario_model: Optional[ScenarioModel] = None
    scenario_forecasts: Optional[ScenarioForecasts] = None
    scenario_resources: Optional[ScenarioResources] = None
    reconfiguration_constraints: Optional[ReconfigurationConstraints] = None
    reconfiguration_options: Optional[ReconfigurationOptions] = None
    reconfiguration_objectives: Optional[ReconfigurationObjectives] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "scenario_0_scenario",
                    "description": "Scenario with id scenario_0.",
                    "id": "scenario_0_scenario",
                    "scenario_model": None,
                    "scenario_forecasts": None,
                    "scenario_resources": {
                        "id_short": "scenario_0_scenario_resources",
                        "description": "Resources of scenario with id scenario_0.",
                        "id": "scenario_0_scenario_resources",
                        "semantic_id": "",
                        "base_id": "resource_0_resource",
                        "solution_ids": None,
                    },
                    "reconfiguration_constraints": {
                        "id_short": "scenario_0_reconfiguration_constraints",
                        "description": "Reconfiguration constraints of scenario with id scenario_0.",
                        "id": "scenario_0_reconfiguration_constraints",
                        "semantic_id": "",
                        "max_reconfiguration_cost": 500000.0,
                        "max_reconfiguration_time": -1.0,
                        "max_number_of_machines": 24,
                        "max_number_of_transport_resources": 6,
                        "max_number_of_process_modules_per_resource": 2,
                    },
                    "reconfiguration_options": {
                        "id_short": "scenario_0_reconfiguration_options",
                        "description": "Reconfiguration options of scenario with id scenario_0.",
                        "id": "scenario_0_reconfiguration_options",
                        "semantic_id": "",
                        "reconfiguration_type": "full",
                        "machine_controllers": ["FIFO", "LIFO", "SPT"],
                        "transport_controllers": ["FIFO", "SPT_transport"],
                        "routing_heuristics": ["shortest_queue", "random"],
                    },
                    "reconfiguration_objectives": {
                        "id_short": "scenario_0_reconfiguration_objectives",
                        "description": "Reconfiguration objectives of scenario with id scenario_0.",
                        "id": "scenario_0_reconfiguration_objectives",
                        "semantic_id": "",
                        "objectives": [
                            {
                                "id_short": "scenario_0_reconfiguration_objective_1",
                                "description": "Reconfiguration objective of scenario with id scenario_0.",
                                "semantic_id": "",
                                "type": "cost",
                                "weight": 0.1,
                            },
                            {
                                "id_short": "scenario_0_reconfiguration_objective_2",
                                "description": "Reconfiguration objective of scenario with id scenario_0.",
                                "semantic_id": "",
                                "type": "throughput",
                                "weight": 1000.0,
                            },
                            {
                                "id_short": "scenario_0_reconfiguration_objective_3",
                                "description": "Reconfiguration objective of scenario with id scenario_0.",
                                "semantic_id": "",
                                "type": "WIP",
                                "weight": 10.0,
                            },
                        ],
                    },
                }
            ]
        }
    }

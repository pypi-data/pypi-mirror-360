from __future__ import annotations
from typing import List, Optional, Literal
from enum import Enum

from pydantic import conlist

from aas_pydantic import AAS, Submodel, SubmodelElementCollection

from sdm_reference_model.procedure import ProcedureTypeEnum
from sdm_reference_model.product import ConstructionData


class ResourceInformation(Submodel):
    """
    Submodel to describe the general information of a resource.

    Args:
        id (str): The id of the general information.
        description (Optional[str]): The description of the general information.
        id_short (Optional[str]): The short id of the general information.
        semantic_id (Optional[str]): The semantic id of the general information.
        name (Optional[str]): The name of the resource.
        manufacturer (Optional[str]): The manufacturer of the resource.
        production_level (Literal["Module", "Station", "System", "Plant", "Network"]): The production level of the resource.
        resource_type (Literal["Manufacturing", "Material Flow", "Storage"]): The type of the resource.
    """

    name: Optional[str] = None
    manufacturer: Optional[str] = None
    production_level: Literal["Module", "Station", "System", "Plant", "Network"]
    resource_type: Literal[
        "Manufacturing",
        "Material Flow",
        "Storage",
        "Barrier",
        "Empty Spot",
        "Boundary",
        "Source",
        "Sink",
    ]


class Capabilities(Submodel):
    """
    Submodel to describe the capabilities of a resource by describing available
    procedures in the resource.

    Args:
        id (str): The id of the capabilities.
        description (Optional[str]): The description of the capabilities.
        id_short (Optional[str]): The short id of the capabilities.
        semantic_id (Optional[str]): The semantic id of the capabilities.
        procedure_ids (List[str]): The list of ids of procedure that are available for the resource.
    """

    procedures_ids: List[str]


class ControlLogic(Submodel):
    """
    Submodel to describe the control logic of a resource, by describing its control policy. It specifies in which sequence the resource processes the products.

    Args:
        id (str): The id of the control logic.
        id_short (str): The short id of the control logic.
        description (Optional[str]): The description of the control logic.
        semantic_id (Optional[str]): The semantic id of the control logic.
        sequencing_policy (Literal["FIFO", "SPT_transport", "LIFO", "SPT", "EDD", "ODD"]): The sequencing policy of the resource, determining in which sequence requests are processed.
        routing_policy (Literal["random", "nearest", "shortest_queue", "alternating, "round_robin"]): The routing policy of the resource how redundant sub resources are used.
    """

    sequencing_policy: Optional[Literal["FIFO", "SPT", "LIFO", "SPT", "EDD", "ODD"]] = (
        None
    )
    routing_policy: Optional[
        Literal["random", "nearest", "shortest_queue", "alternating", "round_robin"]
    ] = None


class SubResource(SubmodelElementCollection):
    """
    SubmodelElementCollection to describe a subresource of a resource with reference to its AAS, position and orientation (2D or 3D).

    Args:
        description (Optional[str]): The description of the subresource.
        id_short (Optional[str]): The short id of the subresource.
        semantic_id (Optional[str]): The semantic id of the subresource.
        resource_id (str): The id of the subresource.
        position (conlist(float, min_length=2, max_length=3)): The position of the subresource (x, y, z).
        orientation (conlist(float, min_length=1, max_length=3)): The orientation of the subresource (alpha, beta, gamma).
    """

    resource_id: str
    position: conlist(float, min_length=2, max_length=3)  # type: ignore
    orientation: conlist(float, min_length=1, max_length=3)  # type: ignore


class ResourceStatus(SubmodelElementCollection):
    """
    SubmodelElementCollection to describe the status of a resource.

    Args:
        description (Optional[str]): The description of the status.
        id_short (Optional[str]): The short id of the status.
        semantic_id (Optional[str]): The semantic id of the status.
        status (ProcedureTypeEnum): The status of the resource.
        status_start (Optional[str]): The start time of the status (ISO 8601 time stamp).
    """

    status: ProcedureTypeEnum
    status_start: Optional[str] = None


class ResourceLink(SubmodelElementCollection):
    """
    SubmodelElementCollection to describe the status of a resource.

    Args:
        description (Optional[str]): The description of the status.
        id_short (Optional[str]): The short id of the status.
        semantic_id (Optional[str]): The semantic id of the status.
        origin_resource_id (str): The id of the origin resource.
        target_resource_id (str): The id of the target resource.
        link_type (Literal["Directional", "Bidirectional"]): The type of the link.
    """

    origin_resource_id: str
    target_resource_id: str
    link_type: Literal["Directional", "Bidirectional"]


class ResourceConfiguration(Submodel):
    """
    Submodel to describe the configuration of a resource, by describing its sub resources and their position and orientation.

    Args:
        id (str): The id of the resource hierarchy.
        description (Optional[str]): The description of the resource hierarchy.
        id_short (Optional[str]): The short id of the resource hierarchy.
        semantic_id (Optional[str]): The semantic id of the resource hierarchy.
        sub_resources (Optional[List[SubResource]]): IDs ob sub resources
    """

    sub_resources: Optional[List[SubResource]] = None
    resource_links: Optional[List[ResourceLink]] = None
    status: Optional[ResourceStatus] = None


class InformationInterface(SubmodelElementCollection):
    """
    Interface for information exchange with the resource.

    Args:
        protocol (str): The protocol of the information interface.
        adress (str): The adress of the information interface (e.g. IP adress)
        port (Optional[int]): The port of the information interface.
        endpoint (Optional[str]): Specifies, the endpoint that to interface requires (e.g. topic, rest Endpoint or OPC UA Node id)
    """

    protocol: str
    host: str
    port: Optional[int] = None
    endpoint: Optional[str] = None


class MaterialDirectionType(str, Enum):
    """
    Enum to describe the direction of material flow in a material interface.
    """

    IN = "IN"
    OUT = "OUT"
    INOUT = "INOUT"


class MaterialInterface(SubmodelElementCollection):
    """
    Interface for material handling, e.g. if a product is passed to this resource, the MaterialInterface specifies the requried position and orientation
    of the product (each in 2D or 3D coordinates).

    Args:
        position (conlist(float, min_length=2, max_length=3)): The position of the material interface.
        orientation (conlist(float, min_length=2, max_length=3)): The orientation of the material interface.
    """

    position: conlist(float, min_length=2, max_length=3)  # type: ignore
    orientation: conlist(float, min_length=2, max_length=3)  # type: ignore
    key_points: List[KeyPoint]
    direction: MaterialDirectionType = MaterialDirectionType.INOUT


class KeyPoint(SubmodelElementCollection):
    position: conlist(float, min_length=2, max_length=3)  # type: ignore
    orientation: conlist(float, min_length=2, max_length=4)  # type: ignore
    procedure_id: (
        str  # Id of the procedure of the resource that should be triggered here...
    )


class EnergyInterface(SubmodelElementCollection):
    """
    Interface for energy handling, e.g. if a product is passed to this resource, the EnergyInterface specifies the requried energy level.

    Args:
        voltage (float): The voltage of the energy interface.
        current (float): The current of the energy interface.
        power (float): The power of the energy interface.
        current_type (str): The current type of the energy interface.
    """

    voltage: float
    current: float
    nominal_power_consumption: float
    peak_power_consumption: float
    standby_power_consumption: float
    current_type: str


class ResourceInterfaces(Submodel):
    """
    Submodel to describe the interfaces of a resource to connect to the resource either by energy, information or material.

    Args:
        id (str): The id of the resource interfaces.
        description (Optional[str]): The description of the resource interfaces.
        id_short (Optional[str]): The short id of the resource interfaces.
        semantic_id (Optional[str]): The semantic id of the resource interfaces.
        information_interface (Optional[List[CommunicationInterface]]): The communication interfaces of the resource.
        material_interfaces (Optional[List[MaterialInterface]]): The material interfaces of the resource.
        energy_interfaces (Optional[List[EnergyInterface]]): The energy interfaces of the resource.
    """

    information_interface: Optional[List[InformationInterface]] = None
    material_interfaces: Optional[List[MaterialInterface]] = None
    energy_interfaces: Optional[List[EnergyInterface]] = None


class ResourcePerformance(SubmodelElementCollection):
    """
    Submodel to make a reference to the Peroformance of a resource.

    Args:
        description (Optional[str]): The description of the resource performance.
        id_short (Optional[str]): The short id of the resource performance.
        semantic_id (Optional[str]): The semantic id of the resource performance.
        performance_id (Optional[str]): The id of the performance AAS of the resource.
        associated_configuration_id (Optional[str]): The id of the configuration AAS of the resource.
        obtained_performance_from (str): The tool / software used to obtain the results.
    """

    performance_id: Optional[str] = None  # link to the performance AAS of the resource
    associated_configuration_id: Optional[str] = None
    obtained_performance_from: str  # Tool / Software used to obtain the results


class ResourcePerformances(Submodel):
    """
    Submodel to describe the performance of a resource.

    Args:
        id (str): The id of the resource performance.
        description (Optional[str]): The description of the resource performance.
        id_short (Optional[str]): The short id of the resource performance.
        semantic_id (Optional[str]): The semantic id of the resource performance.
        resource_performance (Optional[List[ResourcePerformance]]): The performances of the resource.
    """

    resource_performance: Optional[List[ResourcePerformance]] = None


class Location(SubmodelElementCollection):
    resource_id: str
    resource_name: str
    x: float
    y: float
    z: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class ResourceLocationHistory(Submodel):
    """
    Submodel to describe the location history of a resource.

    Args:
        id (str): The id of the location history.
        description (Optional[str]): The description of the location history.
        id_short (Optional[str]): The short id of the location history.
        semantic_id (Optional[str]): The semantic id of the location history.
        locations (Optional[List[Location]]): The location history of the resource.
    """

    locations: Optional[List[Location]] = None


class ProductReference(Submodel):
    """
    Submodel to describe the emission of a resource.

    Args:
        name (str): Name of the tool that is used for a process.
    """

    product_reference_id: Optional[str] = None


class Resource(AAS):
    """
    AAS to describe a resource.

    Args:
        id (str): The id of the resource.
        description (Optional[str]): The description of the resource.
        id_short (Optional[str]): The short id of the resource.
        resource_information (Optional[ResourceInformation]): some general information describing the resource.
        capabilities (Optional[Capabilities]): The capabilities of the resource, containing information about available procedures.
        construction_data (Optional[ConstructionData]): The construction data of the resource.
        resource_configuration (Optional[ResourceHierarchy]): The configruation of the resource, containting information about sub resources.
        control_logic (Optional[ControlLogic]): The control logic of the resource.
        resource_interface (Optional[ResourceInterfaces]): the interfaces of the resource.
    """

    resource_information: Optional[ResourceInformation] = None
    capabilities: Optional[Capabilities] = None
    construction_data: Optional[ConstructionData] = None
    resource_configuration: Optional[ResourceConfiguration] = None
    control_logic: Optional[ControlLogic] = None
    resource_interface: Optional[ResourceInterfaces] = None
    resource_performances: Optional[ResourcePerformances] = None
    resource_location_history: Optional[ResourceLocationHistory] = None
    product_reference: Optional[ProductReference] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
            "id_short": "resource_0_resource",
            "description": "Resource with id resource_0 and name global",
            "id": "resource_0_resource",
            "resource_information": {
                "id_short": "resource_0_general_information",
                "description": "General Information of resource resource_0 with name global",
                "id": "resource_0_general_information",
                "semantic_id": "",
                "name": None,
                "manufacturer": "Bosch",
                "production_level": "Plant",
                "resource_type": "Manufacturing"
            },
            "capabilities": None,
            "construction_data": None,
            "resource_configuration": {
                "id_short": "resource_0_resource_configuration",
                "description": "Resource configuration of resource resource_0 with name global",
                "id": "resource_0_resource_configuration",
                "semantic_id": "",
                "sub_resources": [
                    {
                        "id_short": "resource_0_subresource_resource_20",
                        "description": "Subresource of resource resource_0 with name global",
                        "semantic_id": "",
                        "resource_id": "resource_20_resource",
                        "position": [
                            -1.0,
                            -1.0
                        ],
                        "orientation": [
                            -1.0
                        ]
                    },
                    {
                        "id_short": "resource_0_subresource_resource_4000",
                        "description": "Subresource of resource resource_0 with name global",
                        "semantic_id": "",
                        "resource_id": "resource_4000_resource",
                        "position": [
                            1.5,
                            9.0
                        ],
                        "orientation": [
                            0.0
                        ]
                    },
                    {
                        "id_short": "resource_0_subresource_resource_5000",
                        "description": "Subresource of resource resource_0 with name global",
                        "semantic_id": "",
                        "resource_id": "resource_5000_resource",
                        "position": [
                            16.5,
                            9.0
                        ],
                        "orientation": [
                            0.0
                        ]
                    },
                ],
                "resource_links": None,
                "status": {
                    "id_short": "resource_0_status",
                    "description": "Status of resource resource_0 with name global",
                    "semantic_id": "",
                    "status": "StandBy",
                    "status_start": None
                }
            },
            "control_logic": None,
            "resource_interface": None,
            "resource_performances": None,
            "resource_location_history": None,
            "product_reference": None
        },
        {
            "id_short": "resource_20_resource",
            "description": "Resource with id resource_20 and name F_Sensordeckel_Montage",
            "id": "resource_20_resource",
            "resource_information": {
                "id_short": "resource_20_general_information",
                "description": "General Information of resource resource_20 with name F_Sensordeckel_Montage",
                "id": "resource_20_general_information",
                "semantic_id": "",
                "name": None,
                "manufacturer": "Bosch",
                "production_level": "System",
                "resource_type": "Manufacturing"
            },
            "capabilities": None,
            "construction_data": None,
            "resource_configuration": {
                "id_short": "resource_20_resource_configuration",
                "description": "Resource configuration of resource resource_20 with name F_Sensordeckel_Montage",
                "id": "resource_20_resource_configuration",
                "semantic_id": "",
                "sub_resources": [
                    {
                        "id_short": "resource_20_subresource_resource_13",
                        "description": "Subresource of resource resource_20 with name F_Sensordeckel_Montage",
                        "semantic_id": "",
                        "resource_id": "resource_13_resource",
                        "position": [
                            1.5,
                            4.5
                        ],
                        "orientation": [
                            0.0
                        ]
                    }
                ],
                "resource_links": None,
                "status": {
                    "id_short": "resource_20_status",
                    "description": "Status of resource resource_20 with name F_Sensordeckel_Montage",
                    "semantic_id": "",
                    "status": "StandBy",
                    "status_start": None
                }
            },
            "control_logic": None,
            "resource_interface": None,
            "resource_performances": None,
            "resource_location_history": None,
            "product_reference": None
        },
        {
            "id_short": "resource_13_module_Sensordeckel_Montage",
            "description": "Module of resource resource_13 with capability Sensordeckel_Montage",
            "id": "resource_13_module_Sensordeckel_Montage",
            "resource_information": {
                "id_short": "resource_13_module_Sensordeckel_Montage_resource_information",
                "description": "Resource information of module of resource resource_13 with capability Sensordeckel_Montage",
                "id": "resource_13_module_Sensordeckel_Montage_resource_information",
                "semantic_id": "",
                "name": None,
                "manufacturer": "Bosch",
                "production_level": "Module",
                "resource_type": "Manufacturing"
            },
            "capabilities": {
                "id_short": "resource_13_module_Sensordeckel_Montage_capabilities",
                "description": "Capabilties of resource resource_13",
                "id": "resource_13_module_Sensordeckel_Montage_capabilities",
                "semantic_id": "",
                "procedures_ids": [
                    "task_1135_process_time_1206_procedure",
                    "task_1136_process_time_1207_procedure",
                    "task_1137_process_time_1208_procedure",
                    "task_1138_process_time_1209_procedure",
                    "task_1139_process_time_1210_procedure",
                    "task_1140_process_time_1211_procedure",
                    "task_1141_process_time_1212_procedure",
                    "task_1142_process_time_1213_procedure",
                    "task_1143_process_time_1214_procedure",
                    "task_1144_process_time_1215_procedure",
                    "task_1145_process_time_1216_procedure",
                    "task_1146_process_time_1217_procedure"
                ]
            },
            "construction_data": None,
            "resource_configuration": {
                "id_short": "resource_13_module_Sensordeckel_Montage_resource_configuration",
                "description": "Resource configuration of module of resource resource_13 with capability Sensordeckel_Montage",
                "id": "resource_13_module_Sensordeckel_Montage_resource_configuration",
                "semantic_id": "",
                "sub_resources": None,
                "resource_links": None,
                "status": None
            },
            "control_logic": None,
            "resource_interface": None,
            "resource_performances": None,
            "resource_location_history": None,
            "product_reference": None
        },
        {
            "id_short": "resource_13_resource",
            "description": "Resource with id resource_13 and name F_Sensordeckel_Montage1",
            "id": "resource_13_resource",
            "resource_information": {
                "id_short": "resource_13_general_information",
                "description": "General Information of resource resource_13 with name F_Sensordeckel_Montage1",
                "id": "resource_13_general_information",
                "semantic_id": "",
                "name": None,
                "manufacturer": "Bosch",
                "production_level": "Station",
                "resource_type": "Manufacturing"
            },
            "capabilities": {
                "id_short": "resource_13_capabilities",
                "description": "Capabilties of resource resource_13",
                "id": "resource_13_capabilities",
                "semantic_id": "",
                "procedures_ids": [
                    "task_1135_process_time_1206_procedure",
                    "task_1136_process_time_1207_procedure",
                    "task_1137_process_time_1208_procedure",
                    "task_1138_process_time_1209_procedure",
                    "task_1139_process_time_1210_procedure",
                    "task_1140_process_time_1211_procedure",
                    "task_1141_process_time_1212_procedure",
                    "task_1142_process_time_1213_procedure",
                    "task_1143_process_time_1214_procedure",
                    "task_1144_process_time_1215_procedure",
                    "task_1145_process_time_1216_procedure",
                    "task_1146_process_time_1217_procedure",
                    "resource_13_resource_availibility_15_breakdown_procedure",
                    "resource_13_resource_availibility_15_maintenance_procedure"
                ]
            },
            "construction_data": {
                "id_short": "resource_13_construction_data",
                "description": "Construction data of resource resource_13 with name F_Sensordeckel_Montage1",
                "id": "resource_13_construction_data",
                "semantic_id": "",
                "cad_file": "CESA3R",
                "photo_file": None
            },
            "resource_configuration": {
                "id_short": "resource_13_resource_configuration",
                "description": "Resource configuration of resource resource_13 with name F_Sensordeckel_Montage1",
                "id": "resource_13_resource_configuration",
                "semantic_id": "",
                "sub_resources": [
                    {
                        "id_short": "resource_13_subresource_Sensordeckel_Montage",
                        "description": "Subresource of resource resource_13 with name F_Sensordeckel_Montage1",
                        "semantic_id": "",
                        "resource_id": "resource_13_module_Sensordeckel_Montage",
                        "position": [
                            -1.0,
                            -1.0
                        ],
                        "orientation": [
                            -1.0
                        ]
                    }
                ],
                "resource_links": None,
                "status": {
                    "id_short": "resource_13_status",
                    "description": "Status of resource resource_13 with name F_Sensordeckel_Montage1",
                    "semantic_id": "",
                    "status": "StandBy",
                    "status_start": None
                }
            },
            "control_logic": {
                "id_short": "resource_13_control_logic",
                "description": "Control logic of resource resource_13 with name F_Sensordeckel_Montage1",
                "id": "resource_13_control_logic",
                "semantic_id": "",
                "sequencing_policy": "FIFO",
                "routing_policy": None
            },
            "resource_interface": None,
            "resource_performances": None,
            "resource_location_history": None,
            "product_reference": None
        },
            ]
        }
    }

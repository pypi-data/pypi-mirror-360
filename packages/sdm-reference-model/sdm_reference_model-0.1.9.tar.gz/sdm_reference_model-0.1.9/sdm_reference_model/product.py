from __future__ import annotations
from enum import Enum

from typing import Optional, List

from aas_pydantic import AAS, Submodel, SubmodelElementCollection

from sdm_reference_model.procedure import Event


class ProductUseType(str, Enum):
    """
    Enum to describe how a subproduct is used in the product.
    """

    ASSEMBLED = "assembled"
    UNASSEMBLED = "unassembled"
    CONSUMED = "consumed"


class SubProduct(SubmodelElementCollection):
    """
    SubmodelElementCollection to describe a subproduct of a product with reference to its AAS, status informatino and quantity.

    Args:
        description (Optional[str]): The description of the subproduct.
        id_short (Optional[str]): The short id of the subproduct.
        semantic_id (Optional[str]): The semantic id of the subproduct.
        product_type (str): The type of the subproduct.
        product_id (str): The AAS reference of the subproduct.
        status (Literal["assembled", "unassembled"]): The status of the subproduct.
        quantity (int): The quantity of the subproduct(s).
    """

    product_type: str
    product_id: str
    product_use_type: ProductUseType
    quantity: int


class BOM(Submodel):
    """
    Submodel to describe the bill of materials of a product.

    Args:
        id (str): The id of the bill of materials.
        description (Optional[str]): The description of the bill of materials.
        id_short (Optional[str]): The short id of the bill of materials.
        semantic_id (Optional[str]): The semantic id of the bill of materials.
        sub_product_count (Optional[int]): The total number of subproducts (depht 1)
        sub_products (Optional[List[SubmodelElementCollection]]): The list of subproducts contained in the product (depht 1)
    """

    sub_product_count: Optional[int] = None
    sub_products: Optional[List[SubProduct]] = None


class ProcessReference(Submodel):
    """
    Submodel to reference process to create a product.

    Args:
        id (str): The id of the process reference.
        description (Optional[str]): The description of the process reference.
        id_short (Optional[str]): The short id of the process reference.
        semantic_id (Optional[str]): The semantic id of the process reference.
        process_id (str): reference to the process to create the product
        alternative_process_ids (Optional[List[str]]): alternative processes to create the product
    """

    process_id: str  # reference to the process to create the product
    alternative_processes_ids: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "workplan_0_process_reference",
                    "description": "Process Reference for product TTN01",
                    "id": "workplan_0_process_reference",
                    "semantic_id": "",
                    "process_id": "process_0",
                    "alternative_process_ids": ["process_1", "process_2"],
                }
            ]
        }
    }


class ConstructionData(Submodel):
    """
    Submodel to describe the construction data of a product.

    Args:
        id (str): The id of the construction data.
        description (Optional[str]): The description of the construction data.
        id_short (Optional[str]): The short id of the construction data.
        semantic_id (Optional[str]): The semantic id of the construction data.
        cad_file (Optional[str]): IRI to a CAD file of the product.
    """

    cad_file: Optional[str] = None
    photo_file: Optional[str] = None

class GreenHouseGasEmission(SubmodelElementCollection):
    """
    Submodel collection containing information about the greenhouse gas emission of a procedure in kilogram of CO2-equivalents.

    Args:
        emission_scope_one (Optional[float]): The greenhouse gas emission of scope 1.
        emission_scope_two (Optional[float]): The greenhouse gas emission of scope 2.
        emission_scope_three (Optional[float]): The greenhouse gas emission of scope 3.
    """

    emission_scope_one: Optional[float] = None
    emission_scope_two: Optional[float] = None
    emission_scope_three: Optional[float] = None


class ProductInformation(Submodel):
    """
    Submodel to describe general information of the product.

    Args:
        id (str): The id of the product general information.
        description (Optional[str]): The description of the product general information.
        id_short (Optional[str]): The short id of the product general information.
        semantic_id (Optional[str]): The semantic id of the product general information.
        product_type (str): The type of the product.
        manufacturer (str): The manufacturer of the product.
    """

    product_type: Optional[str] = None
    manufacturer: Optional[str] = None
    name: Optional[str] = None
    maintenance_manual: Optional[str] = None
    operating_manual: Optional[str] = None
    disassembly_manual: Optional[str] = None
    green_house_gas_emission: Optional[GreenHouseGasEmission] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "workplan_0_general_information",
                    "description": "General Information for product TTN01",
                    "id": "workplan_0_general_information",
                    "semantic_id": "",
                    "product_type": None,
                    "manufacturer": "Bosch GmbH",
                    "name": "TTN01",
                    "maintenance_manual": None,
                    "operating_manual": None,
                    "disassembly_manual": None,
                    "green_house_gas_emission": None,
                }
            ]
        }
    }


class TrackingData(Submodel):
    """
    Submodel to describe tracking data of a product.

    Args:
        id (str): The id of the tracking data.
        description (Optional[str]): The description of the tracking data.
        id_short (Optional[str]): The short id of the tracking data.
        semantic_id (Optional[str]): The semantic id of the tracking data.
        execution_log (Optional[List[Event]]): The execution log of the product containing all events of the product.
    """

    execution_log: Optional[List[Event]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "workplan_0_tracking_data",
                    "description": "Tracking data of product TTN01",
                    "id": "workplan_0_tracking_data",
                    "semantic_id": "",
                    "execution_log": [
                        {
                            "id_short": "id_0011b3c034d911f0a04a845cf38935ae",
                            "description": "",
                            "semantic_id": "",
                            "time": "2025-04-23T23:26:05+00:00",
                            "resource_id": "resource_2003_resource",
                            "procedure_id": "task_2010_process_time_3009_procedure",
                            "procedure_type": "Production",
                            "activity": "Start",
                            "product_id": "job_3239_order_workplan_10_product_1",
                            "expected_end_time": "2025-04-23T23:27:11+00:00",
                            "actual_end_time": None,
                            "success": None,
                        },
                        {
                            "id_short": "id_0011b3c334d911f083ec845cf38935ae",
                            "description": "",
                            "semantic_id": "",
                            "time": "2025-04-23T23:30:09+00:00",
                            "resource_id": "resource_2003_resource",
                            "procedure_id": "task_2010_process_time_3009_procedure",
                            "procedure_type": "Production",
                            "activity": "Start",
                            "product_id": "job_3242_order_workplan_10_product_1",
                            "expected_end_time": "2025-04-23T23:31:15+00:00",
                            "actual_end_time": None,
                            "success": None,
                        },
                    ],
                }
            ]
        }
    }


class ProductCostStructure(Submodel):
    """
    Submodel to describe the cost structure of a product during the complete lifecycle of the product.

    Args:
        id (str): The id of the cost structure.
        description (Optional[str]): The description of the cost structure.
        id_short (Optional[str]): The short id of the cost structure.
        semantic_id (Optional[str]): The semantic id of the cost structure.
        material_cost (Optional[float]): The material cost of the product.
        labor_cost (Optional[float]): The labor cost of the product.
        manufacturing_cost (Optional[float]): The manufacturing cost of the product.
        administrative_cost (Optional[float]): The administrative cost of the product.
        energy_cost (Optional[float]): The energy cost of the product during its lifecycle.
        disposal_cost (Optional[float]): The disposal cost of the product.
        maintenance_cost (Optional[float]): The maintenance cost of the product during its lifecycle.
        recycling_cost (Optional[float]): The recycling cost of the product.
        other_cost (Optional[float]): Other costs of the product.
    """

    material_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    manufacturing_cost: Optional[float] = None
    administrative_cost: Optional[float] = None

    energy_cost: Optional[float] = None
    disposal_cost: Optional[float] = None
    maintenance_cost: Optional[float] = None
    recycling_cost: Optional[float] = None
    other_cost: Optional[float] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "workplan_0_cost_structure",
                    "description": "Cost structure of product TTN01",
                    "id": "workplan_0_cost_structure",
                    "semantic_id": "",
                    "material_cost": 150.0,
                    "labor_cost": 0.0,
                    "manufacturing_cost": 30.0,
                    "administrative_cost": 120.0,
                    "energy_cost": None,
                    "disposal_cost": None,
                    "maintenance_cost": None,
                    "recycling_cost": None,
                    "other_cost": None,
                }
            ]
        }
    }


class Product(AAS):
    """
    AAS to describe a product.

    Args:
        id (str): The id of the product.
        description (Optional[str]): The description of the product.
        id_short (Optional[str]): The short id of the product.
        semantic_id (Optional[str]): The semantic id of the product.
        construction_data (Optional[ConstructionData]): The construction data of the product.
        bom (Optional[BOM]): The bill of materials of the product.
        process_reference (Optional[ProcessReference]): The process reference of the product.

    """

    product_information: Optional[ProductInformation] = None
    construction_data: Optional[ConstructionData] = None
    bom: Optional[BOM] = None
    process_reference: Optional[ProcessReference] = None
    tracking_data: Optional[TrackingData] = None
    cost_structure: Optional[ProductCostStructure] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "workplan_0_product",
                    "description": "Master product of type TTN01 containing all information every product of this type has.",
                    "id": "workplan_0_product",
                    "product_information": {
                        "id_short": "workplan_0_general_information",
                        "description": "General Information for product TTN01",
                        "id": "workplan_0_general_information",
                        "semantic_id": "",
                        "product_type": None,
                        "manufacturer": "Bosch GmbH",
                        "name": "TTN01",
                        "maintenance_manual": None,
                        "operating_manual": None,
                        "disassembly_manual": None,
                        "green_house_gas_emission": None,
                    },
                    "construction_data": None,
                    "bom": None,
                    "process_reference": {
                        "id_short": "workplan_0_process_reference",
                        "description": "Reference to the process to produce product TTN01",
                        "id": "workplan_0_process_reference",
                        "semantic_id": "",
                        "process_id": "workplan_0_process",
                        "alternative_processes_ids": None,
                    },
                    "tracking_data": {
                        "id_short": "workplan_0_tracking_data",
                        "description": "Tracking data of product TTN01",
                        "id": "workplan_0_tracking_data",
                        "semantic_id": "",
                        "execution_log": [
                            {
                                "id_short": "id_0011b3c034d911f0a04a845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-23T23:26:05+00:00",
                                "resource_id": "resource_2003_resource",
                                "procedure_id": "task_2010_process_time_3009_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_3239_order_workplan_10_product_1",
                                "expected_end_time": "2025-04-23T23:27:11+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                            {
                                "id_short": "id_0011b3c334d911f083ec845cf38935ae",
                                "description": "",
                                "semantic_id": "",
                                "time": "2025-04-23T23:30:09+00:00",
                                "resource_id": "resource_2003_resource",
                                "procedure_id": "task_2010_process_time_3009_procedure",
                                "procedure_type": "Production",
                                "activity": "Start",
                                "product_id": "job_3242_order_workplan_10_product_1",
                                "expected_end_time": "2025-04-23T23:31:15+00:00",
                                "actual_end_time": None,
                                "success": None,
                            },
                        ],
                    },
                    "cost_structure": {
                        "id_short": "workplan_0_cost_structure",
                        "description": "Cost structure of product TTN01",
                        "id": "workplan_0_cost_structure",
                        "semantic_id": "",
                        "material_cost": 150.0,
                        "labor_cost": 0.0,
                        "manufacturing_cost": 30.0,
                        "administrative_cost": 120.0,
                        "energy_cost": None,
                        "disposal_cost": None,
                        "maintenance_cost": None,
                        "recycling_cost": None,
                        "other_cost": None,
                    },
                },
            ]
        }
    }

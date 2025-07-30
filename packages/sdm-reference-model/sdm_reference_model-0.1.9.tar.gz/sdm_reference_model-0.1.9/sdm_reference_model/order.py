from typing import List, Optional


from aas_pydantic import AAS, Submodel, SubmodelElementCollection


class GeneralInformation(Submodel):
    """
    Submodel to describe the general information of an order.

    Args:
        id (str): The id of the general information.
        description (Optional[str]): The description of the general information.
        id_short (Optional[str]): The short id of the general information.
        semantic_id (Optional[str]): The semantic id of the general information.
        order_id (str): The id of the order.
        priority (int): The priority of the order.
        customer_information (str): The customer information of the order.
    """

    order_id: str
    priority: int
    customer_information: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "job_1000_order_general_information",
                    "description": "General information of order with id job_1000.",
                    "id": "job_1000_order_general_information",
                    "semantic_id": "",
                    "order_id": "job_1000",
                    "priority": 1,
                    "customer_information": "OEM",
                },
            ]
        }
    }


class OrderedProduct(SubmodelElementCollection):
    """
    Submodel that describes the product instances of an order with reference to their AAS.

    Args:
        description (Optional[str]): The description of the product instances.
        id_short (Optional[str]): The short id of the product instances.
        semantic_id (Optional[str]): The semantic id of the product instances.
        product_type (str): Product type of the order.
        target_quantity (int): Number of requested product instances
        product_ids (List[str]): Reference to the AAS of the product instances of the order.
    """

    product_type: str
    target_quantity: int
    product_ids: Optional[List[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "job_1001_ordered_product",
                    "description": "Ordered product of order with id job_1001.",
                    "semantic_id": "",
                    "product_type": "workplan_0_product",
                    "target_quantity": 1,
                    "product_ids": [],
                }
            ]
        }
    }


class OrderedProducts(Submodel):
    """
    Submodel that describes the product instances of an order with reference to their AAS.

    Args:
        id (str): The id of the product instances.
        description (Optional[str]): The description of the product instances.
        id_short (Optional[str]): The short id of the product instances.
        semantic_id (Optional[str]): The semantic id of the product instances.
        ordered_products (List[OrderedProduct]): The list of ordered products specifying the ordered type and the quantity of the product type. .
    """

    ordered_products: List[OrderedProduct]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "job_1000_ordered_products",
                    "description": "Ordered products of order with id job_1000.",
                    "id": "job_1000_ordered_products",
                    "semantic_id": "",
                    "ordered_products": [
                        {
                            "id_short": "job_1000_ordered_product",
                            "description": "Ordered product of order with id job_1000.",
                            "semantic_id": "",
                            "product_type": "workplan_0_product",
                            "target_quantity": 1,
                            "product_ids": [],
                        }
                    ],
                },
            ]
        }
    }


class OrderSchedule(Submodel):
    """
    Submodel to describe the schedule of an order.

    Args:
        id (str): The id of the order schedule.
        description (Optional[str]): The description of the order schedule.
        id_short (Optional[str]): The short id of the order schedule.
        semantic_id (Optional[str]): The semantic id of the order schedule.
        release_time (str): The release time of the order (ISO 8601 datetime).
        due_time (str): The due time of the order (ISO 8601 datetime).
        target_time (str): The target time of the order (ISO 8601 datetime).
    """

    release_time: str
    due_time: str
    target_time: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "job_1000_order_schedule",
                    "description": "Order schedule of order with id job_1000.",
                    "id": "job_1000_order_schedule",
                    "semantic_id": "",
                    "release_time": "2025-05-23T14:12:36.524179+00:00",
                    "due_time": "2025-05-24T06:12:36.524179+00:00",
                    "target_time": "2025-05-23T22:12:36.524179+00:00",
                },
            ]
        }
    }


class Order(AAS):
    """
    AAS to describe an order.

    Args:
        id (str): The id of the order.
        description (Optional[str]): The description of the order.
        id_short (Optional[str]): The short id of the order.
        general_information (GeneralInformation): The general information of the order.
        order_schedule (OrderSchedule): The schedule of the order.
        ordered_products (OrderedProducts): The ordered products of the order.
    """

    general_information: GeneralInformation
    order_schedule: Optional[OrderSchedule] = None
    ordered_products: Optional[OrderedProducts] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id_short": "job_1000_order",
                    "description": "Order with id job_1000.",
                    "id": "job_1000_order",
                    "general_information": {
                        "id_short": "job_1000_order_general_information",
                        "description": "General information of order with id job_1000.",
                        "id": "job_1000_order_general_information",
                        "semantic_id": "",
                        "order_id": "job_1000",
                        "priority": 1,
                        "customer_information": "OEM",
                    },
                    "order_schedule": {
                        "id_short": "job_1000_order_schedule",
                        "description": "Order schedule of order with id job_1000.",
                        "id": "job_1000_order_schedule",
                        "semantic_id": "",
                        "release_time": "2025-05-23T14:12:36.524179+00:00",
                        "due_time": "2025-05-24T06:12:36.524179+00:00",
                        "target_time": "2025-05-23T22:12:36.524179+00:00",
                    },
                    "ordered_products": {
                        "id_short": "job_1000_ordered_products",
                        "description": "Ordered products of order with id job_1000.",
                        "id": "job_1000_ordered_products",
                        "semantic_id": "",
                        "ordered_products": [
                            {
                                "id_short": "job_1000_ordered_product",
                                "description": "Ordered product of order with id job_1000.",
                                "semantic_id": "",
                                "product_type": "workplan_0_product",
                                "target_quantity": 1,
                                "product_ids": [],
                            }
                        ],
                    },
                },
                {
                    "id_short": "job_1001_order",
                    "description": "Order with id job_1001.",
                    "id": "job_1001_order",
                    "general_information": {
                        "id_short": "job_1001_order_general_information",
                        "description": "General information of order with id job_1001.",
                        "id": "job_1001_order_general_information",
                        "semantic_id": "",
                        "order_id": "job_1001",
                        "priority": 1,
                        "customer_information": "OEM",
                    },
                    "order_schedule": {
                        "id_short": "job_1001_order_schedule",
                        "description": "Order schedule of order with id job_1001.",
                        "id": "job_1001_order_schedule",
                        "semantic_id": "",
                        "release_time": "2025-05-23T14:12:36.524179+00:00",
                        "due_time": "2025-05-24T06:12:36.524179+00:00",
                        "target_time": "2025-05-23T22:12:36.524179+00:00",
                    },
                    "ordered_products": {
                        "id_short": "job_1001_ordered_products",
                        "description": "Ordered products of order with id job_1001.",
                        "id": "job_1001_ordered_products",
                        "semantic_id": "",
                        "ordered_products": [
                            {
                                "id_short": "job_1001_ordered_product",
                                "description": "Ordered product of order with id job_1001.",
                                "semantic_id": "",
                                "product_type": "workplan_0_product",
                                "target_quantity": 1,
                                "product_ids": [],
                            }
                        ],
                    },
                },
            ]
        }
    }

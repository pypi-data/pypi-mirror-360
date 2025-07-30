from __future__ import annotations
from typing import Union, Optional, List
from aas_middleware.model.data_model import DataModel, NESTED_DICT

from sdm_reference_model.performance import Performance
from sdm_reference_model.processes import Process
from sdm_reference_model.procedure import Procedure
from sdm_reference_model.product import Product
from sdm_reference_model.resources import Resource
from sdm_reference_model.order import Order
from sdm_reference_model.change_scenario import ChangeScenario


REFERENCE_MODEL_TYPES_LIST = [
    Product,
    Resource,
    Procedure,
    Process,
    Order,
    ChangeScenario,
    Performance,
]


class ReferenceModel(DataModel):
    product: List[Product] = []
    resource: List[Resource] = []
    procedure: List[Procedure] = []
    process: List[Process] = []
    order: List[Order] = []
    performance: List[Performance] = []
    change_scenario: Optional[ChangeScenario] = None

    def from_dict(self, data: NESTED_DICT) -> None:
        # self.super().from_dict(data=data, types=[Product, Resource, Procedure, Process, Order, ChangeScenario])
        # use the from dict of the super class
        super(ReferenceModel, self).from_dict(
            data=data, types=REFERENCE_MODEL_TYPES_LIST
        )
        self.product = self.get_models_of_type(Product)
        self.resource = self.get_models_of_type(Resource)
        self.procedure = self.get_models_of_type(Procedure)
        self.process = self.get_models_of_type(Process)
        self.order = self.get_models_of_type(Order)
        if "performance" in data:
            self.performance = self.get_models_of_type(Performance)
        else:
            self.performance = []
        if "change_scenario" in data:
            self.change_scenario = self.get_models_of_type(ChangeScenario).pop()
        else:
            self.change_scenario = None

    @classmethod
    def from_models(
        cls,
        *models: List[
            Union[Product, Resource, Procedure, Process, Order, ChangeScenario]
        ],
    ) -> ReferenceModel:
        instance = cls()
        for model in models:
            if isinstance(model, Product):
                instance.product.append(model)
            elif isinstance(model, Resource):
                instance.resource.append(model)
            elif isinstance(model, Procedure):
                instance.procedure.append(model)
            elif isinstance(model, Process):
                instance.process.append(model)
            elif isinstance(model, Order):
                instance.order.append(model)
            elif isinstance(model, Performance):
                instance.performance.append(model)
            elif isinstance(model, ChangeScenario):
                instance.change_scenario = model
                continue
            instance.add(model)
        return instance

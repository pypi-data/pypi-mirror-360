import importlib_metadata
import toml
from .product import Product
from .resources import Resource
from .procedure import Procedure
from .processes import Process
from .order import Order
from .performance import Performance
from .change_scenario import ChangeScenario

from .reference_model import ReferenceModel


def get_version() -> str:
    try:
        return importlib_metadata.version("sdm_reference_model")
    except:
        pass
    try:
        pyproject = toml.load("pyproject.toml")
        return pyproject["tool"]["poetry"]["version"]
    except:
        pass
    raise ModuleNotFoundError(
        "Could not find version in package metadata or pyproject.toml"
    )


VERSION = get_version()

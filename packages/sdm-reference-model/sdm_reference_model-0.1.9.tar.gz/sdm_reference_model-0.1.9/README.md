# SDM Reference Model
![PyPI](https://img.shields.io/pypi/v/sdm_reference_model)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sdm_reference_model)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The SDM Reference Model offers a structured framework for modeling a production system and its assets using the Asset Administration Shell (AAS). It provides a standardized way to represent essential components such as products, resources, procedures, processes, orders, and change scenarios.

This model aligns with the ISA 95 and ISA 88 standards, ensuring compatibility with established hierarchies and production systems modeling principles. Specifically:
- **ISA 95**: Defines a hierarchy for the structure of production systems, including levels like enterprise, site, area, work center, and workstation.
- **ISA 88**: Focuses on batch control and gives a basis for process modeling.^^

## Features

The SDM Reference Model:
- Enables hierarchical modeling of production systems.
- Supports detailed descriptions of operations on a shop floor based on products, processes, procedures, and resources.
- Allows to consider data for automation (device and material interfaces) and sustainability (energy consumption, emissions).
- Facilitates serialization to AAS for integration into Industry 4.0 frameworks.

## Installation

Install the reference model with the following command:

```sh
pip install sdm-reference-model
```

**Requirements**:
- Python 3.10 or higher.

## Modeling a Production System

To model a production system, define components such as:
1. **Products**: Define materials, intermediate goods, and finished products.
2. **Resources**: Represent physical or virtual assets like machines, stations, or tools.
3. **Procedures**: Model execution of resource operations.
4. **Processes**: Define workflows and sequences of operations demanded by a product.

### Example Script

The following script demonstrates how to:
1. Define products, resources, and procedures.
2. Combine these components into a reference model.
3. Serialize the model to JSON and AAS formats.

```python
from datetime import datetime
import json
from pathlib import Path
import uuid

import aas_middleware
from sdm_reference_model import product, procedure, resources
from sdm_reference_model.reference_model import ReferenceModel

# Define a production procedure
procedure_1 = procedure.Procedure(
    id="Pressen_1_Manuell",
    description="Manual Press Operation 1",
    procedure_information=procedure.ProcedureInformation(
        id="Pressen_1_manuell_Information",
        description="Information about Manual Press Operation 1",
        procedure_type=procedure.ProcedureTypeEnum.PRODUCTION,
    ),
    process_attributes=None,
    execution_model=procedure.ExecutionModel(
        id="Pressen_1_manuell_Execution_Model",
        description="Execution model for Manual Press Operation 1",
        execution_log=[
            procedure.Event(
                id_short="u" + str(uuid.uuid1()).replace("-", "_"),
                time=datetime.now().isoformat(),
                resource_id="Station_Pressen_1_Manuell",
                procedure_id="Pressen_1_Manuell",
                product_id="Stellmotor_12334"
            ),
        ],
    ),
)

# Define a product
stell_motor_12334 = product.Product(
    id="Stellmotor_12334",
    description="Actuator Motor 12334",
    product_information=product.ProductInformation(
        id="Stellmotor_12334_Information",
        manufacturer="Manufacturer A",
    ),
)

# Define a resource
resource_1 = resources.Resource(
    id="Station_Pressen_1_Manuell",
    description="Manual Press Station 1",
    resource_information=resources.ResourceInformation(
        id="Station_Pressen_1_Manuell_Information",
        description="Details about Manual Press Station 1",
        manufacturer="wbk Institut für Produktionstechnik",
        production_level="Station",
        resource_type="Manufacturing",
    ),
    product_reference=resources.ProductReference(
        id="Station_Pressen_1_Manuell_Product_Reference",
        description="Reference to products handled at Manual Press Station 1",
        product_reference_id="wbk_manuelle_Pressstation",
    ),
)

# Combine components
products = [stell_motor_12334]
procedures = [procedure_1]
resources = [resource_1]

# Create a reference model
all_components = procedures + resources + products
reference_model = ReferenceModel.from_models(*all_components)

# Serialize to JSON
output_dir = Path(__file__).parent / "examples"
output_dir.mkdir(exist_ok=True)

with open(output_dir / "pydantic_reference_model.json", "w") as f:
    f.write(reference_model.json())

# Serialize to AAS JSON format
aas_json = aas_middleware.formatting.AasJsonFormatter().serialize(reference_model)
with open(output_dir / "aas_reference_model.json", "w") as f:
    f.write(json.dumps(aas_json, indent=4))
```

### Output

The script generates the following files in the `examples` directory:
1. **`pydantic_reference_model.json`**: The reference model serialized as plain JSON.
2. **`aas_reference_model.json`**: The reference model serialized in AAS-compliant JSON format.

## Conclusion

The SDM Reference Model provides a robust framework for modeling production systems aligned with industry standards. Its serialization to AAS ensures interoperability in Industry 4.0 ecosystems. Extend the example script to include additional components and customize the reference model as needed. 

## License

This project is licensed under the MIT License.
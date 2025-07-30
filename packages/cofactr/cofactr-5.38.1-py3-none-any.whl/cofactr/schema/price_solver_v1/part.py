"""Part class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.price_solver_v0.part import Part as PriceSolverV0Part


@dataclass
class Part(PriceSolverV0Part):  # pylint: disable=too-many-instance-attributes
    """Part."""

    lifecycle_status: str

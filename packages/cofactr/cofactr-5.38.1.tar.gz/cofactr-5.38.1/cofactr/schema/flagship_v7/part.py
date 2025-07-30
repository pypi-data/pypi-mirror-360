"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_v6.part import Part as FlagshipV6Part


@dataclass
class Part(FlagshipV6Part):
    """Part."""

    fresh_data_at: Optional[str]

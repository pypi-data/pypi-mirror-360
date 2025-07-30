"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List, Optional

# Local Modules
from cofactr.schema.flagship_v4.part import Part as FlagshipV4Part


@dataclass
class Part(FlagshipV4Part):
    """Part."""

    owner_id: Optional[str]
    custom_id: Optional[str]
    deprecated_custom_ids: List[str]

"""Part seller class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship.seller import Seller as FlagshipSeller

@dataclass
class Seller(FlagshipSeller):
    """Part seller."""

    best_case_lead: Optional[int]

"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List, Optional

# Local Modules
from cofactr.schema.flagship_v5.part import Part as FlagshipV5Part


@dataclass
class Part(FlagshipV5Part):
    """Part."""

    median_factory_lead_days: Optional[int]
    num_authed_distributors_with_offers: int
    num_authed_distributors_with_offers_current_stock: int
    num_distributors_with_offers_current_stock: int

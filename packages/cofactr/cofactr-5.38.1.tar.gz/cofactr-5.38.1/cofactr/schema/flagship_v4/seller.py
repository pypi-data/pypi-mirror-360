"""Part seller class."""
# Standard Modules
from dataclasses import dataclass
from typing import List, Optional

# Local Modules
from cofactr.schema.flagship_v3.seller import Seller as FlagshipV3Seller


@dataclass
class Seller(FlagshipV3Seller):
    """Part seller."""

    deprecated_ids: List[str]
    convenience_return_window: Optional[int]  # Days.
    scheduled_release_period: Optional[int]  # Months.

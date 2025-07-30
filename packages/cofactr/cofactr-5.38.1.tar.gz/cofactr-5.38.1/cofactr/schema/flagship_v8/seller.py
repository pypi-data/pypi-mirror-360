"""Part seller class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_v7.seller import Seller as FlagshipV7Seller


@dataclass
class Seller(FlagshipV7Seller):
    """Part seller."""

    custom_reel_price: Optional[float]

"""Part seller class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.schema.flagship_v5.seller import Seller as FlagshipV5Seller


@dataclass
class Seller(FlagshipV5Seller):
    """Part seller."""

    us_shipping_methods: List[str]
    international_shipping_methods: List[str]

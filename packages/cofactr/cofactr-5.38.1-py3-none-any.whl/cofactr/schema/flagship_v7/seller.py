"""Part seller class."""
# Standard Modules
from dataclasses import dataclass
from typing import Dict

# Local Modules
from cofactr.schema.flagship_v6.seller import Seller as FlagshipV6Seller

# Shipping method label -> lead time.
PlatformShippingMethods = Dict[str, int]

@dataclass
class Seller(FlagshipV6Seller):
    """Part seller."""

    us_shipping_methods: PlatformShippingMethods
    international_shipping_methods: PlatformShippingMethods

"""Part seller class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_v2.seller import Seller as FlagshipV2Seller

@dataclass
class Seller(FlagshipV2Seller):
    """Part seller."""

    overlap: bool

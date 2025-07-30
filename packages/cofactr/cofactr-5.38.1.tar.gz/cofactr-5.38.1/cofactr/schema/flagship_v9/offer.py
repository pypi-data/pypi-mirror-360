"""Part offer class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_v8.offer import Offer as FlagshipV8Offer
from cofactr.schema.flagship_v8.seller import Seller as FlagshipV8Seller


@dataclass
class Offer(FlagshipV8Offer):
    """Part offer."""

    seller: FlagshipV8Seller

    custom_reel_sku: Optional[str]

    def __post_init__(self):
        """Convert types."""

        self.seller = FlagshipV8Seller(**self.seller)  # pylint: disable=not-a-mapping

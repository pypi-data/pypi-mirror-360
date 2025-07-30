"""Part offer class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.flagship_v7.offer import Offer as FlagshipV7Offer
from cofactr.schema.flagship_v7.seller import Seller as FlagshipV7Seller


@dataclass
class Offer(FlagshipV7Offer):
    """Part offer."""

    seller: FlagshipV7Seller

    def __post_init__(self):
        """Convert types."""

        self.seller = FlagshipV7Seller(**self.seller)  # pylint: disable=not-a-mapping

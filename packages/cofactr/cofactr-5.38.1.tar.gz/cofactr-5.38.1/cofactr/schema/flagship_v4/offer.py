"""Part offer class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.flagship_v3.offer import Offer as FlagshipV3Offer
from cofactr.schema.flagship_v3.seller import Seller as FlagshipV3Seller


@dataclass
class Offer(FlagshipV3Offer):
    """Part offer."""

    seller: FlagshipV3Seller
    overlap: bool

    def __post_init__(self):
        """Convert types."""

        self.seller = FlagshipV3Seller(**self.seller)  # pylint: disable=not-a-mapping

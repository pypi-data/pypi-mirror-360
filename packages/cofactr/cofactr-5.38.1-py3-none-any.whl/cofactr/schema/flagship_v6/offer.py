"""Part offer class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.flagship_v5.offer import Offer as FlagshipV5Offer
from cofactr.schema.flagship_v5.seller import Seller as FlagshipV5Seller


@dataclass
class Offer(FlagshipV5Offer):
    """Part offer."""

    seller: FlagshipV5Seller

    def __post_init__(self):
        """Convert types."""

        self.seller = FlagshipV5Seller(**self.seller)  # pylint: disable=not-a-mapping

"""Part offer class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.flagship_v6.offer import Offer as FlagshipV6Offer
from cofactr.schema.flagship_v6.seller import Seller as FlagshipV6Seller


@dataclass
class Offer(FlagshipV6Offer):
    """Part offer."""

    seller: FlagshipV6Seller

    def __post_init__(self):
        """Convert types."""

        self.seller = FlagshipV6Seller(**self.seller)  # pylint: disable=not-a-mapping

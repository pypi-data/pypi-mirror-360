"""Part offer class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_v4.offer import Offer as FlagshipV4Offer
from cofactr.schema.flagship_v4.seller import Seller as FlagshipV4Seller


@dataclass
class Offer(FlagshipV4Offer):
    """Part offer."""

    seller: FlagshipV4Seller
    convenience_return_window: Optional[int]  # Days.
    scheduled_release_period: Optional[int]  # Months.

    def __post_init__(self):
        """Convert types."""

        self.seller = FlagshipV4Seller(**self.seller)  # pylint: disable=not-a-mapping

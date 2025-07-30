"""Part offer class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.flagship_v2.offer import Offer as FlagshipV2Offer
from cofactr.schema.flagship_v2.seller import Seller


@dataclass
class Offer(FlagshipV2Offer):
    """Part offer."""

    seller: Seller
    # Is the part on backorder?
    is_backordered: bool
    # Indicates that we aren't sure the lead is correct because of factors like
    # master distributor relationships.
    is_uncertain_lead: bool

    def __post_init__(self):
        """Convert types."""

        self.seller = Seller(**self.seller)  # pylint: disable=not-a-mapping

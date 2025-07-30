"""Part seller class."""
# Standard Modules
from dataclasses import dataclass

# Local Modules
from cofactr.schema.flagship_v4.seller import Seller as FlagshipV4Seller


@dataclass
class Seller(FlagshipV4Seller):
    """Part seller."""

    # Does the API support placing new orders for this seller?
    is_api_ordering_supported: bool
    # Does the API support checking the status of existing orders for this seller?
    is_api_order_status_supported: bool

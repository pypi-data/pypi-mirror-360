"""Order class."""
# pylint: disable=not-a-mapping
# Standard Modules
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Error:
    """Error."""

    code: Optional[str]
    message: Optional[str]
    name: Optional[str]


@dataclass
class ScheduledRelease:
    """Scheduled release."""

    scheduled_date: Optional[str]
    scheduled_quantity: Optional[int]


@dataclass
class OrderStatusLine:
    """Order status line."""

    line_id: str
    customer_reference: Optional[str]
    cofactr_product_id: Optional[str]
    seller_product_id: Optional[str]
    quantity_ordered: Optional[int]
    quantity_shipped: Optional[int]
    quantity_backordered: Optional[int]
    country_of_origin: Optional[str]
    backorder_schedule: List[ScheduledRelease]
    schedule: List[ScheduledRelease]

    def __post_init__(self):
        """Convert types."""

        self.backorder_schedule = [
            ScheduledRelease(**schedule) for schedule in self.backorder_schedule
        ]
        self.schedule = [ScheduledRelease(**schedule) for schedule in self.schedule]


@dataclass
class PackageItem:
    """Package item."""

    # Line ID of item being shipped.
    line_id: str
    # Quantity in package.
    quantity: Optional[int]


@dataclass
class PackageDetail:
    """Package detail."""

    items: List[PackageItem]
    tracking_url: Optional[str]
    tracking_number: Optional[str]
    # Name of carrier that will deliver the package.
    carrier_name: Optional[str]
    # Method to be used for shipping the order.
    shipping_method: Optional[str]

    def __post_init__(self):
        """Convert types."""

        self.items = [PackageItem(**item) for item in self.items]


@dataclass
class OrderStatus:  # pylint: disable=too-many-instance-attributes
    """Order status."""

    # Unique Cofactr-defined identifier representing the order.
    id: str
    # Identifier representing the order in seller's order management system.
    seller_order_id: str
    # Errors associated with the order.
    errors: List[Error]
    package_details: List[PackageDetail]
    order_status_lines: List[OrderStatusLine]

    def __post_init__(self):
        """Convert types."""

        self.errors = [Error(**error) for error in self.errors]
        self.package_details = [
            PackageDetail(**detail) for detail in self.package_details
        ]
        self.order_status_lines = [
            OrderStatusLine(**line) for line in self.order_status_lines
        ]

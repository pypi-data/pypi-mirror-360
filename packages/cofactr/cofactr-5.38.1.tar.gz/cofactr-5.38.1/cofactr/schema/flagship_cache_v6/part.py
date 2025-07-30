"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_cache_v5.part import Part as FlagshipCacheV5Part


@dataclass
class Part(FlagshipCacheV5Part):  # pylint: disable=too-many-instance-attributes
    """Part."""

    aecq_status: str
    buyable: int
    multisourcing: int
    multisourcing_current: int
    reach_status: str
    rohs_status: str
    median_factory_lead_days: Optional[str]

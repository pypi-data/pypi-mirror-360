"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_cache_v2.part import Part as FlagshipCacheV2Part


@dataclass
class Part(FlagshipCacheV2Part):  # pylint: disable=too-many-instance-attributes
    """Part."""

    min_lead: Optional[int]

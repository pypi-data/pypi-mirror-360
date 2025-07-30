"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.schema.flagship_cache_v3.part import Part as FlagshipCacheV3Part


@dataclass
class Part(FlagshipCacheV3Part):  # pylint: disable=too-many-instance-attributes
    """Part."""

    alt_mpns: List[str]

"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional

# Local Modules
from cofactr.schema.flagship_cache_v0.part import Part as FlagshipCacheV0Part


@dataclass
class Part(FlagshipCacheV0Part):  # pylint: disable=too-many-instance-attributes
    """Part."""

    deprecated_by: Optional[str]

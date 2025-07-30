"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List, Optional

# Local Modules
from cofactr.schema.flagship_cache_v1.part import Part as FlagshipCacheV1Part


@dataclass
class Part(FlagshipCacheV1Part):  # pylint: disable=too-many-instance-attributes
    """Part."""

    owner_id: Optional[str]
    custom_id: Optional[str]
    deprecated_custom_ids: List[str]

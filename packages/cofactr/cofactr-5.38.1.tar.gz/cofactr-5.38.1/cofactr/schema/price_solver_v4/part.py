"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.schema.flagship_v2.offer import Offer as FlagshipV2Offer
from cofactr.schema.flagship_v6.part import Part as FlagshipV6Part


@dataclass
class Part(FlagshipV6Part):
    """Part."""

    offers: List[FlagshipV2Offer]

    def __post_init__(self):
        """Post initialization."""

        self.mfg = self.mfr
        self.offers = [FlagshipV2Offer(**offer) for offer in self.offers]

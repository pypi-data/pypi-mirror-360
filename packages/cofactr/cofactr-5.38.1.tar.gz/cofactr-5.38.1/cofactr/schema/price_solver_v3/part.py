"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.schema.flagship_v2.offer import Offer as FlagshipV2Offer
from cofactr.schema.flagship_v5.part import Part as FlagshipV5Part


@dataclass
class Part(FlagshipV5Part):
    """Part."""

    offers: List[FlagshipV2Offer]

    def __post_init__(self):
        """Post initialization."""

        self.mfg = self.mfr
        self.offers = [FlagshipV2Offer(**offer) for offer in self.offers]

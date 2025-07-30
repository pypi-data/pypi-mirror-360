"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List

# Local Modules
from cofactr.schema.flagship_v6.offer import Offer as FlagshipV6Offer
from cofactr.schema.flagship_v7.part import Part as FlagshipV7Part


@dataclass
class Part(FlagshipV7Part):
    """Part."""

    offers: List[FlagshipV6Offer]

    def __post_init__(self):
        """Post initialization."""

        self.mfg = self.mfr
        self.offers = [FlagshipV6Offer(**offer) for offer in self.offers]

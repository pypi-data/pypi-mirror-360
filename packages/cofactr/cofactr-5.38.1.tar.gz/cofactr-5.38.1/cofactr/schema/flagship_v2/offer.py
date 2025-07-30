"""Part offer class."""
# Standard Modules
from dataclasses import dataclass
from typing import Dict

# Local Modules
from cofactr.schema.flagship.offer import Offer as FlagshipOffer
from cofactr.schema.types import OfferCorrection


@dataclass
class Offer(FlagshipOffer):
    """Part offer."""

    corrections: Dict[str, OfferCorrection]

"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import List, Literal, Optional, TypedDict

Source = Literal["nexar", "digikey"]

class SuggestedAlt(TypedDict):
    """Offer correction."""

    id: str
    sources: List[Source]

@dataclass
class Part:  # pylint: disable=too-many-instance-attributes
    """Part."""

    owner_id: Optional[str]
    id: str
    deprecated_ids: List[str]
    suggested_alts: List[SuggestedAlt]

"""Part class."""
# Standard Modules
from dataclasses import dataclass
from typing import Optional


@dataclass
class Part:  # pylint: disable=too-many-instance-attributes
    """Part."""

    id: str

    created_at: str
    modified_at: str

    mpn: Optional[str]
    mfr: Optional[str]
    hero_image: Optional[str]
    classification: Optional[str]
    description: Optional[str]
    package: Optional[str]
    terminations: Optional[int]
    termination_type: str
    lifecycle_status: str

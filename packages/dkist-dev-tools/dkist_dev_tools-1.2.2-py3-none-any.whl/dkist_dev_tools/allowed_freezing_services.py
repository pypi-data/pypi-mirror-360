"""Controlled set of DKIST repos that are suppoed to be frozen."""
from enum import StrEnum


class FrozenServices(StrEnum):
    """Controlled set of repos that need freezing."""

    VBI = "dkist-processing-vbi"
    VISP = "dkist-processing-visp"
    CRYONIRSP = "dkist-processing-cryonirsp"
    DLNIRSP = "dkist-processing-dlnirsp"
    TEST = "dkist-processing-test"
    OPS = "dkist-processing-ops"

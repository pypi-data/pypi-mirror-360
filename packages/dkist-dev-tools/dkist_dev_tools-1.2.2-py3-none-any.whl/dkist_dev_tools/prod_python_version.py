"""
Hard-code the version of python running on PROD.

The freeze dependency script *must* be run in an environment that matches this major.minor version.
"""
from dataclasses import dataclass


@dataclass
class ProdPythonVersion:
    """Container for currently-used version of python on PROD."""

    major: int = 3
    minor: int = 11

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


PROD_PYTHON_VERSION = ProdPythonVersion()

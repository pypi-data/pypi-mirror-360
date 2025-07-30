"""Parser of version strings to ensure a leading 'v' is dealt with correctly."""
from dataclasses import dataclass

import click
from packaging import version
from packaging.version import InvalidVersion


@dataclass
class Version:
    """Container for raw and v-prefixed version strings."""

    raw_version: str
    v_version: str


class VersionType(click.ParamType):
    """Click parameter type that parses a string as a `Version` object."""

    name = "version"

    def convert(self, value: str, param: str, context) -> Version:
        """
        Convert a string to a `Version` by ensuring we have both raw and v-prefixed version names.

        Also validate that the raw version is a valid Semantic Version.
        """
        raw_version = value.replace("v", "")
        try:
            version.parse(raw_version)
        except InvalidVersion:
            self.fail(f"Raw version '{raw_version}' is not a valid version specifier")
        v_version = f"v{raw_version}"
        return Version(raw_version=raw_version, v_version=v_version)


VERSION_TYPE = VersionType()

import pytest
from click import BadParameter

from dkist_dev_tools.version_type import VERSION_TYPE


@pytest.mark.parametrize(
    "input, raw_version, v_version",
    [
        pytest.param("v1.2.3", "1.2.3", "v1.2.3", id="v1.2.3"),
        pytest.param("1.2.3", "1.2.3", "v1.2.3", id="1.2.3"),
        pytest.param("v2.3.4rc1", "2.3.4rc1", "v2.3.4rc1", id="v2.3.4rc1"),
    ],
)
def test_version_type(input, raw_version, v_version):
    """
    Given: A raw version str with either a prefix "v" or not
    When: Parsing the version with VERSION_TYPE
    Then: The `raw_version` and `v_version` attributes are correctly parsed
    """
    parsed_version = VERSION_TYPE(input)
    assert parsed_version.raw_version == raw_version
    assert parsed_version.v_version == v_version


def test_bad_version():
    """
    Given: A bad version string
    When: Parsing the version with VERSION_TYPE
    Then: The correct error is raised
    """
    with pytest.raises(BadParameter, match="Raw version 'foo' is not a valid version specifier"):
        VERSION_TYPE("foo")

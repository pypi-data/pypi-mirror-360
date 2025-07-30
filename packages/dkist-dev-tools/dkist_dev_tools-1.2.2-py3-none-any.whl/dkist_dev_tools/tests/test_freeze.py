import tomllib
from collections import namedtuple
from subprocess import Popen

import pytest

from dkist_dev_tools.freeze_dependencies import check_python_version
from dkist_dev_tools.freeze_dependencies import update_pyproject_toml_dependencies
from dkist_dev_tools.prod_python_version import PROD_PYTHON_VERSION

DUMMY_PYPROJECT_TOML_TEMPLATE = """[tool]

[project]
dynamic = ["version"]
name = "{package_name}"
requires-python = ">=3.11"
description = "Test package for dkist-dev-tools tests"
authors = [ {{name = "NSO / AURA", email = "dkistdc@nso.edu"}} ]
license = {{text = "BSD-3-Clause"}}
classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "click",
    "rich",
]

[project.optional-dependencies]
"""


@pytest.fixture
def allowed_repo_dummy_toml():
    return DUMMY_PYPROJECT_TOML_TEMPLATE.format(package_name="dkist-processing-test")


@pytest.fixture
def unallowed_repo_dummy_toml():
    return DUMMY_PYPROJECT_TOML_TEMPLATE.format(package_name="foo-bar")


@pytest.mark.parametrize(
    "version, run_from_project_dir",
    [
        pytest.param("v6.2.8", True, id="vVersion-run_from_dir"),
        pytest.param("v6.2.8", False, id="vVersion-dir_option"),
        pytest.param("6.2.8", True, id="rawVersion"),
    ],
)
def test_freeze_cli(
    package_dir,
    init_package_pyproject,
    allowed_repo_dummy_toml,
    version,
    run_from_project_dir,
    tmp_path_factory,
):
    """
    Given: A package dir with a valid pyproject.toml
    When: Using the cli to freeze dependencies to a given version
    Then: The pyproject.toml is updated with a version stamp in the "tools.dkist-dev-tools.version" node
          and a list of frozen deps under "project.optional-dependencies.frozen".
    """
    package_pyproject = init_package_pyproject(allowed_repo_dummy_toml)
    args = [version]
    run_path = package_dir
    if not run_from_project_dir:
        args = ["-d", str(package_dir)] + args
        run_path = tmp_path_factory.mktemp("process_path")

    p = Popen(args=["ddt", "freeze"] + args, cwd=run_path)

    p.wait()
    assert p.returncode == 0

    with open(package_pyproject, "rb") as f:
        new_pyproject = tomllib.load(f)
        assert new_pyproject["tool"]["dkist-dev-tools"]["version"] == version.replace("v", "")
        frozen_deps = new_pyproject["project"]["optional-dependencies"]["frozen"]
        for dep in frozen_deps:
            assert "==" in dep
            if "dkist-processing-test" in dep:
                assert dep == f"dkist-processing-test == {version.replace('v', '')}"


def test_freeze_correct(package_dir, allowed_repo_dummy_toml, init_package_pyproject):
    """
    Given: A package dir with a valid pyproject.toml
    When: Freezing dependencies to a given version by calling the underlying functions directly
    Then: The pyproject.toml is updated with a version stamp in the "tools.dkist-dev-tools.version" node
          and a list of frozen deps under "project.optional-dependencies.frozen".
    """
    package_pyproject = init_package_pyproject(allowed_repo_dummy_toml)
    version = "6.2.8"
    update_pyproject_toml_dependencies(
        project_dir=package_dir, version=version, skip_allowed_repo_check=False
    )

    with open(package_pyproject, "rb") as f:
        new_pyproject = tomllib.load(f)
        assert new_pyproject["tool"]["dkist-dev-tools"]["version"] == version
        frozen_deps = new_pyproject["project"]["optional-dependencies"]["frozen"]
        for dep in frozen_deps:
            assert "==" in dep
            if "foo-bar" in dep:
                assert dep == f"foo-bar == {version}"


def test_bad_python_version(package_dir, mocker):
    """
    Given: A system where the python version is not equal to the one used in the DC
    When: Checking the python version
    Then: The correct error is raised
    """
    mocked_version_info = namedtuple("mocked_version_info", ["major", "minor"])
    mocker.patch("sys.version_info", mocked_version_info(major=2, minor=7))

    with pytest.raises(
        RuntimeError,
        match=f"Your python version does not match what is used on PROD. You have 2.7, but PROD uses {PROD_PYTHON_VERSION}",
    ):
        check_python_version()


def test_checking_allowed_repo(package_dir, unallowed_repo_dummy_toml, init_package_pyproject):
    """
    Given: A package dir with a valid pyproject.toml that ISN'T one of the official "frozen" repos
    When: Freezing dependencies with the `skip_allowed_repo_check` switch on and off
    Then: If the `skip_allowed_repo_check` is on then freezing happens. If not, the command exits with an error.
    """
    init_package_pyproject(unallowed_repo_dummy_toml)
    version = "6.2.8"
    with pytest.raises(SystemExit, match="1"):
        update_pyproject_toml_dependencies(
            project_dir=package_dir, version=version, skip_allowed_repo_check=False
        )

    update_pyproject_toml_dependencies(
        project_dir=package_dir, version=version, skip_allowed_repo_check=True
    )

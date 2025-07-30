import shutil
from subprocess import Popen

import pytest

if shutil.which("git") is None:
    raise ProcessLookupError("Could not find a 'git' executable in your path")


@pytest.fixture
def frozen_raw_version():
    return "6.6.6"


@pytest.fixture
def frozen_package_pyproject(init_package_pyproject, frozen_raw_version):
    frozen_toml_str = f"""[tool.dkist-dev-tools]
# Most recently frozen version by dkist-dev-tools
version = "{frozen_raw_version}"
date = 2025-01-01T00:00:00.0000

[project]
dynamic = ["version"]
name = "foo-bar"
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
frozen = [
    "click == 8.1.8",
    "rich == 13.9.4",
    "dkist-dev-tools == {frozen_raw_version}",
]
"""
    pyproject_toml = init_package_pyproject(frozen_toml_str)

    return pyproject_toml


@pytest.fixture
def no_dkist_dev_tools_package_pyproject(init_package_pyproject, frozen_raw_version):
    frozen_toml_str = f"""[tool]

[project]
dynamic = ["version"]
name = "foo-bar"
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
frozen = [
    "click == 8.1.8",
    "rich == 13.9.4",
    "dkist-dev-tools == {frozen_raw_version}",
]
"""
    pyproject_toml = init_package_pyproject(frozen_toml_str)

    return pyproject_toml


@pytest.fixture
def no_frozen_deps_package_pyproject(init_package_pyproject, frozen_raw_version):
    frozen_toml_str = f"""[tool.dkist-dev-tools]
# Most recently frozen version by dkist-dev-tools
version = "{frozen_raw_version}"
date = 2025-01-01T00:00:00.0000

[project]
dynamic = ["version"]
name = "foo-bar"
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
    pyproject_toml = init_package_pyproject(frozen_toml_str)

    return pyproject_toml


@pytest.mark.parametrize(
    "BB_tag_set, run_from_project_dir",
    [
        pytest.param(True, True, id="BB_tag"),
        pytest.param(False, True, id="git_tag"),
        pytest.param(True, False, id="BB_tag-dir_option"),
    ],
)
def test_correct_frozen(
    frozen_package_pyproject,
    package_dir,
    frozen_raw_version,
    BB_tag_set,
    run_from_project_dir,
    monkeypatch,
    tmp_path_factory,
):
    """
    Given: A correctly frozen pyproject toml
    When: Checking the freeze
    Then: The command succeeds
    """
    v_version = f"v{frozen_raw_version}"

    if BB_tag_set:
        monkeypatch.setenv("BITBUCKET_TAG", v_version)
    else:
        Popen(["git", "init"], cwd=package_dir).wait()
        Popen(["git", "add", "."], cwd=package_dir).wait()
        Popen(["git", "commit", "-m", "first commit!"], cwd=package_dir).wait()
        Popen(["git", "tag", v_version], cwd=package_dir).wait()

    run_path = package_dir
    args = []
    if not run_from_project_dir:
        args = ["-d", str(package_dir)]
        run_path = tmp_path_factory.mktemp("process_path")

    p = Popen(["ddt", "check", "freeze"] + args, cwd=run_path)
    p.wait()

    assert p.returncode == 0


def test_check_fails_on_wrong_version(
    frozen_package_pyproject, frozen_raw_version, package_dir, monkeypatch
):
    """
    Given: A pyporject toml frozen with a different version than is in BITBUCKET_TAG
    When: Checking the freeze
    Then: The command fails
    """
    bad_version = "v2.3.4"
    assert bad_version.replace("v", "") != frozen_raw_version

    monkeypatch.setenv("BITBUCKET_TAG", bad_version)
    p = Popen(["ddt", "check", "freeze"], cwd=package_dir)
    p.wait()

    assert p.returncode == 1


def test_missing_tool_node(
    no_dkist_dev_tools_package_pyproject, package_dir, frozen_raw_version, monkeypatch
):
    """
    Given: A pyproject toml that is missing the `tool.dkist-dev-tools` node
    When: Checking the freeze
    Then: The command fails
    """
    v_version = f"v{frozen_raw_version}"
    monkeypatch.setenv("BITBUCKET_TAG", v_version)
    p = Popen(["ddt", "check", "freeze"], cwd=package_dir)
    p.wait()

    assert p.returncode == 1


def test_no_frozen_deps(
    no_frozen_deps_package_pyproject, package_dir, frozen_raw_version, monkeypatch
):
    """
    Given: A pyproject toml that has a `tool.dkist-dev-tools` node, but no "frozen" list in `project.optional-dependencies`
    When: Checking the freeze
    Then: The command fails
    """
    v_version = f"v{frozen_raw_version}"
    monkeypatch.setenv("BITBUCKET_TAG", v_version)
    p = Popen(["ddt", "check", "freeze"], cwd=package_dir)
    p.wait()

    assert p.returncode == 1

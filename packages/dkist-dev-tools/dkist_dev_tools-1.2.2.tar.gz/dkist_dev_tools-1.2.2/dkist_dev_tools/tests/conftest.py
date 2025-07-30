import re
from pathlib import Path

import pytest


@pytest.fixture
def wide_terminal(monkeypatch):
    """Mock the terminal size env variable so capturing output does have issues with wrapped lines."""
    monkeypatch.setenv("COLUMNS", "500")


@pytest.fixture
def package_dir(tmp_path_factory) -> Path:
    package_dir = tmp_path_factory.mktemp("package-", numbered=True)
    return package_dir


@pytest.fixture
def init_package_pyproject(package_dir):
    def pyproject_writer(toml_str, project_file_name="pyproject.toml") -> Path:
        pyproject_toml = package_dir / project_file_name
        with open(pyproject_toml, "w") as f:
            f.write(toml_str)
        return pyproject_toml

    return pyproject_writer


def normalize_logged_output(output) -> str:
    """
    Handle line breaks and the traceback info at the end of each line so that terminal size doesn't affect searching
    console output.
    """
    return " ".join(re.sub(r"[a-zA-Z_]+\.py:[0-9]+$", "", output, flags=re.MULTILINE).split())


@pytest.fixture
def relative_changelog_fragment_dir() -> str:
    return "changelog"


@pytest.fixture
def changelog_file_name() -> str:
    return "CHANGELOG.rst"


@pytest.fixture
def minimal_towncrier_pyproject_toml(relative_changelog_fragment_dir, changelog_file_name) -> str:
    return f"""[project]
dynamic = ["version"]
name = "dkist-processing-foo"

[tool.towncrier]
    package = "dkist_procesing_foo"
    filename = "{changelog_file_name}"
    directory = "{relative_changelog_fragment_dir}/"
    issue_format = "`#{{issue}} <https://bitbucket.org/dkistdc/dkist_processing_foo/pull-requests/{{issue}}>`__"
    title_format = "{{version}} ({{project_date}})"
    ignore = [".gitempty", "*.science*rst"]

[[tool.towncrier.type]]
      directory = "feature"
      name = "Features"
      showcontent = true
"""

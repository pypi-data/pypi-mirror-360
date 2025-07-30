from subprocess import PIPE
from subprocess import Popen

import pytest

from dkist_dev_tools.tests.conftest import normalize_logged_output


@pytest.fixture
def science_changelog_file_name() -> str:
    return "SCIENCE_CHANGELOG.rst"


@pytest.fixture
def minimal_science_towncrier_pyproject_toml(
    relative_changelog_fragment_dir, science_changelog_file_name
) -> str:
    return f"""[project]
dynamic = ["version"]
name = "dkist-processing-foo"

[tool.towncrier]
    package = "dkist_procesing_foo"
    filename = "{science_changelog_file_name}"
    directory = "{relative_changelog_fragment_dir}/"
    issue_format = "`#{{issue}} <https://bitbucket.org/dkistdc/dkist_processing_foo/pull-requests/{{issue}}>`__"
    title_format = "{{version}} ({{project_date}})"
    orphan_prefix = "+"
    all_bullets = true
    ignore = [".gitempty"]

[[tool.towncrier.type]]
      directory = "science"
      name = ""
      showcontent = true
"""


@pytest.mark.parametrize(
    "version, skip_draft, draft_OK_response, run_from_project_dir",
    [
        pytest.param("v6.2.8", False, "y", True, id="vVersion-draftOK"),
        pytest.param("v6.2.8", False, "n", True, id="vVersion-draftBad"),
        pytest.param("6.2.8", True, None, True, id="rawVersion-noDraft"),
        pytest.param("6.2.8", True, "y", False, id="dir_option"),
    ],
)
def test_changelog_cli(
    init_package_pyproject,
    minimal_towncrier_pyproject_toml,
    relative_changelog_fragment_dir,
    changelog_file_name,
    version,
    skip_draft,
    draft_OK_response,
    run_from_project_dir,
    package_dir,
    tmp_path_factory,
    wide_terminal,
):
    """
    Given: A project dir with a towncrier TOML and some new fragments
    When: Rendering the changelog with `ddt changelog`
    Then: The changelog is correctly rendered, unless the user says the draft looks wrong
    """
    init_package_pyproject(minimal_towncrier_pyproject_toml)

    changelog_dir = package_dir / relative_changelog_fragment_dir
    changelog_dir.mkdir()
    fragment_name = "34.feature.rst"
    with open(changelog_dir / fragment_name, "w") as f:
        f.write("Add a feature\n")

    rendered_changelog = package_dir / changelog_file_name
    with open(rendered_changelog, "w") as f:
        f.write("Previous stuff")

    Popen(["git", "init"], cwd=package_dir).wait()
    Popen(["git", "add", "."], cwd=package_dir).wait()
    Popen(["git", "commit", "-m", "first commit!"], cwd=package_dir).wait()

    args = [version]
    if skip_draft:
        args += ["-s"]

    run_path = package_dir
    if not run_from_project_dir:
        args = ["-d", str(package_dir)] + args
        run_path = tmp_path_factory.mktemp("process_path")

    p = Popen(args=["ddt", "changelog"] + args, cwd=run_path, stdin=PIPE)
    if draft_OK_response is not None:
        p.communicate(input=draft_OK_response.encode())
    p.wait()

    expected_return_code = 1 if draft_OK_response == "n" else 0
    assert p.returncode == expected_return_code

    with open(rendered_changelog, "r") as f:
        lines = f.readlines()

    if draft_OK_response == "n":
        assert lines[0] == "Previous stuff"
    else:
        v_version = f"v{version.replace('v', '')}"
        assert lines[0].startswith(f"{v_version}")
        assert any(["Add a feature" in l for l in lines])

        g = Popen(args=["git", "status"], cwd=package_dir, stdout=PIPE)
        git_out = g.communicate()[0].decode().split("\n")
        assert f"\tmodified:   {changelog_file_name}" in git_out
        assert f"\tdeleted:    {relative_changelog_fragment_dir}/{fragment_name}" in git_out


def test_render_with_science(
    init_package_pyproject,
    minimal_towncrier_pyproject_toml,
    minimal_science_towncrier_pyproject_toml,
    relative_changelog_fragment_dir,
    changelog_file_name,
    science_changelog_file_name,
    package_dir,
    wide_terminal,
):
    """
    Given: A project dir with both a base and science towncrier TOML and some new fragments for each
    When: Rendering the changelogs with `ddt changelog`
    Then: The two changelogs are correctly rendered
    """
    init_package_pyproject(minimal_towncrier_pyproject_toml)
    init_package_pyproject(
        minimal_science_towncrier_pyproject_toml, project_file_name="towncrier_science.toml"
    )

    changelog_dir = package_dir / relative_changelog_fragment_dir
    changelog_dir.mkdir()
    fragment_name = "34.feature.rst"
    with open(changelog_dir / fragment_name, "w") as f:
        f.write("Add a feature\n")

    science_fragment_name = "+.science.rst"
    with open(changelog_dir / science_fragment_name, "w") as f:
        f.write("Did science\n")

    rendered_changelog = package_dir / changelog_file_name
    science_rendered_changelog = package_dir / science_changelog_file_name
    rendered_changelog.touch()
    science_rendered_changelog.touch()

    Popen(["git", "init"], cwd=package_dir).wait()
    Popen(["git", "add", "."], cwd=package_dir).wait()
    Popen(["git", "commit", "-m", "first commit!"], cwd=package_dir).wait()

    version = "6.2.8"
    v_version = "v6.2.8"
    args = [version, "-s"]

    p = Popen(args=["ddt", "changelog"] + args, cwd=package_dir)
    p.wait()

    assert p.returncode == 0

    with open(rendered_changelog, "r") as f:
        lines = f.readlines()
        assert lines[0].startswith(f"{v_version}")
        assert any(["Add a feature" in l for l in lines])

    with open(science_rendered_changelog, "r") as f:
        lines = f.readlines()
        assert lines[0].startswith(f"{v_version}")
        assert any(["Did science" in l for l in lines])

    g = Popen(args=["git", "status"], cwd=package_dir, stdout=PIPE)
    git_out = g.communicate()[0].decode().split("\n")
    assert f"\tmodified:   {changelog_file_name}" in git_out
    assert f"\tmodified:   {science_changelog_file_name}" in git_out
    assert f"\tdeleted:    {relative_changelog_fragment_dir}/{fragment_name}" in git_out
    assert f"\tdeleted:    {relative_changelog_fragment_dir}/{science_fragment_name}" in git_out


def test_no_toml(package_dir, wide_terminal):
    """
    Given: A directory with no towncrier config toml
    When: Trying to run `ddt changelog`
    Then: Fail and log a message
    """
    p = Popen(["ddt", "changelog", "v1.2.3", "-s"], cwd=package_dir, stdout=PIPE)
    p.wait()
    output = normalize_logged_output(p.communicate()[0].decode())

    assert p.returncode == 1
    assert f"Could not find 'pyproject.toml' file in '{package_dir}'" in output


def test_no_fragment_dir(
    package_dir,
    init_package_pyproject,
    minimal_towncrier_pyproject_toml,
    relative_changelog_fragment_dir,
    wide_terminal,
):
    """
    Given: A directory with no towncrier config toml
    When: Trying to run `ddt changelog`
    Then: Fail and log a message
    """
    init_package_pyproject(minimal_towncrier_pyproject_toml)

    p = Popen(["ddt", "changelog", "v1.2.3", "-s"], cwd=package_dir, stdout=PIPE)
    p.wait()
    output = normalize_logged_output(p.communicate()[0].decode())

    assert p.returncode == 1
    assert (
        f"Could not find a '{relative_changelog_fragment_dir}' fragments directory in '{package_dir}'"
        in output
    )


def test_nothing_to_do(
    package_dir,
    init_package_pyproject,
    minimal_towncrier_pyproject_toml,
    relative_changelog_fragment_dir,
    changelog_file_name,
    wide_terminal,
):
    """
    Given: A valid package directory with no new changelog fragments
    When: Running `ddt changelog`
    Then: Nothing is done
    """
    init_package_pyproject(minimal_towncrier_pyproject_toml)

    changelog_dir = package_dir / relative_changelog_fragment_dir
    changelog_dir.mkdir()

    rendered_changelog = package_dir / changelog_file_name
    with open(rendered_changelog, "w") as f:
        f.write("Previous stuff")

    Popen(["git", "init"], cwd=package_dir).wait()
    Popen(["git", "add", "."], cwd=package_dir).wait()
    Popen(["git", "commit", "-m", "first commit!"], cwd=package_dir).wait()

    p = Popen(["ddt", "changelog", "1.2.3", "-s"], cwd=package_dir, stdout=PIPE)
    p.wait()
    output = normalize_logged_output(p.communicate()[0].decode())

    assert p.returncode == 0
    assert f"Could not find any fragments in {relative_changelog_fragment_dir}" in output

    g = Popen(args=["git", "status"], cwd=package_dir, stdout=PIPE)
    git_out = normalize_logged_output(g.communicate()[0].decode())
    assert "modified:" not in git_out
    assert "deleted:" not in git_out


def test_science_but_no_standard_fragments(
    package_dir,
    init_package_pyproject,
    minimal_towncrier_pyproject_toml,
    minimal_science_towncrier_pyproject_toml,
    relative_changelog_fragment_dir,
    changelog_file_name,
    science_changelog_file_name,
    wide_terminal,
):
    """
    Given: A valid package directory with a science changelog fragment, but no non-science fragments
    When: Running `ddt changelog`
    Then: Fail and log a message
    """
    init_package_pyproject(minimal_towncrier_pyproject_toml)
    init_package_pyproject(
        minimal_science_towncrier_pyproject_toml, project_file_name="towncrier_science.toml"
    )

    changelog_dir = package_dir / relative_changelog_fragment_dir
    changelog_dir.mkdir()

    science_fragment_name = "+.science.rst"
    with open(changelog_dir / science_fragment_name, "w") as f:
        f.write("Did science\n")

    rendered_changelog = package_dir / changelog_file_name
    science_rendered_changelog = package_dir / science_changelog_file_name
    rendered_changelog.touch()
    science_rendered_changelog.touch()

    Popen(["git", "init"], cwd=package_dir).wait()
    Popen(["git", "add", "."], cwd=package_dir).wait()
    Popen(["git", "commit", "-m", "first commit!"], cwd=package_dir).wait()

    p = Popen(args=["ddt", "changelog", "1.2.3", "-s"], cwd=package_dir, stdout=PIPE)
    p.wait()
    output = normalize_logged_output(p.communicate()[0].decode())

    assert p.returncode == 1
    assert "Cannot update SCIENCE_CHANGELOG without a corresponding update to CHANGELOG." in output

from subprocess import Popen

import pytest


@pytest.fixture
def remote_git_repo(tmp_path_factory):
    repo_path = tmp_path_factory.mktemp("git_remote")
    Popen(["git", "init", "--bare"], cwd=repo_path).wait()

    return repo_path


@pytest.mark.parametrize(
    "fail, run_from_project_dir",
    [
        pytest.param(False, True, id="success"),
        pytest.param(True, True, id="failure"),
        pytest.param(False, False, id="dir_option"),
    ],
)
def test_towncrier_check(
    init_package_pyproject,
    relative_changelog_fragment_dir,
    minimal_towncrier_pyproject_toml,
    fail,
    package_dir,
    run_from_project_dir,
    remote_git_repo,
    tmp_path_factory,
    wide_terminal,
):
    """
    Given: A package with changes from origin/main and, optionally, a changelog fragment
    When: Running towncrier check
    Then: Success if the fragment exists, failure otherwise
    """
    init_package_pyproject(minimal_towncrier_pyproject_toml)

    Popen(["git", "init"], cwd=package_dir).wait()
    Popen(["git", "add", "."], cwd=package_dir).wait()
    Popen(["git", "commit", "-m", "first commit!"], cwd=package_dir).wait()
    Popen(["git", "remote", "add", "origin", str(remote_git_repo)], cwd=package_dir).wait()
    Popen(["git", "push", "-u", "origin", "main"], cwd=package_dir).wait()

    # Need to make a change so towncrier thinks a fragment is needed
    new_file = package_dir / "new_file"
    with open(new_file, "w") as f:
        f.write("new code!")
    Popen(["git", "add", new_file], cwd=package_dir).wait()
    Popen(["git", "commit", "-m", '"new_file"'], cwd=package_dir).wait()

    if not fail:
        fragment_name = "66.feature.rst"
        fragment_dir = package_dir / relative_changelog_fragment_dir
        fragment_dir.mkdir()
        with open(fragment_dir / fragment_name, "w") as f:
            f.write("Do a thing\n")
        Popen(["git", "add", relative_changelog_fragment_dir], cwd=package_dir).wait()
        Popen(["git", "commit", "-m", "add changelog fragment"], cwd=package_dir).wait()

    run_path = package_dir
    args = []
    if not run_from_project_dir:
        args = ["-d", str(package_dir)]
        run_path = tmp_path_factory.mktemp("process_path")

    p = Popen(["ddt", "check", "changelog"] + args, cwd=run_path)
    p.wait()

    assert p.returncode == int(fail)


@pytest.mark.parametrize(
    "rc, fragments, rendered, run_from_project_dir",
    [
        pytest.param(True, False, False, True, id="rc"),
        pytest.param(False, True, True, True, id="unrendered_fragments"),
        pytest.param(False, False, False, True, id="not_rendered"),
        pytest.param(False, False, True, True, id="success"),
        pytest.param(False, False, True, False, id="dir_option"),
        pytest.param(True, False, True, True, id="rc_and_rendered"),
    ],
)
def test_check_changelog_rendered(
    init_package_pyproject,
    relative_changelog_fragment_dir,
    changelog_file_name,
    minimal_towncrier_pyproject_toml,
    rc,
    fragments,
    rendered,
    run_from_project_dir,
    package_dir,
    tmp_path_factory,
    wide_terminal,
):
    """
    Given: A tagged git repo in varying states of a changelog being rendered, needing rendering, etc.
    When: Checking that the changelog was correctly rendered
    Then: The correct result is returned
    """
    version = "v6.2.8"
    if rc:
        version = f"{version}rc1"
    init_package_pyproject(minimal_towncrier_pyproject_toml)

    Popen(["git", "init"], cwd=package_dir).wait()
    Popen(["git", "add", "."], cwd=package_dir).wait()
    Popen(["git", "commit", "-m", "first commit!"], cwd=package_dir).wait()
    Popen(["git", "tag", version], cwd=package_dir).wait()

    fragment_dir = package_dir / relative_changelog_fragment_dir
    fragment_dir.mkdir()
    if fragments:
        fragment_name = "66.feature.rst"
        with open(fragment_dir / fragment_name, "w") as f:
            f.write("Do a thing\n")

    changelog_path = package_dir / changelog_file_name
    with open(changelog_path, "w") as f:
        if rendered:
            f.write(f"{version} (2001-01-01)\n===============\n")
        f.write("\nSomething")

    run_path = package_dir
    args = []
    if not run_from_project_dir:
        args = ["-d", str(package_dir)]
        run_path = tmp_path_factory.mktemp("process_path")

    expected_return_code = int(not ((rc ^ rendered) * (not fragments)))
    p = Popen(["ddt", "check", "changelog"] + args, cwd=run_path)
    p.wait()

    assert p.returncode == expected_return_code

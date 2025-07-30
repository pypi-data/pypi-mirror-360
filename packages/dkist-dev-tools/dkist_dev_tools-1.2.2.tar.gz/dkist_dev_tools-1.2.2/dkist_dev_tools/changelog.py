"""Tool for rendering a CHANGELOG with `towncrier`."""
import re
import sys
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen

import click
import tomlkit
from towncrier._builder import find_fragments
from towncrier._settings import load_config_from_options

from dkist_dev_tools.console import console
from dkist_dev_tools.get_pyproject_toml import get_pyproject_toml
from dkist_dev_tools.git import git_get_v_version
from dkist_dev_tools.version_type import Version
from dkist_dev_tools.version_type import VERSION_TYPE


def run_towncrier_command(cmd_list, cmd_path: Path = None) -> Popen:
    """Run a command and print the output only if it fails."""
    p = Popen(cmd_list, stdout=PIPE, stderr=PIPE, cwd=cmd_path)
    p.wait()

    if return_code := p.returncode:
        stdout, stderr = p.communicate()
        console.log(stdout.decode())
        console.log(f"[red]{stderr.decode()}[/red]")
        console.log("[red]Command failed :wilted_flower:[/red]")
        sys.exit(return_code)

    return p


def render_changelogs(project_dir: str | Path, v_version: str, skip_draft: bool = False):
    """
    Render changelog fragments into an update in the main changelog file.

    Can also update a science changelog file, if one exists.

    Prior to any rendering a check is made that fragments exist. This is to avoid adding empty sections to the changelog file.
    """
    default_config = get_pyproject_toml(project_dir)

    with open(default_config, "r") as f:
        toml_dict = tomlkit.load(f)
        package_name = toml_dict["project"]["name"]

    render_needed = check_fragments(default_config, log_empty=True)
    if render_needed:
        console.log("Rendering standard changelog")
        render_single_changelog(
            v_version=v_version,
            package_name=package_name,
            config_file=default_config,
            project_dir=project_dir,
            skip_draft=skip_draft,
        )

    science_config = Path("towncrier_science.toml")
    if science_config.exists():
        science_render_needed = check_fragments(science_config, log_empty=False)
        if science_render_needed:
            console.log("Rendering science changelog")
            if not render_needed:
                console.log(
                    "[red]Cannot update SCIENCE_CHANGELOG without a corresponding update to CHANGELOG.[/red]"
                )
                sys.exit(1)

            render_single_changelog(
                v_version=v_version,
                package_name=package_name,
                config_file=science_config,
                project_dir=project_dir,
                skip_draft=skip_draft,
            )

    console.log("[green]All done![/green]")


def check_fragments(config_file: Path, log_empty: bool = True) -> bool:
    """
    Check for the existence of the fragment directory and any fragments that are ready for rendering.

    We do a separate check instead of relying on `towncrier` because that program is very permissive regarding
    missing/empty fragment directories. We want to be more strict about when an update to the changelog is needed.
    """
    base_directory, towncrier_config = load_config_from_options(
        directory=None, config_path=str(config_file)
    )

    fragment_dir = Path(base_directory) / towncrier_config.directory
    if not fragment_dir.exists() or not fragment_dir.is_dir():
        console.log(
            f"[red]Could not find a '{fragment_dir.name}' fragments directory in '{base_directory}' :wilted_flower:[/red]"
        )
        sys.exit(1)

    _, fragment_list = find_fragments(
        base_directory=base_directory,
        config=towncrier_config,
        strict=(towncrier_config.ignore is not None),
    )

    if len(fragment_list) == 0:
        if log_empty:
            console.log(
                f"[yellow]Could not find any fragments in {towncrier_config.directory}. Nothing to do.[/yellow]"
            )
        return False

    return True


def render_single_changelog(
    v_version: str,
    config_file: Path,
    package_name: str,
    project_dir: Path,
    skip_draft: bool = False,
):
    """
    Run `towncrier build` for a single changelog (i.e., config file path).

    By default, a draft of the change is printed to stdout and the user is asked to confirm it is OK before writing
    the change to the actual changelog file. This check can be skipped with the ``skip_draft`` kwarg.
    """
    base_towncrier_call = [
        "towncrier",
        "build",
        "--version",
        v_version,
        "--config",
        config_file,
        "--name",
        package_name,
        "--yes",
    ]
    if not skip_draft:
        console.log("Rendering draft changelog...")
        p = run_towncrier_command(base_towncrier_call + ["--draft"], cmd_path=project_dir)
        stdout, stderr = p.communicate()
        console.log(f"{':arrow_down:' * 30}\n{stdout.decode()}\n{':arrow_up:'* 30}")

        draft_OK = click.confirm("Does the draft look OK?", default=False)
        if not draft_OK:
            console.log("Please fix the fragments and try again")
            sys.exit(1)

    else:
        console.log("[yellow]Skipping draft check. L E T 'S  G O O O O![/yellow]")

    console.log("Rendering and writing changelog...")
    run_towncrier_command(base_towncrier_call, cmd_path=project_dir)


@click.command(
    help="Render updates to CHANGELOG.rst for a given version. SCIENCE_CHANGELOG.rst will also be updated, if needed.",
    short_help="Render and updated CHANGELOG.rst",
    options_metavar="<options>",
)
@click.option(
    "-d",
    "--project-dir",
    help="Directory containing a 'pyproject.toml' file. Defaults to current directory.",
    default=Path.cwd(),
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, readable=True, path_type=Path
    ),
)
@click.option(
    "-s",
    "--skip-draft",
    help="Skip a visual check of the changes before writing the new CHANGELOG(s)",
    default=False,
    is_flag=True,
)
@click.argument("version", type=VERSION_TYPE, metavar="<version>")
def changelog(version: Version, skip_draft: bool, project_dir: Path):
    """Command-line entry point for `render_changelogs`."""
    render_changelogs(project_dir=project_dir, v_version=version.v_version, skip_draft=skip_draft)


def check_changelog_rendered(version: Version, project_dir: Path) -> None:
    """
    Check that the changelog has been rendered for the current version.

    First, check that no rendered fragments exist in the fragment directory. Then check that the changelog matches
    the current tagged version.

    A changelog rendered for a release candidate will fail the check.
    """
    v_version = version.v_version

    project_toml = get_pyproject_toml(project_dir)
    with open(project_toml, "r") as f:
        toml_dict = tomlkit.load(f)
        fragment_dir = project_dir / toml_dict["tool"]["towncrier"]["directory"]
        changelog_file_name = project_dir / toml_dict["tool"]["towncrier"]["filename"]

    with open(changelog_file_name, "r") as f:
        first_line = f.readline()

    if "rc" in v_version:
        if v_version in first_line:
            console.log("[red]Changelog was rendered for a release candidate :wilted_flower:[/red]")
            sys.exit(1)

        console.log("Release candidate detected. No check needed.")
        sys.exit(0)

    if list(fragment_dir.glob("*rst")):
        console.log(
            f"[red]Unmerged changelog fragments found in '{fragment_dir}' :wilted_flower:[/red]"
        )
        sys.exit(1)

    match_str = f"^{v_version}(?!rc)"
    if not re.search(match_str, first_line):
        console.log(
            f"[red]{changelog_file_name} has not been updated for {v_version} :wilted_flower:[/red]"
        )
        sys.exit(1)

    console.log("[green]Changelog correctly rendered[/green]")
    sys.exit(0)


def run_towncrier_check(project_dir: Path | None = None):
    """Run `towncrier check` and capture output."""
    run_towncrier_command(["towncrier", "check"], cmd_path=project_dir)

    console.log("[green]Looks good![/green]")
    sys.exit(0)


@click.command(
    help="Check either that changelog fragments exist or, for tagged versions, the changelog has been rendered.",
    short_help="Check that changelog machinery is in the correct state",
    name="changelog",
    options_metavar="<options>",
)
@click.option(
    "-d",
    "--project-dir",
    help="Directory containing a 'pyproject.toml' file. Defaults to current directory.",
    default=Path.cwd(),
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, readable=True, path_type=Path
    ),
)
def check_changelog(project_dir: Path):
    """Check that a tagged version has a rendered changelog OR changelog fragments exist."""
    if tagged_version := git_get_v_version(cmd_path=project_dir, fail_on_no_version=False):
        console.log("Detected tagged version. Checking if changelog was rendered.")
        check_changelog_rendered(tagged_version, project_dir=project_dir)

    console.log("No tagged version detected. Running towncrier check.")
    run_towncrier_check(project_dir=project_dir)

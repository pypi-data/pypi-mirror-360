"""Tool for freezing a complete set of dependencies for a given `dkist-processing-INSTRUMENT` package."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen
from tempfile import TemporaryDirectory
from venv import EnvBuilder

import click
import tomlkit
from packaging import version

from dkist_dev_tools.allowed_freezing_services import FrozenServices
from dkist_dev_tools.console import console
from dkist_dev_tools.get_pyproject_toml import get_pyproject_toml
from dkist_dev_tools.git import git_get_v_version
from dkist_dev_tools.prod_python_version import PROD_PYTHON_VERSION
from dkist_dev_tools.version_type import Version
from dkist_dev_tools.version_type import VERSION_TYPE


class LoudTemporaryDirectory(TemporaryDirectory):
    """Subclass of `TemporaryDirectory` that logs its cleanup to the console."""

    def cleanup(self):
        """Call `super().cleanup()` and log a message to the console."""
        super().cleanup()
        console.log(f"Cleaning up temporary environment directory {self.name}")


class RequirementFreezer(EnvBuilder):
    """Subclass of EnvBuilder that also pip-installs a given package and gets the full dependencies."""

    def __init__(self, project_dir: str | Path, dkist_package: str, *args, **kwargs):
        super().__init__(*args, with_pip=True, **kwargs)
        with LoudTemporaryDirectory(prefix="dkist_dev_tools_") as env_dir:
            self.build_full_environment(
                project_dir=project_dir, dkist_package=dkist_package, env_dir=env_dir
            )

    def build_full_environment(
        self, project_dir: str | Path, dkist_package: str, env_dir: str | Path
    ):
        """Create a fresh env, install the current package, and grab the full dependencies."""
        with console.status("Creating temporary virtual environment") as status:
            # These next lines are a direct copy from `self.create(env_dir)`
            # We're writing them out so we can inject status updates at various steps and continue past the
            # end of `self.create()` to get the package dependencies.
            env_dir = os.path.abspath(env_dir)
            context = self.ensure_directories(env_dir)
            self.context = context
            self.env_python_command = context.env_exec_cmd
            self.create_configuration(context)
            self.setup_python(context)
            self._setup_pip(context)
            self.setup_scripts(context)
            ####
            console.log(f"Created temporary environment in {context.env_dir}")

            status.update("Updating PIP")
            self.update_pip()
            console.log("Updated PIP")

            status.update(f"Installing {dkist_package}")
            self.install_dkist_package(project_dir)
            console.log(f"Successfully installed {dkist_package}")

            status.update("Grabbing as-built environment")
            self.requirements_dict_list = self.get_requirements_dict_list()
            console.log("Recorded as-built environment")

    def _run_env_python_command(self, python_args: list[str]):
        """
        Run a command with the env's python and capture outputs.

        If the command fails we'll log the stdout and stderr and exit with the command's return code.
        """
        full_args = [self.env_python_command] + python_args
        proc = Popen(full_args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()

        if return_code := proc.returncode:
            console.log(stdout.decode())
            console.log(f"[red]{stderr.decode()}[/red]")
            console.log("[red]Command failed :wilted_flower:[/red]")
            sys.exit(return_code)

        return stdout, stderr

    def update_pip(self):
        """Run `python -m pip install -U pip`."""
        args = ["-m", "pip", "install", "-U", "pip"]
        self._run_env_python_command(args)

    def install_dkist_package(self, project_dir: str | Path):
        """Run `python -m pip install {PROJET_DIR}`."""
        args = ["-m", "pip", "install", str(project_dir)]
        self._run_env_python_command(args)

    def get_requirements_dict_list(self) -> list[dict[str, str]]:
        """Get all dependencies of the current env and parse into a list of specifiers suitable for pyproject.toml."""
        args = ["-m", "pip", "list", "--format=json"]
        stdout, _ = self._run_env_python_command(args)

        return json.loads(stdout.decode())


def update_pyproject_toml_dependencies(
    project_dir: str | Path, version: str, skip_allowed_repo_check: bool
):
    """
    Get a full list of dependencies for the given package and put them as a pip extra in the projects pyproject.toml.

    The pip extra is called "frozen".
    """
    check_python_version()

    pyproject_file = get_pyproject_toml(project_dir)

    console.log(f"Using pyproject.toml in {str(project_dir)}")
    with open(pyproject_file, "r+") as f:
        toml_dict = tomlkit.load(f)

        cwd_package_name = toml_dict["project"]["name"]

        if not check_current_repo_needs_freezing(cwd_package_name):
            if not skip_allowed_repo_check:
                console.log(
                    f"[red]{cwd_package_name} is not package that needs freezing. (To override this message pass the '-f' option)[/red]"
                )
                sys.exit(1)
            else:
                console.log(
                    f"[yellow]{cwd_package_name} is not a package that needs freezing, but we're doing it anyway![/yellow]"
                )

        console.log(f"Updating dependencies for [green]{cwd_package_name}...[/green]")

        freezer = RequirementFreezer(project_dir=project_dir, dkist_package=cwd_package_name)

        console.log(f"Updating {str(pyproject_file)}")
        ddt_tool_table = tomlkit.table(is_super_table=True)
        ddt_tool_table.add(tomlkit.comment("Most recently frozen version by dkist-dev-tools"))
        ddt_tool_table.add("version", version)
        ddt_tool_table.add("date", datetime.now())
        ddt_tool_table.add(tomlkit.nl())

        frozen_deps_list = format_requirements(
            freezer.requirements_dict_list, dkist_package=cwd_package_name, version=version
        )

        toml_dict["tool"]["dkist-dev-tools"] = ddt_tool_table
        toml_dict["project"]["optional-dependencies"]["frozen"] = frozen_deps_list
        toml_dict["project"]["optional-dependencies"]["frozen"].multiline(True)

        f.seek(0)
        tomlkit.dump(toml_dict, f)
        f.truncate()

    console.log("[green]All done![/green]")


def format_requirements(
    requirements_dict_list: list[dict[str, str]], dkist_package: str, version: str
) -> list[str]:
    """Convert a json-formatted list of requirement dicts and update the current ``dksit_package`` to a new version."""
    flat_dict = {item["name"]: item["version"] for item in requirements_dict_list}
    flat_dict[dkist_package] = version

    requirements_str_list = sorted([" == ".join(item) for item in flat_dict.items()])

    return requirements_str_list


def check_python_version():
    """
    Ensure that the user is using the same version of python that is run on PROD.

    We only check the major and minor versions.
    """
    current_version = sys.version_info
    if not (
        current_version.major == PROD_PYTHON_VERSION.major
        and current_version.minor == PROD_PYTHON_VERSION.minor
    ):
        current_version_str = f"{current_version.major}.{current_version.minor}"
        raise RuntimeError(
            f"Your python version does not match what is used on PROD. You have {current_version_str}, but PROD uses {PROD_PYTHON_VERSION}"
        )


def check_current_repo_needs_freezing(package_name: str) -> bool:
    """Check that the current package is in the known set of packages that require freezing."""
    return package_name in list(FrozenServices)


@click.command(
    help="Build a new version of a dkist-processing-INSTRUMENT package in a clean env and update the 'frozen' pip extra in its pyproject.toml",
    short_help="Freeze full dependencies of fresh install into a pyproject.toml",
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
    "-f",
    "--force",
    "skip_allowed_repo_check",
    help="Freeze the package without checking if it's a package that needs freezing.",
    default=False,
    is_flag=True,
)
@click.argument("version", type=VERSION_TYPE, metavar="<version>")
def freeze(project_dir: Path, version: Version, skip_allowed_repo_check: bool):
    """Command-line entry point for `update_pyproject_toml_dependencies`."""
    update_pyproject_toml_dependencies(project_dir, version.raw_version, skip_allowed_repo_check)


@click.command(
    help="Check that the frozen version in pyporject.toml matches the current repo version",
    short_help="Ensure dependency freeze matches current version",
    name="freeze",
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
def check_frozen_dependencies(project_dir: Path) -> None:
    """Check that the frozen version in a pyproject.toml matches a given version."""
    project_toml = get_pyproject_toml(project_dir)

    bb_version = os.environ.get("BITBUCKET_TAG", None)
    if bb_version is None:
        console.log(
            "[yellow]BITBUCKET_TAG env variable not found. Inferring version from git tag[/yellow]"
        )
        parsed_version = git_get_v_version(cmd_path=project_dir, fail_on_no_version=True)
    else:
        parsed_version = VERSION_TYPE(bb_version)

    current_version = version.Version(parsed_version.raw_version)

    with open(project_toml, "r") as f:
        toml_dict = tomlkit.load(f)

    try:
        frozen_version = version.Version(toml_dict["tool"]["dkist-dev-tools"]["version"])
    except tomlkit.exceptions.NonExistentKey:
        console.log(f"[red]Could not find \[tool.dkist-dev-tools.version] in {project_toml}[/red]")
        sys.exit(1)

    if current_version != frozen_version:
        console.log(
            f"[red]Frozen version {frozen_version} does not match current version {current_version} :wilted_flower:[/red]"
        )
        sys.exit(1)

    if "frozen" not in toml_dict["project"]["optional-dependencies"]:
        console.log(
            f"[red]'Frozen' pip extra does not exist. Was it deleted manually? :triumph:[/red]"
        )
        sys.exit(1)

    console.log("[green]Correctly frozen![/green]")
    sys.exit(0)

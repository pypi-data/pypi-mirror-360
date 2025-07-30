"""Functions for calling git commands and parsing their output."""
import sys
from pathlib import Path
from subprocess import PIPE
from subprocess import Popen

from dkist_dev_tools.console import console
from dkist_dev_tools.version_type import Version
from dkist_dev_tools.version_type import VERSION_TYPE


def run_git_command(
    git_args: list[str], cmd_path: Path | None = None, exit_on_fail: bool = True
) -> tuple[int, str, str]:
    """
    Run a single git command.

    If ``exit_on_fail`` is `True` then a non-zero return code from `git` will cause the current process to exit with the
    same return code.
    """
    full_args = ["git"] + git_args
    proc = Popen(full_args, stdout=PIPE, stderr=PIPE, cwd=cmd_path)
    proc.wait()
    stdout, stderr = proc.communicate()

    return_code = proc.returncode

    if exit_on_fail and return_code:
        console.log(stdout.decode())
        console.log(f"[red]{stderr.decode()}[/red]")
        console.log("[red]Command failed :wilted_flower:[/red]")
        sys.exit(return_code)

    return return_code, stdout.decode(), stderr.decode()


def git_get_v_version(
    cmd_path: Path | None = None, fail_on_no_version: bool = True
) -> Version | None:
    """
    Look for a tag on the current commit that starts with 'v'.

    If ``fail_on_no_version`` is `False` then `None` will be returned when git is unable to find a matching version.
    """
    args = ["describe", "--tags", "--match", "v*", "--exact-match"]
    return_code, stdout, stderr = run_git_command(
        args, exit_on_fail=fail_on_no_version, cmd_path=cmd_path
    )

    if return_code:
        console.log("Could not determine git version tag")
        return None

    version = stdout.strip("\n")
    console.log(f"Found version '{version}'")
    return VERSION_TYPE(version)

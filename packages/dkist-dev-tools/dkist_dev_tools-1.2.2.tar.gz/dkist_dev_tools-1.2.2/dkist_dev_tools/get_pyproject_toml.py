"""Functions for getting default pyproject TOMLs."""
import sys
from pathlib import Path

from dkist_dev_tools.console import console


def get_pyproject_toml(project_dir) -> Path:
    """Load a pyproject.toml file from a given directory."""
    if isinstance(project_dir, str):
        project_dir = Path(project_dir)

    project_dir = project_dir.resolve()
    pyproject_file = project_dir / "pyproject.toml"

    if not pyproject_file.exists():
        console.log(
            f"[red]Could not find 'pyproject.toml' file in '{project_dir}' :wilted_flower:[/red]"
        )
        sys.exit(1)

    return pyproject_file

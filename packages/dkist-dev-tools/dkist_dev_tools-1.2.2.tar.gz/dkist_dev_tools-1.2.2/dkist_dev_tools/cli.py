"""High-level command line entry."""
import click

from dkist_dev_tools.changelog import changelog
from dkist_dev_tools.changelog import check_changelog
from dkist_dev_tools.freeze_dependencies import check_frozen_dependencies
from dkist_dev_tools.freeze_dependencies import freeze


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    options_metavar="<options>",
    subcommand_metavar="<command> [<args>]",
)
def ddt_command():
    """
    Suit of helpful scripts for developers of DKIST instrument pipelines.

    "Fun tools for cool people"
    """
    pass


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    options_metavar="<options>",
    short_help="Checks that the current release is ready for pushing",
    subcommand_metavar="<command> [<args>]",
)
def check():
    """Commands to check that an instrument pipeline release has been correctly set up."""
    pass


ddt_command.add_command(freeze)
ddt_command.add_command(changelog)
ddt_command.add_command(check)
check.add_command(check_frozen_dependencies)
check.add_command(check_changelog)

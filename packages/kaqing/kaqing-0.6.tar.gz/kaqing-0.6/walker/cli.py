import click

from walker import batch
from walker.cli_group import cli
from walker.utils import display_help
from . import __version__, repl

cli.add_command(batch.appid, "appid")
cli.add_command(batch.check, "check")
cli.add_command(batch.cql, "cql")
cli.add_command(batch.issues, "issues")
cli.add_command(batch.logs, "logs")
cli.add_command(batch.ls, "ls")
cli.add_command(batch.nodetool, "nodetool")
cli.add_command(batch.reaper, "reaper")
cli.add_command(repl.repl, "repl")
cli.add_command(batch.report, "report")
cli.add_command(batch.restart, "restart")
cli.add_command(batch.rolling_restart, "roll")
cli.add_command(batch.status, "status")

@cli.command()
def version():
    """Get the library version."""
    click.echo(click.style(f"{__version__}", bold=True))

@cli.command()
def help():
    """Show help message and exit."""
    display_help(True)

if __name__ == "__main__":
    cli()
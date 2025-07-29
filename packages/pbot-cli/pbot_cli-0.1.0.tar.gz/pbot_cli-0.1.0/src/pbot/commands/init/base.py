import typer
from pbot.commands.init import python

# Create the Typer app for the 'init' group with invoke_without_command=True
app = typer.Typer(help="PBOT Project Initializer", invoke_without_command=True)

@app.callback()
def init_callback(ctx: typer.Context):
    """
    Default command when user runs `pbot init` without subcommand.
    """
    if ctx.invoked_subcommand is None:
        typer.secho("🚀 Welcome to PBOT Init!", fg=typer.colors.GREEN)
        typer.echo("Available project types:")
        typer.echo("  pbot init python     → Initialize a Python project")
        typer.echo("  pbot init angular    → (coming soon)")
        typer.echo("  pbot init react      → (coming soon)")

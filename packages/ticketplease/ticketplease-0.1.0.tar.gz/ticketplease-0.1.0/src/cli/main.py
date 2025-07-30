"""Main CLI entry point for TicketPlease."""

import typer
from rich.console import Console

from ticketplease.main import run_config, run_task_generation

from . import __version__

app = typer.Typer(
    name="tk",
    help="CLI assistant for generating task descriptions using AI",
    add_completion=False,
)
console = Console()


@app.command()
def please() -> None:
    """Start the interactive task generation flow."""
    run_task_generation()


@app.command()
def config() -> None:
    """Configure your TicketPlease settings."""
    run_config(is_update=True)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version and exit"),
) -> None:
    """Show help when no command is provided."""
    if version:
        console.print(f"TicketPlease version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()

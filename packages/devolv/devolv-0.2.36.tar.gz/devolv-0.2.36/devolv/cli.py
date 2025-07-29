import typer
from devolv import __version__
from devolv.iam.validator.cli import validate
from devolv.drift.cli import drift

app = typer.Typer(help="Devolv CLI - Modular DevOps Toolkit")
# Register subcommands
app.command("validate")(validate)
app.command("drift")(drift)

@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show Devolv version and exit.",
        callback=lambda value: _print_version(value),
        is_eager=True,
    )
):
    pass

def _print_version(value: bool):
    if value:
        typer.echo(f"Devolv version: {__version__}")
        raise typer.Exit()

"""
chinmoysay - A simple CLI greeting application
"""

import typer
from typing import Optional


app = typer.Typer(help="A friendly CLI app for greetings!")


@app.command()
def greet(name: str = typer.Argument(..., help="Name of the person to greet")):
    """Greet someone with a friendly hello."""
    typer.echo(f"Hi {name}")


@app.command()
def goodbye(name: str = typer.Argument(..., help="Name of the person to say goodbye to")):
    """Say goodbye to someone."""
    typer.echo(f"Bye {name}")


@app.command()
def goodnight(name: str = typer.Argument(..., help="Name of the person say good night")):
    """Say goodnight to someone"""
    typer.echo(f"Good Night {name}")


# @app.command()
# def version():
#     """Show the version of chinmoysay."""
#     typer.echo("chinmoysay version 1.1.0")

def version_callback(value: bool):
    """
        Callback function that gets called when --version is used.

        Args:
            value: Boolean indicating if the flag was used

        How it works:
        - When user types 'chinmoysay --version', this function is called
        - If value is True (flag was used), it prints version and exits
        - If value is False/None (flag not used), it does nothing
        """
    if value:
        typer.echo(f"greetCLi version 1.2.0")
        raise typer.Exit()


@app.callback()
def main_callback(
        version: Optional[bool] = typer.Option(
            None,  # Default value (None means flag not used)
            "--version",  # Long flag name
            "-v",  # Short flag name
            callback=version_callback,  # Function to call when flag is used
            is_eager=True,  # Process this flag BEFORE other commands
            help="Show version and exit."  # Help text for the flag
        )
):
    """
    Main callback function for the CLI app.

    This function runs BEFORE any subcommands are processed.
    The is_eager=True parameter ensures version checking happens first.
    """
    pass


def main():
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()

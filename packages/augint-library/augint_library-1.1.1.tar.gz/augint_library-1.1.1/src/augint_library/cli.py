import click

"""cli.py

A minimal example module for demonstrating pdoc-generated documentation.

This module provides a simple greeting function and a CLI entry point.
"""


def print_hi(name: str) -> None:
    """
    Print a friendly greeting to the given name.

    This function formats and prints a personalized greeting message.

    Parameters:
        name (str): The name of the person to greet.

    Example:
        >>> print_hi("Alice")
        Hi Alice
    """
    print(f"Hi {name}")


@click.command()
@click.argument("name", default="there", type=str)
def cli(name: str) -> None:
    """
    Entry point for the example CLI.

    Calls `print_hi` with a default name if none is given.

    Example:
        $ python print_hi.py NAME
        Hi NAME
    """
    print_hi(name)


if __name__ == "__main__":
    # Run the main function when this module is executed as a script
    cli()

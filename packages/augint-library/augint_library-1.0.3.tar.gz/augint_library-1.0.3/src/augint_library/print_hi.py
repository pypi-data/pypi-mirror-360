"""print_hi.py

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
        Hi, Alice
    """
    print(f"Hi, {name}")


def main() -> None:
    """
    Entry point for the example CLI.

    Calls `print_hi` with a default name.

    This function is invoked when the module is run as a script.

    Example:
        $ python print_hi.py
        Hi, Test Project
    """
    print_hi("Test Project")


if __name__ == "__main__":
    # Run the main function when this module is executed as a script
    main()

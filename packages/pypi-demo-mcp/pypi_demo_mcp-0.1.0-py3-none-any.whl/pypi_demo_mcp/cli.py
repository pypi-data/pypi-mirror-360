#!/usr/bin/env python3
"""Command-line interface for PyPI Demo MCP."""

import argparse
import sys
from .server import main, install_to_claude


def cli():
    """Command-line interface."""
    parser = argparse.ArgumentParser(description="PyPI Demo MCP Server")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["run", "install"],
        default="run",
        help="Command to execute (run or install)"
    )
    
    args = parser.parse_args()
    
    if args.command == "install":
        install_to_claude()
    else:
        main()


if __name__ == "__main__":
    cli()

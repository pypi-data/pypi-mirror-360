#!/usr/bin/env python
import click

from orca_studio.cli.scan_mode import scan_mode_cmd


@click.group()
def cli():
    """ORCA Studio - Tools for computational chemistry visualization and analysis."""
    pass


# Register commands
cli.add_command(scan_mode_cmd)

if __name__ == "__main__":
    cli()

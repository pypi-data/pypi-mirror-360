"""Device management commands for Sungazer PVS6 API."""

import json

import click
from rich.console import Console
from rich.table import Table

from sungazer.cli.main import OddTypeEncoder, handle_exceptions


@click.group(help="Device information commands.")
def device():
    """
    Device management commands.

    These commands allow you to discover and manage devices connected to the
    Sungazer PVS6 system, including inverters, batteries, and other components.
    """


@device.command(name="list", help="Get the list of connected devices.")
@click.pass_context
@handle_exceptions
def list_devices(ctx):
    """
    Get the device discovery progress and list of connected devices.

    This command retrieves information about all devices discovered by the
    Sungazer PVS6 system, including their types, status, and configuration
    details.

    Returns:
        Device information including:
        - Device types (inverters, batteries, gateways, etc.)
        - Device status and operational state
        - Configuration and firmware information

    """
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    result = client.devices.list()

    if output_format == "json":
        click.echo(json.dumps(result.model_dump(), indent=2, cls=OddTypeEncoder))
    elif output_format == "table":
        console = Console()

        # Get the devices from the response
        devices_data = result.model_dump()
        devices = devices_data.get("devices", [])

        if not devices:
            console.print("No devices found")
            return

        # Create a table for each device
        for device in devices:
            # Create table with title and subtitle
            table = Table(
                title=(
                    f"{device.get('TYPE', 'Unknown')}: {device.get('MODEL', 'Unknown')}"
                ),
                caption=f"{device.get('SERIAL', 'Unknown Serial')}",
                show_header=True,
                header_style="bold magenta",
            )

            # Add columns
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")

            # Add rows for each field in the device
            for key, value in device.items():
                if isinstance(value, (dict, list)):
                    formatted_value = json.dumps(value, indent=2, cls=OddTypeEncoder)
                else:
                    formatted_value = str(value)

                table.add_row(key, formatted_value)

            console.print(table)
            console.print()  # Add spacing between devices

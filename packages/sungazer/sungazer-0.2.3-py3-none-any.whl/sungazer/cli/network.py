"""Network management commands for Sungazer PVS6 API."""

import click

from sungazer.cli.main import handle_exceptions, output_formatter


@click.group(help="Network information commands.")
def network():
    """
    Network management commands.

    These commands allow you to view and manage network interfaces on the
    Sungazer PVS6 device, including WiFi, cellular, and Ethernet connections.
    """


@network.command(name="list", help="Get the list of network interfaces.")
@click.pass_context
@handle_exceptions
def list_networks(ctx):
    """
    Get the list of network interfaces on the Sungazer PVS6 device.

    This command retrieves information about all network interfaces configured
    on the device, including their status, IP addresses, connection types,
    and operational state.

    Returns:
        Network interface information including:
        - Interface types (WiFi, cellular, Ethernet)
        - Connection status and IP addresses
        - Signal strength and provider information
        - Overall system connectivity status

    """
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    result = client.network.list()
    output_formatter(result.model_dump(), output_format)

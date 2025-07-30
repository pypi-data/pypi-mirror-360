"""Firmware management commands for Sungazer PVS6 API."""

import click

from sungazer.cli.main import handle_exceptions, output_formatter


@click.group(help="Firmware management commands.")
def firmware():
    """
    Firmware management commands.

    These commands allow you to check firmware status and manage firmware
    updates for the Sungazer PVS6 device and connected components.
    """


@firmware.command(name="check", help="Check if new firmware is available.")
@click.pass_context
@handle_exceptions
def check_firmware(ctx):
    """
    Check if new firmware is available for the Sungazer PVS6 device.

    This command queries the device to determine if firmware updates are
    available. It checks both the main device firmware and firmware for
    connected components.

    Returns:
        Firmware information including:
        - Current firmware version
        - Available firmware updates
        - Download URLs for updates (if available)
        - Update status and compatibility information

    """
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    result = client.firmware.check()
    output_formatter(result.model_dump(), output_format)

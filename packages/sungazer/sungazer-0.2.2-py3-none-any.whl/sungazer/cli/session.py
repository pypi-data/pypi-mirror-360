"""Session management commands for Sungazer PVS6 API."""

import click

from sungazer.cli.main import handle_exceptions, output_formatter


@click.group(help="Session management commands")
def session():
    """
    Session management commands.

    These commands allow you to start and stop sessions with the Sungazer PVS6 device.
    A session must be established before performing most operations on the device.
    """


@session.command(name="start", help="Start a new session.")
@click.pass_context
@handle_exceptions
def start(ctx):
    """
    Start a new session with the Sungazer PVS6 device.

    This command initiates a new session with the device, which is required
    for most API operations. The session provides authentication and maintains
    the connection state with the device.

    Returns:
        Session information including device version details, serial number,
        hardware model, and firmware information.

    """
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    result = client.session.start()
    output_formatter(result.model_dump(), output_format)


@session.command(name="stop", help="Stop the current session.")
@click.pass_context
@handle_exceptions
def stop(ctx):
    """
    Stop the current session with the Sungazer PVS6 device.

    This command terminates the active session with the device. It's good
    practice to explicitly stop sessions when you're done to free up
    resources on the device.

    Returns:
        Confirmation of session termination with result status.

    """
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    result = client.session.stop()
    output_formatter(result.model_dump(), output_format)

"""Grid profile management commands for Sungazer PVS6 API."""

import click

from sungazer.cli.main import handle_exceptions, output_formatter


@click.group(name="grid-profile", help="Grid profile management commands.")
def grid_profile():
    """
    Grid profile management commands.

    These commands allow you to view and manage grid profiles on the Sungazer
    PVS6 system. Grid profiles define how the solar system interacts with the
    utility grid and ensure compliance with local regulations.
    """


@grid_profile.command(name="get", help="Get the current grid profile configuration.")
@click.pass_context
@handle_exceptions
def get(ctx):
    """
    Get the current grid profile configuration.

    This command retrieves information about the currently active grid profile
    and any pending profile changes. Grid profiles define compliance parameters
    for utility grid interaction.

    Returns:
        Grid profile information including:
        - Currently active profile name and ID
        - Pending profile changes (if any)
        - Profile completion percentage
        - Support status across system components
        - Overall profile operation status

    """
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    result = client.grid_profiles.get()
    output_formatter(result.model_dump(), output_format)


@grid_profile.command(
    name="refresh", help="Refresh the list of available grid profiles."
)
@click.pass_context
@handle_exceptions
def refresh(ctx):
    """
    Refresh the list of available grid profiles.

    This command updates the list of available grid profiles from the Sungazer
    system. It may download new profiles or update existing ones based on
    current compliance requirements.

    Returns:
        Grid profile refresh information including:
        - Refresh operation result status
        - Updated profile list with metadata
        - Profile creation/update timestamps
        - Available profiles with compliance details

    """
    client = ctx.obj["client"]
    output_format = ctx.obj["output_format"]

    result = client.grid_profiles.refresh()
    output_formatter(result.model_dump(), output_format)

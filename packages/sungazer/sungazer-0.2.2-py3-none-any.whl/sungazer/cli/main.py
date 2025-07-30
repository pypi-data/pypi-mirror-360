import configparser
import json
import sys
import traceback
from datetime import datetime
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any, Dict

import click
from rich.console import Console
from rich.table import Table

from sungazer.client import SungazerClient


class OddTypeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime and IPv4Address objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, IPv4Address):
            return str(obj)
        return super().default(obj)


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file.

    Checks the following locations in order:
    1. /etc/sungazer.conf
    2. ~/.sungazer.conf
    3. ./sungazer.conf

    Returns:
        Dictionary with configuration values

    """
    config = configparser.ConfigParser()
    config_files = [
        "/etc/sungazer.conf",
        str(Path("~/.sungazer.conf").expanduser()),
        "./sungazer.conf",
    ]

    # Default values
    result = {
        "base_url": "http://sunpowerconsole.com/cgi-bin",
        "timeout": 30,
        "serial": None,
    }

    for config_file in config_files:
        if Path(config_file).exists():
            config.read(config_file)
            if "sungazer" in config:
                if "base_url" in config["sungazer"]:
                    result["base_url"] = config["sungazer"]["base_url"]
                if "timeout" in config["sungazer"]:
                    result["timeout"] = int(config["sungazer"]["timeout"])
                if "serial" in config["sungazer"]:
                    result["serial"] = config["sungazer"]["serial"]
            break

    return result


def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Read JSON from a file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data

    """
    with Path(file_path).open() as f:
        return json.load(f)


def output_formatter(data: Any, output_format: str):  # noqa: PLR0912
    """
    Format and output data based on the specified format.

    Args:
        data: The data to output
        output_format: The output format (json or table)

    """
    if output_format == "json":
        click.echo(json.dumps(data, indent=2, cls=OddTypeEncoder))
    elif output_format == "table":
        console = Console()

        if isinstance(data, list):
            if not data:
                console.print("Empty result")
                return

            # Create a table from a list of dictionaries
            table = Table(show_header=True)

            # Add columns based on first item keys
            sample = data[0]
            if isinstance(sample, dict):
                for key in sample:
                    table.add_column(key)

                # Add rows
                for item in data:
                    table.add_row(*[str(item.get(key, "")) for key in sample])

                console.print(table)
            else:
                # Simple list of non-dict values
                table.add_column("Value")
                for item in data:
                    table.add_row(str(item))
                console.print(table)
        elif isinstance(data, dict):
            # Create a table with key-value pairs
            table = Table(show_header=True)
            table.add_column("Key")
            table.add_column("Value")

            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    table.add_row(key, json.dumps(value, indent=2, cls=OddTypeEncoder))
                else:
                    table.add_row(key, str(value))

            console.print(table)
        else:
            # Simple value
            console.print(str(data))


def handle_exceptions(func):
    """Decorator to handle exceptions consistently across commands."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            click.echo(f"Error: {e!s}", err=True)
            sys.exit(1)
        except Exception as e:  # noqa: BLE001
            click.echo(f"Error: {e!s}", err=True)
            click.echo(traceback.format_exc(), err=True)
            sys.exit(1)

    return wrapper


@click.group()
@click.option(
    "--base-url",
    help="Base URL for the API",
    envvar="SUNGAZER_BASE_URL",
)
@click.option(
    "--timeout",
    type=int,
    help="Request timeout in seconds",
    envvar="SUNGAZER_TIMEOUT",
)
@click.option(
    "--output",
    type=click.Choice(["json", "table"]),
    default="json",
    help="Output format",
)
@click.pass_context
def cli(ctx, base_url, timeout, output):
    """Sungazer CLI - Command line interface for Sungazer PVS6 API."""
    # Load config from file
    config = load_config()

    # Override with CLI options if provided
    if base_url:
        config["base_url"] = base_url
    if timeout:
        config["timeout"] = timeout

    # Create client
    client = SungazerClient(
        base_url=config["base_url"],
        timeout=config["timeout"],
        serial=config["serial"],
    )

    # Store in context
    ctx.ensure_object(dict)
    ctx.obj["client"] = client
    ctx.obj["output_format"] = output


# Import all subcommands
from sungazer.cli.device import device
from sungazer.cli.firmware import firmware
from sungazer.cli.grid_profile import grid_profile
from sungazer.cli.network import network
from sungazer.cli.session import session

# Register all subcommands
cli.add_command(session)
cli.add_command(network)
cli.add_command(device)
cli.add_command(firmware)
cli.add_command(grid_profile)

if __name__ == "__main__":
    cli()

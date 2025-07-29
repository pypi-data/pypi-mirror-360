# -*- coding: UTF-8 -*-
import sys
from typing import Annotated, Any

from typer import Argument, Context, Typer

import cli.prompt as pmt
from cli.utils import convert_literal
from settings import AppSettings, Mode, get_settings, set_settings_by_path, update_settings


app = Typer(
    name="config",
    help="Configuration Subcommands.",
    rich_markup_mode="rich",
)

try:
    app_settings = get_settings()
except Exception as e:
    pmt.error(f"Error: {e}")
    sys.exit(1)


@app.callback()
def before(context: Context):
    if context.invoked_subcommand not in ["list"] and app_settings.root is None:
        pmt.error_exit("No blog root. Use \"blog init\" to initialize the blog.")


@app.command(name="list")
def list_config():
    """List all configurations."""

    def print_deep_dict(config: dict[str, Any], prefix=""):
        for key, value in config.items():
            key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                print_deep_dict(value, key)
            else:
                pmt.info(f"{key} = {str(value) if value != '' else None}")

    print_deep_dict(app_settings.model_dump())


@app.command(name="set")
def set_config(
    key: Annotated[str, Argument(help="Configuration key using dot-notation.")],
    value: Annotated[Any, Argument(help="Configuration value.", parser=convert_literal)],
):
    """Set a configuration."""
    try:
        updated = set_settings_by_path(app_settings, key, value)
        update_settings(updated)
        pmt.success(f"Configuration \"{key}\" updated to \"{value}\" successfully.")
    except Exception as e:
        pmt.error_exit(f"Error: {e}")


@app.command()
def reset():
    """Reset configuration."""
    try:
        init_settings = AppSettings(mode=Mode.File)
        update_settings(init_settings)
    except Exception as e:
        pmt.error_exit(f"Error: {e}")
    pmt.success(f"Reset default configuration successfully.")

from __future__ import annotations

import logging

import typer

from .commands.backtest import backtest
from .commands.calibrate import calibrate
from .commands.dashboard import dashboard
from .commands.data import download_data, get_dividends, save_snapshot
from .commands.demo import demo
from .commands.price import price
from .commands.tools import get_implied_rate

__doc__ = """
This module provides the main entry point for the optpricing CLI.

It defines the main Typer application and registers all commands and subcommands
from the `commands` directory.
"""

# --- Main App Definition ---
app = typer.Typer(
    name="optpricing",
    help="A quantitative finance library for option pricing and analysis.",
    add_completion=False,
)

data_app = typer.Typer(name="data", help="Tools for downloading and managing data.")
tools_app = typer.Typer(name="tools", help="Miscellaneous financial utility tools.")


# --- Register Commands ---
# Register top-level commands to the main app
app.command()(dashboard)
app.command()(calibrate)
app.command()(backtest)
app.command()(price)
app.command()(demo)

# Register data commands to the data_app
data_app.command(name="download")(download_data)
data_app.command(name="snapshot")(save_snapshot)
data_app.command(name="dividends")(get_dividends)

# Register tools commands to the tools_app
tools_app.command(name="implied-rate")(get_implied_rate)


# --- Add Sub-Apps to Main App ---
app.add_typer(data_app)
app.add_typer(tools_app)


# --- Utility Functions ---
def setup_logging(verbose: bool):
    """
    Configures the root logger based on the verbosity flag.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

"""
pytrnsys_process package for processing TRNSYS simulation results.

This package provides tools and utilities for analyzing and processing
TRNSYS simulation output data.
"""

__version__ = "0.0.2"

from pytrnsys_process.config import REPO_ROOT, Defaults, global_settings
from pytrnsys_process.plot import (
    bar_chart,
    energy_balance,
    histogram,
    line_plot,
    scatter_plot,
    scalar_compare_plot,
    stacked_bar_chart,
    get_figure_with_twin_x_axis,
)
from pytrnsys_process.process import (
    Simulation,
    SimulationsData,
    do_comparison,
    process_single_simulation,
    process_whole_result_set,
    process_whole_result_set_parallel,
)
from pytrnsys_process.util import (
    export_plots_in_configured_formats,
    load_simulation_from_pickle,
    load_simulations_data_from_pickle,
)

__all__ = [
    "line_plot",
    "bar_chart",
    "stacked_bar_chart",
    "histogram",
    "energy_balance",
    "scatter_plot",
    "scalar_compare_plot",
    "get_figure_with_twin_x_axis",
    "process_whole_result_set_parallel",
    "process_single_simulation",
    "process_whole_result_set",
    "do_comparison",
    "export_plots_in_configured_formats",
    "global_settings",
    "Defaults",
    "REPO_ROOT",
    "Simulation",
    "SimulationsData",
    "load_simulations_data_from_pickle",
    "load_simulation_from_pickle",
]

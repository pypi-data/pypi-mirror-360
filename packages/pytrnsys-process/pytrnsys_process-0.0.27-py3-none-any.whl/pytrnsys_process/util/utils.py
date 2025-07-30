import collections.abc as _abc
import logging as _logging
import os as _os
import pathlib as _pl
import pickle as _pickle
import subprocess as _subprocess
import typing as _tp

import matplotlib.pyplot as _plt

from pytrnsys_process import config as conf
from pytrnsys_process import log
from pytrnsys_process.process import data_structures as ds


def get_sim_folders(path_to_results: _pl.Path) -> _abc.Sequence[_pl.Path]:
    sim_folders = []
    for item in path_to_results.glob("*"):
        if item.is_dir():
            sim_folders.append(item)
    return sim_folders


def get_files(
    sim_folders: _abc.Sequence[_pl.Path],
    results_folder_name: _tp.Optional[str] = None,
    get_mfr_and_t: _tp.Optional[bool] = None,
    read_deck_files: _tp.Optional[bool] = None,
) -> _abc.Sequence[_pl.Path]:
    """Get simulation files from folders based on configuration.

    Parameters
    __________
        sim_folders:
            Sequence of paths to simulation folders

        results_folder_name:
            Name of folder containing printer files

        get_mfr_and_t:
            Whether to include step files (T and Mfr files)

        read_deck_files:
            Whether to include deck files

    Returns
    _______
        Sequence of paths to simulation files
    """
    if not results_folder_name:
        results_folder_name = (
            conf.global_settings.reader.folder_name_for_printer_files
        )
    if not get_mfr_and_t:
        get_mfr_and_t = conf.global_settings.reader.read_step_files
    if not read_deck_files:
        read_deck_files = conf.global_settings.reader.read_deck_files

    sim_files: list[_pl.Path] = []
    for sim_folder in sim_folders:
        if get_mfr_and_t:
            sim_files.extend(sim_folder.glob("*[_T,_Mfr].prt"))
        if read_deck_files:
            sim_files.extend(sim_folder.glob("**/*.dck"))
        results_path = sim_folder / results_folder_name
        if results_path.exists():
            sim_files.extend(results_path.glob("*"))

    return [x for x in sim_files if x.is_file()]


def export_plots_in_configured_formats(
    fig: _plt.Figure,
    path_to_directory: str,
    plot_name: str,
    plots_folder_name: str = "plots",
) -> None:
    """Save a matplotlib figure in multiple formats and sizes.

    Saves the figure in all configured formats (png, pdf, emf) and sizes (A4, A4_HALF)
    as specified in the plot settings (api.settings.plot).
    For EMF format, the figure is first saved as SVG and then converted using Inkscape.

    Parameters
    __________
        fig:
            The matplotlib Figure object to save.

        path_to_directory:
            Directory path where the plots should be saved.

        plot_name:
            Base name for the plot file (will be appended with size and format).

        plots_folder_name:
            leave empty if you don't want to save in a new folder

    Note
    ____
        - Creates a 'plots' subdirectory if it doesn't exist
        - For EMF files, requires Inkscape to be installed at the configured path
        - File naming format: {plot_name}-{size_name}.{format}

    Example
    _______
        >>> from pytrnsys_process import api, data_structures
        >>> def processing_of_monthly_data(simulation: data_structures.Simulation):
        >>>     monthly_df = simulation.monthly
        >>>     columns_to_plot = ["QSnk60P", "QSnk60PauxCondSwitch_kW"]
        >>>     fig, ax = api.bar_chart(monthly_df, columns_to_plot)
        >>>
        >>>     # Save the plot in multiple formats
        >>>     api.export_plots_in_configured_formats(fig, simulation.path, "monthly-bar-chart")
        >>>     # Creates files like:
        >>>     #   results/simulation1/plots/monthly-bar-chart-A4.png
        >>>     #   results/simulation1/plots/monthly-bar-chart-A4.pdf
        >>>     #   results/simulation1/plots/monthly-bar-chart-A4.emf
        >>>     #   results/simulation1/plots/monthly-bar-chart-A4_HALF.png
        >>>     #   etc.
    """
    plot_settings = conf.global_settings.plot
    plots_folder = _pl.Path(path_to_directory) / plots_folder_name
    plots_folder.mkdir(exist_ok=True)

    for size_name, size in plot_settings.figure_sizes.items():
        file_no_suffix = plots_folder / f"{plot_name}-{size_name}"
        fig.set_size_inches(size)
        for fmt in plot_settings.file_formats:
            if fmt == ".emf":
                path_to_svg = file_no_suffix.with_suffix(".svg")
                fig.savefig(path_to_svg)
                convert_svg_to_emf(file_no_suffix)
                if ".svg" not in plot_settings.file_formats:
                    _os.remove(path_to_svg)
            else:
                fig.savefig(file_no_suffix.with_suffix(fmt))


def convert_svg_to_emf(file_no_suffix: _pl.Path) -> None:
    logger = log.default_console_logger
    try:
        inkscape_path = conf.global_settings.plot.inkscape_path
        if not _pl.Path(inkscape_path).exists():
            raise OSError(f"Inkscape executable not found at: {inkscape_path}")
        emf_filepath = file_no_suffix.with_suffix(".emf")
        path_to_svg = file_no_suffix.with_suffix(".svg")

        _subprocess.run(
            [
                inkscape_path,
                "--export-filename=" + str(emf_filepath),
                "--export-type=emf",
                str(path_to_svg),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    except _subprocess.CalledProcessError as e:
        logger.error(
            "Inkscape conversion failed: %s\nOutput: %s",
            e,
            e.output,
            exc_info=True,
        )
    except OSError as e:
        logger.error("System error running Inkscape: %s", e, exc_info=True)


def get_file_content_as_string(
    file_path: _pl.Path, encoding: _tp.Optional[str] = None
) -> str:
    """Read and return the entire content of a file as a string.

    Parameters
    __________
        file_path pathlib.Path:
            Path to the file to read
        encoding str, optional:
            File encoding to use.
            defaults to UTF-8 if that fails it tries to use windows-1252

    Returns
    _______
        file_content: str
            Content of the file as a string
    """

    def read(encoding_to_try):
        with open(file_path, "r", encoding=encoding_to_try) as file:
            return file.read()

    if not encoding:
        try:
            return read("UTF-8")
        except UnicodeDecodeError:
            return read("windows-1252")
    return read(encoding)


def save_to_pickle(
    data: ds.Simulation | ds.SimulationsData,
    path: _pl.Path,
    logger: _logging.Logger = log.default_console_logger,
) -> None:
    """Save ResultsForComparison data to a pickle file.

    This function saves the entire ResultsForComparison object to a pickle file,
    preserving all data structures and relationships.

    Parameters
    __________
        data:
            data object to save

        path:
            Path where to save the pickle file

    Raises
    _______
        OSError: If there's an error when writing to the file
    """
    try:
        with open(path, "wb") as f:
            _pickle.dump(data, f)
    except OSError as e:
        logger.error(
            "Error saving ResultsForComparison to pickle: %s", e, exc_info=True
        )
        raise


def load_simulations_data_from_pickle(
    path: _pl.Path, logger: _logging.Logger = log.default_console_logger
) -> ds.SimulationsData:
    """Load SimulationsData from a pickle file.

    This function loads a previously saved SimulationsData object from a pickle file.

    Parameters
    __________
        path: pathlib.Path
            To the pickle file to load

        logger: logging.Logger, optional
            Logger object that will log any messages, warnings, and/or errors

    Returns
    _______
        SimulationsData: :class:`pytrnsys_processing.data_structures.SimulationsData`
            Reconstructed SimulationsData object

    Raises
    _______
        OSError: If there's an error reading the file
        pickle.UnpicklingError: If the file is corrupted or invalid
    """
    try:
        with open(path, "rb") as f:
            simulations_data = _pickle.load(f)

        # Check if it has the expected attributes of SimulationsData
        required_attrs = {"simulations", "scalar", "path_to_simulations"}
        if all(hasattr(simulations_data, attr) for attr in required_attrs):
            return _tp.cast(ds.SimulationsData, simulations_data)

        raise ValueError(
            f"Loaded object is missing required SimulationsData attributes. Type: {type(simulations_data).__name__}"
        )

    except OSError as e:
        logger.error(
            "Error loading ResultsForComparison from pickle: %s",
            e,
            exc_info=True,
        )
        raise
    except (_pickle.UnpicklingError, ValueError) as e:
        logger.error(
            "Invalid ResultsForComparison pickle format: %s", e, exc_info=True
        )
        raise


def load_simulation_from_pickle(
    path: _pl.Path, logger: _logging.Logger = log.default_console_logger
) -> ds.Simulation:
    """Load a Simulation object from a pickle file.

    This function loads a previously saved Simulation object from a pickle file.

    Parameters
    __________
        path: pathlib.Path
            To the pickle file to load

        logger: logging.Logger, optional
            Logger object that will log any messages, warnings, and/or errors

    Returns
    _______
        Simulation: :class:`pytrnsys_processing.data_structures.Simulation`
            Reconstructed Simulation object

    Raises
    _______
        OSError: If there's an error reading the file
        pickle.UnpicklingError: If the file is corrupted or invalid"""
    try:
        with open(path, "rb") as f:
            simulation = _pickle.load(f)

        # Check if it has the expected attributes of a Simulation
        required_attrs = {"monthly", "hourly", "step", "scalar", "path"}
        if all(hasattr(simulation, attr) for attr in required_attrs):
            return _tp.cast(ds.Simulation, simulation)

        raise ValueError(
            f"Loaded object is missing required Simulation attributes. Type: {type(simulation).__name__}"
        )
    except OSError as e:
        logger.error(
            "Error loading Simulation from pickle: %s", e, exc_info=True
        )
        raise
    except (_pickle.UnpicklingError, ValueError) as e:
        logger.error("Invalid Simulation pickle format: %s", e, exc_info=True)
        raise

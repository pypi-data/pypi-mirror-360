import logging as _logging
import pathlib as _pl
from collections import abc as _abc
from dataclasses import dataclass, field

import pandas as _pd

from pytrnsys_process import config as conf
from pytrnsys_process import deck, log, read, util
from pytrnsys_process.process import data_structures as ds
from pytrnsys_process.process import file_type_detector as ftd


def process_sim(
    sim_files: _abc.Sequence[_pl.Path], sim_folder: _pl.Path
) -> ds.Simulation:
    # Used to store the array of dataframes for each file type.
    # Later used to concatenate all into one dataframe and saving as Sim object
    simulation_data_collector = _SimulationDataCollector()

    sim_logger = log.get_simulation_logger(sim_folder)
    for sim_file in sim_files:
        try:
            _process_file(
                simulation_data_collector,
                sim_file,
                _determine_file_type(sim_file, sim_logger),
            )
        except ValueError as e:
            sim_logger.error(
                "Error reading file %s it will not be available for processing: %s",
                sim_file,
                str(e),
                exc_info=True,
            )
        except KeyError as e:
            sim_logger.error(
                "Error reading file %s it will not be available for processing: %s",
                sim_file,
                str(e),
                exc_info=True,
            )

    return _merge_dataframes_into_simulation(
        simulation_data_collector, sim_folder
    )


def handle_duplicate_columns(df: _pd.DataFrame) -> _pd.DataFrame:
    """
    Process duplicate columns in a DataFrame, ensuring they contain consistent data.

    This function checks for duplicate column names and verifies that:
    1. If one duplicate column has NaN values, the other(s) must also have NaN at the same indices
    2. All non-NaN values must be identical across duplicate columns

    Parameters
    __________
    df: pandas.DataFrame
        Input DataFrame to process

    Returns
    _______
    df: pandas.DataFrame
        DataFrame with duplicate columns removed, keeping only the first occurrence

    Raises
    ______
    ValueError
        If duplicate columns have:
        1. NaN values in one column while having actual values in another at the same index, or
        2. Different non-NaN values at the same index

    Note
    ____
    https://stackoverflow.com/questions/14984119/python-pandas-remove-duplicate-columns
    """
    remove_time_as_well = False
    for col in df.columns[df.columns.duplicated(keep=False)]:
        duplicate_cols = df.iloc[:, df.columns == col]

        nan_mask = duplicate_cols.isna()
        value_mask = ~nan_mask
        if ((nan_mask.sum(axis=1) > 0) & (value_mask.sum(axis=1) > 0)).any():
            raise ValueError(
                f"Column '{col}' has NaN values in one column while having actual values in another"
            )

        if not duplicate_cols.apply(lambda x: x.nunique() <= 1, axis=1).all():
            if col == "Time":
                remove_time_as_well = True
                continue

            raise ValueError(
                f"Column '{col}' has conflicting values at same indices"
            )

    columns_to_be_removed = df.columns.duplicated()
    if remove_time_as_well:
        columns_to_be_removed += df.columns.get_loc("Time")  # type: ignore[arg-type]

    df = df.iloc[:, ~columns_to_be_removed].copy()

    return df


def _determine_file_type(
    sim_file: _pl.Path, logger: _logging.Logger
) -> conf.FileType:
    """Determine the file type using name and content."""
    try:
        return ftd.get_file_type_using_file_name(sim_file, logger)
    except ValueError:
        return ftd.get_file_type_using_file_content(sim_file, logger)


@dataclass
class _SimulationDataCollector:
    hourly: list[_pd.DataFrame] = field(default_factory=list)
    monthly: list[_pd.DataFrame] = field(default_factory=list)
    step: list[_pd.DataFrame] = field(default_factory=list)
    parsed_deck: _pd.DataFrame = field(default_factory=_pd.DataFrame)


def _read_file(file_path: _pl.Path, file_type: conf.FileType) -> _pd.DataFrame:
    """
    Factory method to read data from a file using the appropriate reader.

    Parameters
    __________
    file_path: pathlib.Path
        Path to the file to be read

    file_type: conf.FileType
        Type of data in the file (MONTHLY, HOURLY, or TIMESTEP)

    Returns
    _______
    pandas.DataFrame
        Data read from the file

    Raises
    ______
    ValueError
        If file extension is not supported
    """
    starting_year = conf.global_settings.reader.starting_year
    extension = file_path.suffix.lower()
    logger = log.get_simulation_logger(file_path.parents[1])
    if extension in [".prt", ".hr"]:
        reader = read.PrtReader()
        if file_type == conf.FileType.MONTHLY:
            return reader.read_monthly(
                file_path, logger=logger, starting_year=starting_year
            )
        if file_type == conf.FileType.HOURLY:
            return reader.read_hourly(
                file_path, logger=logger, starting_year=starting_year
            )
        if file_type == conf.FileType.TIMESTEP:
            return reader.read_step(
                file_path, starting_year=starting_year, skipfooter=23, header=1
            )
        if file_type == conf.FileType.HYDRAULIC:
            return reader.read_step(file_path, starting_year=starting_year)
    elif extension == ".csv":
        return read.CsvReader().read_csv(file_path)

    raise ValueError(f"Unsupported file extension: {extension}")


def _process_file(
    simulation_data_collector: _SimulationDataCollector,
    file_path: _pl.Path,
    file_type: conf.FileType,
) -> bool:
    if file_type == conf.FileType.MONTHLY:
        simulation_data_collector.monthly.append(
            _read_file(file_path, conf.FileType.MONTHLY)
        )
    elif file_type == conf.FileType.HOURLY:
        simulation_data_collector.hourly.append(
            _read_file(file_path, conf.FileType.HOURLY)
        )
    elif (
        file_type == conf.FileType.TIMESTEP
        and conf.global_settings.reader.read_step_files
    ):
        simulation_data_collector.step.append(
            _read_file(file_path, conf.FileType.TIMESTEP)
        )
    elif (
        file_type == conf.FileType.HYDRAULIC
        and conf.global_settings.reader.read_step_files
    ):
        simulation_data_collector.step.append(
            _read_file(file_path, conf.FileType.HYDRAULIC)
        )
    elif (
        file_type == conf.FileType.DECK
        and conf.global_settings.reader.read_deck_files
    ):
        simulation_data_collector.parsed_deck = _get_deck_as_df(file_path)
    else:
        return False
    return True


def _get_deck_as_df(
    file_path: _pl.Path,
) -> _pd.DataFrame:
    deck_file_as_string = util.get_file_content_as_string(file_path)
    parsed_deck: dict[str, float] = deck.parse_deck_for_constant_expressions(
        deck_file_as_string, log.get_simulation_logger(file_path.parent)
    )
    deck_as_df = _pd.DataFrame([parsed_deck])
    return deck_as_df


def _merge_dataframes_into_simulation(
    simulation_data_collector: _SimulationDataCollector, sim_folder: _pl.Path
) -> ds.Simulation:
    monthly_df = _get_df_without_duplicates(simulation_data_collector.monthly)
    hourly_df = _get_df_without_duplicates(simulation_data_collector.hourly)
    timestep_df = _get_df_without_duplicates(simulation_data_collector.step)
    parsed_deck = simulation_data_collector.parsed_deck

    return ds.Simulation(
        sim_folder.as_posix(), monthly_df, hourly_df, timestep_df, parsed_deck
    )


def _get_df_without_duplicates(dfs: _abc.Sequence[_pd.DataFrame]):
    if len(dfs) > 0:
        return handle_duplicate_columns(_pd.concat(dfs, axis=1))

    return _pd.DataFrame()

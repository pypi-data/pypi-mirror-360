import datetime as _dt
import logging as _logging
import pathlib as _pl
import re as _re

from pytrnsys_process import config as conf
from pytrnsys_process import log
from pytrnsys_process import read


def get_file_type_using_file_content(
    file_path: _pl.Path, logger: _logging.Logger = log.default_console_logger
) -> conf.FileType:
    """
    Determine the file type by analyzing its content.

    Parameters
    __________
        file_path: :class:`pathlib.Path`
            Path to the file to analyze

    Returns
    _______
        FileType: :class:`pytrnsys_process.constants.FileType`
            The detected file type (MONTHLY, HOURLY, or TIMESTEP)

    Raises
    ______
        ValueError: If the file type cannot be determined from the content
    """
    reader = read.PrtReader()

    try:
        # First try reading as regular file to check if it's monthly or hourly
        monthly_or_hourly_df = reader.read(file_path)
        if monthly_or_hourly_df.columns[0] == "Month":
            logger.info("Detected %s as monthly file", file_path)
            return conf.FileType.MONTHLY
        if monthly_or_hourly_df.columns[0] == "Period":
            logger.info("Detected %s as hourly file", file_path)
            return conf.FileType.HOURLY
        try:
            # Try reading as hydraulic file
            return _try_read_as_step(
                file_path,
                logger,
                conf.FileType.HYDRAULIC,
                skipfooter=0,
                header=0,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            # try reading as a step file
            return _try_read_as_step(
                file_path,
                logger,
                conf.FileType.TIMESTEP,
                skipfooter=23,
                header=1,
            )
    except Exception as e:
        logger.error("Error reading file %s: %s", file_path, str(e))
        raise ValueError(f"Failed to read file {file_path}: {str(e)}") from e

    # If we get here, file type could not be determined
    raise ValueError(
        f"Could not determine file type from content of {file_path}"
    )


def _try_read_as_step(
    file_path, logger, expected_file_type, skipfooter, header
):
    reader = read.PrtReader()
    step_df = reader.read(file_path, skipfooter=skipfooter, header=header)
    if step_df.columns[0] in ["Period", "TIME"]:
        step_df = reader.read_step(
            file_path, skipfooter=skipfooter, header=header
        )
        time_interval = step_df.index[1] - step_df.index[0]
        if time_interval < _dt.timedelta(hours=1):
            logger.info(
                "Detected %s as a %s", file_path, expected_file_type.name
            )
            return expected_file_type
    raise ValueError(f"Unable to read as {expected_file_type.name}")


def get_file_type_using_file_name(
    file: _pl.Path, logger: _logging.Logger = log.default_console_logger
) -> conf.FileType:
    """
    Determine the file type by checking the filename against known patterns.

    Parameters
    __________
        file: :class:`pathlib.Path`
            The path to the file to check

    Returns
    ________
        FileType: :class:`pytrnsys_process.constants.FileType`
            The detected file type (MONTHLY, HOURLY, TIMESTEP or DECK)

    Raises
    ______
        ValueError: If no matching pattern is found
    """

    file_name = file.stem.lower()
    file_suffix = file.suffix.lower()

    # Check for DECK files first (suffix-based)
    if file_suffix == conf.FileType.DECK.value:
        return conf.FileType.DECK

    for file_type in conf.FileType:
        # Skip DECK type as it's already handled
        if file_type == conf.FileType.DECK:
            continue
        if any(
            _re.search(pattern, file_name)
            for pattern in file_type.value.patterns
        ):
            return file_type

    logger.warning("No matching file type found for filename: %s", file_name)
    raise ValueError(f"No matching file type found for filename: {file_name}")


def has_pattern(file: _pl.Path, file_type: conf.FileType) -> bool:
    """
    Check if a filename contains any of the patterns associated with a specific FileType.

    Parameters
    __________
        file: :class:`pathlib.Path`
            The path to the file to check

        file_type: :class:`pytrnsys_process.constants.FileType`
            The FileType enum containing patterns to match against

    Returns
    _______
        bool: bool
            True if the filename contains any of the patterns, False otherwise
    """
    file_name = file.stem.lower()
    return any(
        _re.search(pattern, file_name) for pattern in file_type.value.patterns
    )

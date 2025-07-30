"""
Configures logging for the pytrnsys_process package with three outputs:
1. Console output (INFO level) - Shows basic messages without stacktrace
2. Regular log file (INFO level) - Logs to pytrnsys_process.log without stacktrace
3. Debug log file (DEBUG level) - Logs to pytrnsys_process_debug.log with full stacktrace

The logging setup includes custom formatting for each handler and uses a TracebackInfoFilter
to control stacktrace visibility in different outputs. The main logger is configured at DEBUG
level to capture all logging events, while individual handlers control what gets displayed
in each output.

All handlers use the same log record.
Once the log record is modified and anything removed from it, will not be available in the other handlers.
"""

import logging as _logging
import pathlib as _pl
import sys as _sys


class _TracebackInfoFilter(_logging.Filter):
    """Clear or restore the exception on log records
    Copied from, seems to be only solution that works
    https://stackoverflow.com/questions/54605699/python-logging-disable-stack-trace
    """

    # pylint: disable=protected-access

    def __init__(self, clear=True):  # pylint: disable=super-init-not-called
        self.clear = clear

    def filter(self, record):
        if self.clear:
            record._exc_info_hidden, record.exc_info = record.exc_info, None
            # clear the exception traceback text cache, if created.
            record.exc_text = None
        elif hasattr(record, "_exc_info_hidden"):
            record.exc_info = record._exc_info_hidden
            del record._exc_info_hidden
        return True


_console_format = _logging.Formatter("%(levelname)s - %(message)s")

# Default console logger, used as default logger in functions
default_console_logger = _logging.getLogger("default_pytrnsys_process")
_default_console_handler = _logging.StreamHandler(_sys.stdout)
_default_console_handler.setLevel(_logging.INFO)
default_console_logger.addHandler(_default_console_handler)


def get_main_logger(path: _pl.Path) -> _logging.Logger:
    main_logger = _logging.getLogger("main_logger")

    # Check if handlers already exist to avoid duplicates
    if main_logger.handlers:
        return main_logger

    console_handler = _logging.StreamHandler(_sys.stdout)
    console_handler.setLevel(_logging.INFO)

    # Regular log file without stacktrace
    file_handler = _logging.FileHandler(
        path / "pytrnsys_process.log", mode="a"
    )
    file_handler.setLevel(_logging.INFO)

    # Debug log file with stacktrace
    debug_file_handler = _logging.FileHandler(
        path / "pytrnsys_process_debug.log", mode="a"
    )
    debug_file_handler.setLevel(_logging.DEBUG)

    # configure formatters
    file_format = _logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # set formatters
    console_handler.setFormatter(_console_format)
    file_handler.setFormatter(file_format)
    debug_file_handler.setFormatter(file_format)

    # add filters
    console_handler.addFilter(_TracebackInfoFilter())
    file_handler.addFilter(_TracebackInfoFilter())

    # Add this handler first because the other handlers will modify the log record
    main_logger.addHandler(debug_file_handler)
    main_logger.addHandler(console_handler)
    main_logger.addHandler(file_handler)

    main_logger.setLevel(_logging.DEBUG)

    return main_logger


def initialize_logs(path: _pl.Path):
    """Initialize log files by clearing their contents at the start of a new run."""
    # Clear main log files by opening them in write mode briefly
    with open(path / "pytrnsys_process.log", "w", encoding="utf-8"):
        pass
    with open(path / "pytrnsys_process_debug.log", "w", encoding="utf-8"):
        pass


def get_simulation_logger(simulation_path: _pl.Path) -> _logging.Logger:
    """Create a logger specific to a simulation directory.

    Parameters
    __________
        simulation_path:
            Path to the simulation directory

    Returns
    _______
        Logger instance configured to write to a log file in the simulation directory
    """
    sim_logger = _logging.getLogger(
        f"simulation_logger.{simulation_path.name}"
    )

    # Check if handlers already exist to avoid duplicates
    if sim_logger.handlers:
        return sim_logger

    log_file = simulation_path / "processing.log"
    sim_file_handler = _logging.FileHandler(log_file, mode="w")
    sim_file_handler.setLevel(_logging.INFO)

    # Use same format as main logger but without name since it's simulation specific
    sim_format = _logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    sim_file_handler.setFormatter(sim_format)

    sim_logger.addHandler(sim_file_handler)

    sim_logger.setLevel(_logging.INFO)

    return sim_logger

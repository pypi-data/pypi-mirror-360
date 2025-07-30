import logging as _logging
import pathlib as _pl
import time as _time
import typing as _tp
from collections import abc as _abc
from concurrent import futures as _futures

import matplotlib.pyplot as _plt
import pandas as _pd

from pytrnsys_process import config as conf
from pytrnsys_process import log, util
from pytrnsys_process.process import data_structures as ds
from pytrnsys_process.process import process_sim as ps


class UnableToProcessSimulationError(Exception):
    """Raised when a simulation cannot be processed."""


# pylint: disable=too-many-locals
def _process_batch(
    sim_folders: list[_pl.Path],
    processing_scenario: _tp.Union[
        _abc.Callable[[ds.Simulation], None],
        _tp.Sequence[_abc.Callable[[ds.Simulation], None]],
    ],
    results_folder: _pl.Path,
    parallel: bool = False,
    max_workers: int | None = None,
) -> ds.SimulationsData:
    """Common processing logic for both sequential and parallel batch processing.

    This internal function implements the core processing logic used by both sequential
    and parallel processing modes. It handles the setup of processing infrastructure,
    execution of processing tasks, and collection of results.

    Parameters
    __________
        sim_folders:
            List of simulation folders to process

        processing_scenario:
            Processing scenario(s) to apply to each simulation

        results_folder:
            Root folder containing all simulations

        parallel:
            Whether to process simulations in parallel

        max_workers:
            Maximum number of worker processes for parallel execution


    Returns
    _______
        SimulationsData containing the processed simulation results and metadata

    Note:
    _____
        This is an internal function that should not be called directly.
        Use process_single_simulation, process_whole_result_set, or
        process_whole_result_set_parallel instead.


    """
    start_time = _time.time()
    results = ds.ProcessingResults()
    simulations_data = ds.SimulationsData(
        path_to_simulations=results_folder.as_posix()
    )

    main_logger = log.get_main_logger(results_folder)

    if parallel:
        with _futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            tasks = {}
            for sim_folder in sim_folders:
                main_logger.info(
                    "Submitting simulation folder for processing: %s",
                    sim_folder.name,
                )
                tasks[
                    executor.submit(
                        _process_simulation,
                        sim_folder,
                        processing_scenario,
                        conf.global_settings.reader.force_reread_prt,
                    )
                ] = sim_folder

            for future in _futures.as_completed(tasks):
                try:
                    _handle_simulation_result(
                        future.result(), results, simulations_data
                    )
                except Exception as e:  # pylint: disable=broad-except
                    _handle_simulation_error(
                        e, tasks[future], results, main_logger
                    )
    else:
        for sim_folder in sim_folders:
            try:
                main_logger.info("Processing simulation: %s", sim_folder.name)
                result = _process_simulation(sim_folder, processing_scenario)
                _handle_simulation_result(result, results, simulations_data)
            except Exception as e:  # pylint: disable=broad-except
                _handle_simulation_error(e, sim_folder, results, main_logger)

    simulations_data = _concat_scalar(simulations_data)
    _log_processing_results(results, main_logger)

    end_time = _time.time()
    execution_time = end_time - start_time
    main_logger.info(
        "%s execution time: %.2f seconds",
        "Parallel" if parallel else "Total",
        execution_time,
    )

    return simulations_data


def _handle_simulation_result(
    result: tuple[ds.Simulation, list[str]],
    results: ds.ProcessingResults,
    simulations_data: ds.SimulationsData,
) -> None:
    """Handle the result of a processed simulation.

    Parameters
    __________
        result: Tuple of (simulation, failed_scenarios)
        sim_folder: Path to the simulation folder
        results: ProcessingResults to update
        simulations_data: SimulationsData to update
    """
    simulation, failed_scenarios = result
    results.processed_count += 1
    simulations_data.simulations[_pl.Path(simulation.path).name] = simulation
    if failed_scenarios:
        results.failed_scenarios[_pl.Path(simulation.path).name] = (
            failed_scenarios
        )


def _handle_simulation_error(
    error: Exception,
    sim_folder: _pl.Path,
    results: ds.ProcessingResults,
    main_logger: _logging.Logger,
) -> None:
    """Handle an error that occurred during simulation processing.

    Parameters
    __________
        error: The exception that occurred
        sim_folder: Path to the simulation folder
        results: ProcessingResults to update
    """
    results.error_count += 1
    results.failed_simulations.append(sim_folder.name)
    main_logger.error(
        "Failed to process simulation in %s: %s",
        sim_folder,
        str(error),
        exc_info=True,
    )


def process_single_simulation(
    sim_folder: _pl.Path,
    processing_scenario: _tp.Union[
        _abc.Callable[[ds.Simulation], None],
        _tp.Sequence[_abc.Callable[[ds.Simulation], None]],
    ],
) -> ds.Simulation:
    """Process a single simulation folder using the provided processing step/scenario.

    Parameters
    __________
        sim_folder: pathlib.Path
            Path to the simulation folder to process

        processing_scenario: collections.abc.Callable or collections.abc.Sequence of collections.abc.Callable
            They should contain the processing logic for a simulation.
            Each callable should take a Simulation object as its only parameter and modify it in place.

    Returns
    _______
        Simulation: :class:`pytrnsys_process.api.Simulation`

    Example
    _______
            >>> import pathlib as _pl
            >>> from pytrnsys_process import api
            ...
            >>> def processing_step_1(sim: api.Simulation):
            ...     # Process simulation data
            ...     pass
            >>> results = api.process_single_simulation(
            ...     _pl.Path("path/to/simulation"),
            ...     processing_step_1
            ... )
    """
    main_logger = log.get_main_logger(sim_folder)
    log.initialize_logs(sim_folder)
    main_logger.info("Starting processing of simulation %s", sim_folder)
    sim_folders = [sim_folder]
    simulations_data = _process_batch(
        sim_folders, processing_scenario, sim_folder.parent
    )
    try:
        return simulations_data.simulations[sim_folder.name]
    except KeyError as exc:
        raise UnableToProcessSimulationError(
            f"Failed to process simulation in {sim_folder}"
        ) from exc


def process_whole_result_set(
    results_folder: _pl.Path,
    processing_scenario: _tp.Union[
        _abc.Callable[[ds.Simulation], None],
        _tp.Sequence[_abc.Callable[[ds.Simulation], None]],
    ],
) -> ds.SimulationsData:
    """Process all simulation folders in a results directory sequentially.

    Processes each simulation folder found in the results directory one at a time,
    applying the provided processing step/scenario to each simulation.

    Using the default settings your structure should look like this:

    | results_folder
    |     ├─ sim-1
    |     ├─ sim-2
    |     ├─ sim-3
    |         ├─ temp
    |             ├─ your-printer-files.prt

    Parameters
    __________
        results_folder pathlib.Path:
            Path to the directory containing simulation folders.
            Each subfolder should contain a temp folder containing valid simulation data files.

        processing_scenario: collections.abc.Callable or collections.abc.Sequence of collections.abc.Callable
            They should containd the processing logic for a simulation.
            Each callable should take a Simulation object as its only parameter and modify it in place.

    Returns
    _______
        SimulationsData: :class:`pytrnsys_process.api.SimulationsData`
            - monthly: Dict mapping simulation names to monthly DataFrame results
            - hourly: Dict mapping simulation names to hourly DataFrame results
            - scalar: DataFrame containing scalar/deck values from all simulations

    Raises
    ______
        ValueError: If results_folder doesn't exist or is not a directory
        Exception: Individual simulation failures are logged but not re-raised

    Example
    _______
        >>> import pathlib as _pl
        >>> from pytrnsys_process import api
        ...
        >>> def processing_step_1(sim):
        ...     # Process simulation data
        ...     pass
        >>> def processing_step_2(sim):
        ...     # Process simulation data
        ...     pass
        >>> results = api.process_whole_result_set(
        ...     _pl.Path("path/to/results"),
        ...     [processing_step_1, processing_step_2]
        ... )
    """
    _validate_folder(results_folder)
    main_logger = log.get_main_logger(results_folder)
    log.initialize_logs(results_folder)
    main_logger.info(
        "Starting batch processing of simulations in %s", results_folder
    )

    sim_folders = [
        sim_folder
        for sim_folder in results_folder.iterdir()
        if sim_folder.is_dir()
    ]
    simulations_data = _process_batch(
        sim_folders, processing_scenario, results_folder
    )
    util.save_to_pickle(
        simulations_data,
        results_folder / conf.FileNames.SIMULATIONS_DATA_PICKLE_FILE.value,
    )

    return simulations_data


def process_whole_result_set_parallel(
    results_folder: _pl.Path,
    processing_scenario: _tp.Union[
        _abc.Callable[[ds.Simulation], None],
        _tp.Sequence[_abc.Callable[[ds.Simulation], None]],
    ],
    max_workers: int | None = None,
) -> ds.SimulationsData:
    """Process all simulation folders in a results directory in parallel.

    Uses a ProcessPoolExecutor to process multiple simulations concurrently,
    applying the provided processing step/scenario to each simulation.

    Using the default settings your structure should look like this:

    | results_folder
    |     ├─ sim-1
    |     ├─ sim-2
    |     ├─ sim-3
    |         ├─ temp
    |             ├─ your-printer-files.prt

    Parameters
    __________
        results_folder pathlib.Path:
            Path to the directory containing simulation folders.
            Each subfolder should contain a temp folder containing valid simulation data files.

        processing_scenario: collections.abc.Callable or collections.abc.Sequence of collections.abc.Callable
            They should containd the processing logic for a simulation.
            Each callable should take a Simulation object as its only parameter and modify it in place.
        max_workers int, default None:
            Maximum number of worker processes to use.
            If None, defaults to the number of processors on the machine.

    Returns
    _______
        SimulationsData: :class:`pytrnsys_process.api.SimulationsData`
            - monthly: Dict mapping simulation names to monthly DataFrame results
            - hourly: Dict mapping simulation names to hourly DataFrame results
            - scalar: DataFrame containing scalar/deck values from all simulations

    Raises
    _______
        ValueError: If results_folder doesn't exist or is not a directory
        Exception: Individual simulation failures are logged but not re-raised

    Example
    _______
        >>> import pathlib as _pl
        >>> from pytrnsys_process import api
        ...
        >>> def processing_step_1(sim):
        ...     # Process simulation data
        ...     pass
        >>> def processing_step_2(sim):
        ...     # Process simulation data
        ...     pass
        >>> results = api.process_whole_result_set_parallel(
        ...     _pl.Path("path/to/results"),
        ...     [processing_step_1, processing_step_2]
        ... )
    """
    # The last :returns: ensures that the formatting works in PyCharm
    _validate_folder(results_folder)
    log.initialize_logs(results_folder)
    main_logger = log.get_main_logger(results_folder)
    main_logger.info(
        "Starting batch processing of simulations in %s with parallel execution",
        results_folder,
    )

    sim_folders = [
        sim_folder
        for sim_folder in results_folder.iterdir()
        if sim_folder.is_dir()
    ]
    simulations_data = _process_batch(
        sim_folders,
        processing_scenario,
        results_folder,
        parallel=True,
        max_workers=max_workers,
    )
    util.save_to_pickle(
        simulations_data,
        results_folder / conf.FileNames.SIMULATIONS_DATA_PICKLE_FILE.value,
    )

    return simulations_data


def do_comparison(
    comparison_scenario: _tp.Union[
        _abc.Callable[[ds.SimulationsData], None],
        _abc.Sequence[_abc.Callable[[ds.SimulationsData], None]],
    ],
    simulations_data: _tp.Optional[ds.SimulationsData] = None,
    results_folder: _tp.Optional[_pl.Path] = None,
) -> ds.SimulationsData:
    """Execute comparison scenarios on processed simulation results.

    Parameters
    __________
        comparison_scenario: collections.abc.Callable or collections.abc.Sequence of collections.abc.Callable
            They should containd the comparison logic.
            Each callable should take a SimulationsData object as its only parameter and modify it in place.

        simulations_data: SimulationsData, optional
            SimulationsData object containing the processed
            simulations data to be compared.

        results_folder: pathlib.Path, optional
            Path to the directory containing simulation results.
            Used if simulations_data is not provided.

    Returns
    _______
        SimulationsData: :class:`pytrnsys_process.api.SimulationsData`

    Example
    __________
        >>> from pytrnsys_process import api
        ...
        >>> def comparison_step(simulations_data: ds.SimulationsData):
        ...     # Compare simulation results
        ...     pass
        ...
        >>> api.do_comparison(comparison_step, simulations_data=processed_results)
    """
    if not simulations_data:
        if not results_folder:
            raise ValueError(
                "Either simulations_data or results_folder must be provided to perform comparison"
            )
        path_to_simulations_data = (
            results_folder / conf.FileNames.SIMULATIONS_DATA_PICKLE_FILE.value
        )
        if (
            path_to_simulations_data.exists()
            and not conf.global_settings.reader.force_reread_prt
        ):
            simulations_data = util.load_simulations_data_from_pickle(
                path_to_simulations_data
            )
            # Moving locations of files breaks the paths.
            # If the pickle file is found, then we know the new path is correct.
            # The original path is saved for later retrieval.
            simulations_data.path_to_simulations_original = (
                simulations_data.path_to_simulations
            )
            if not simulations_data.path_to_simulations == str(results_folder):
                simulations_data.path_to_simulations = str(results_folder)

        else:
            simulations_data = process_whole_result_set_parallel(
                results_folder, []
            )
    main_logger = log.get_main_logger(
        _pl.Path(simulations_data.path_to_simulations)
    )
    _process_comparisons(simulations_data, comparison_scenario, main_logger)

    return simulations_data


def _process_comparisons(
    simulations_data: ds.SimulationsData,
    comparison_scenario: _tp.Union[
        _abc.Callable[[ds.SimulationsData], None],
        _abc.Sequence[_abc.Callable[[ds.SimulationsData], None]],
    ],
    main_logger: _logging.Logger,
):
    scenario = (
        [comparison_scenario]
        if callable(comparison_scenario)
        else comparison_scenario
    )
    for step in scenario:
        try:
            step(simulations_data)
            _plt.close("all")
        except Exception as e:  # pylint: disable=broad-except
            scenario_name = getattr(step, "__name__", str(step))
            main_logger.error(
                "Scenario %s failed for comparison: %s ",
                scenario_name,
                str(e),
                exc_info=True,
            )


def _concat_scalar(simulation_data: ds.SimulationsData) -> ds.SimulationsData:
    scalar_values_to_concat = {
        sim_name: sim.scalar
        for sim_name, sim in simulation_data.simulations.items()
        if not sim.scalar.empty
    }
    if scalar_values_to_concat:
        simulation_data.scalar = _pd.concat(
            scalar_values_to_concat.values(),
            keys=scalar_values_to_concat.keys(),
        ).droplevel(1)
    return simulation_data


def _validate_folder(folder: _pl.Path) -> None:
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")


def _process_simulation(
    sim_folder: _pl.Path,
    processing_scenarios: _tp.Union[
        _abc.Callable[[ds.Simulation], None],
        _tp.Sequence[_abc.Callable[[ds.Simulation], None]],
    ],
    force_reread_prt: _tp.Optional[bool] = None,
) -> tuple[ds.Simulation, list[str]]:
    if not force_reread_prt:
        force_reread_prt = conf.global_settings.reader.force_reread_prt
    sim_logger = log.get_simulation_logger(sim_folder)
    sim_logger.info("Starting simulation processing")
    sim_pickle_file = sim_folder / conf.FileNames.SIMULATION_PICKLE_FILE.value
    simulation: ds.Simulation
    if sim_pickle_file.exists() and not force_reread_prt:
        sim_logger.info("Loading simulation from pickle file")
        simulation = util.load_simulation_from_pickle(
            sim_pickle_file, sim_logger
        )
    else:
        sim_logger.info("Processing simulation from raw files")
        sim_files = util.get_files([sim_folder])
        simulation = ps.process_sim(sim_files, sim_folder)
        if sim_files:
            util.save_to_pickle(simulation, sim_pickle_file, sim_logger)

    failed_scenarios = []

    # Convert single scenario to list for uniform handling
    scenarios = (
        [processing_scenarios]
        if callable(processing_scenarios)
        else processing_scenarios
    )

    for scenario in scenarios:
        try:
            scenario_name = getattr(scenario, "__name__", str(scenario))
            sim_logger.info("Running scenario: %s", scenario_name)
            scenario(simulation)
            sim_logger.info(
                "Successfully completed scenario: %s", scenario_name
            )
            _plt.close("all")
        except Exception as e:  # pylint: disable=broad-except
            failed_scenarios.append(scenario_name)
            sim_logger.error(
                "Scenario %s failed: %s",
                scenario_name,
                str(e),
                exc_info=True,
            )

    if failed_scenarios:
        sim_logger.warning(
            "Simulation completed with %d failed scenarios",
            len(failed_scenarios),
        )
    else:
        sim_logger.info("Simulation completed successfully")

    return simulation, failed_scenarios


def _log_processing_results(
    results: ds.ProcessingResults, main_logger: _logging.Logger
) -> None:
    main_logger.info("=" * 80)
    main_logger.info("BATCH PROCESSING SUMMARY")
    main_logger.info("-" * 80)
    main_logger.info(
        "Total simulations processed: %d | Failed: %d",
        results.processed_count,
        results.error_count,
    )

    if results.error_count > 0:
        main_logger.warning(
            "Some simulations failed to process. Check the log for details."
        )
        main_logger.warning("Failed simulations:")
        for sim in results.failed_simulations:
            main_logger.warning("  • %s", sim)

    if results.failed_scenarios:
        main_logger.warning("Failed scenarios by simulation:")
        for sim, scenarios in results.failed_scenarios.items():
            if scenarios:
                main_logger.warning("  • %s:", sim)
                for scenario in scenarios:
                    main_logger.warning("    - %s", scenario)
    main_logger.info("=" * 80)

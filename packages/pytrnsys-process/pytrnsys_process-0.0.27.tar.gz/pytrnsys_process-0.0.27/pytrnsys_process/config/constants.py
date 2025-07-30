import pathlib as _pl
from dataclasses import dataclass
from enum import Enum

import pytrnsys_process as pp


class PlotSizes(Enum):
    A4 = (7.8, 3.9)
    A4_HALF = (3.8, 3.9)


@dataclass(frozen=True)
class FilePattern:
    patterns: list[str]
    prefix: str


class FileType(Enum):
    MONTHLY = FilePattern(patterns=["_mo_", "_mo$", "^mo_"], prefix="mo_")
    HOURLY = FilePattern(patterns=["_hr_", "_hr$", "^hr_"], prefix="hr_")
    TIMESTEP = FilePattern(
        patterns=["_step_", "_step$", "^step_"],
        prefix="step_",
    )
    HYDRAULIC = FilePattern(
        patterns=["_mfr_", "_mfr$", "_t$"],
        prefix="step_",
    )
    DECK = ".dck"


class FileNames(Enum):
    SIMULATION_PICKLE_FILE = "simulation.pickle"
    SIMULATIONS_DATA_PICKLE_FILE = "simulations_data.pickle"


REPO_ROOT: _pl.Path = _pl.Path(pp.__file__).parents[1]
"""
Path to the repository root
"""

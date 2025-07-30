from collections import abc as _abc
from dataclasses import dataclass, field
from enum import Enum

from pytrnsys_process.config import constants as const


@dataclass
class Plot:  # pylint: disable=too-many-instance-attributes
    """
    Class holding the global settings for plots.

    Attributes
    __________
    file_formats: list[str]
        List of file formats to which the plots will be exported when asked.

    figure_sizes:
        Dictionary of figure sizes to save to file.
        By default these the 'A4 plot' will fit horizontally on an A4 page.
        Two of the 'half A4 plot' can fit horizontally on an A4 page.


    inkscape_path:
        Path to the installation of Inkscape.
        This is required to save plots to the EMF format.


    date_format:
        Formatting to use when plotting datetimes.


    """

    file_formats: _abc.Sequence[str] = field(
        default_factory=lambda: [".png", ".pdf", ".emf"]
    )

    figure_sizes: dict[str, tuple[float, float]] = field(
        default_factory=lambda: {
            const.PlotSizes.A4.name: const.PlotSizes.A4.value,
            const.PlotSizes.A4_HALF.name: const.PlotSizes.A4_HALF.value,
        }
    )

    inkscape_path: str = "C://Program Files//Inkscape//bin//inkscape.exe"

    date_format: str = "%b %Y"
    label_font_size: int = 10
    legend_font_size: int = 8
    title_font_size: int = 12
    markers: _abc.Sequence[str] = field(
        default_factory=lambda: [
            "x",
            "o",
            "^",
            "D",
            "v",
            "<",
            ">",
            "p",
            "*",
            "s",
        ]
    )


@dataclass
class Reader:
    """
    Class holding global settings for the reading files.

    Attributes
    __________
        folder_name_for_printer_files: str
            Name of the data folder inside the simulation directly (Default: 'temp')

        read_step_files: bool
            Step files are ignored by default.

        read_deck_files: bool
            Deck files are parsed for constants by default.

        force_reread_prt: bool
            Processing will use the faster pickle files, unless this is True.

        starting_year: int
            The reader will use this to set the year in which the data starts in the datetime index.
    """

    folder_name_for_printer_files: str = "temp"
    read_step_files: bool = False
    read_deck_files: bool = True
    force_reread_prt: bool = False
    starting_year: int = 2024


@dataclass
class Settings:
    """
    Class holding the global settings for processing.

    Attributes
    __________
        plot: Plot
            class holding global settings for plots

        reader: Reader
            class holding global settings for readers

    """

    plot: Plot

    reader: Reader


class Defaults(Enum):
    """Default settings for different use cases"""

    DEFAULT = Settings(plot=Plot(), reader=Reader())


global_settings: Settings = Defaults.DEFAULT.value

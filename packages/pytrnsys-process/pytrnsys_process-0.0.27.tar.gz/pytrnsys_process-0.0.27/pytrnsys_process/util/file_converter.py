import logging as _logging
import pathlib as _pl
import re as _re

import pandas as _pd

from pytrnsys_process import config as conf
from pytrnsys_process import log, read
from pytrnsys_process.process import file_type_detector as ftd


class CsvConverter:

    @staticmethod
    def rename_file_with_prefix(
        file_path: _pl.Path,
        prefix: conf.FileType,
        logger: _logging.Logger = log.default_console_logger,
    ) -> None:
        """Rename a file with a given prefix.

        Parameters
        __________
            file_path:
                Path to the file to rename
            prefix:
                FileType enum value specifying the prefix to use

        Returns
        _______
            Path: :class:`pathlib.Path`
                Path to the renamed file

        Raises
        ______
            FileNotFoundError: If the file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")

        new_name = f"{prefix.value.prefix}{file_path.name}"
        new_path = file_path.parent / new_name
        file_path.rename(new_path)

        logger.info("Renamed %s to %s", file_path, new_path)

    def convert_sim_results_to_csv(
        self,
        input_path: _pl.Path,
        output_dir: _pl.Path,
        logger: _logging.Logger = log.default_console_logger,
    ) -> None:
        """Convert TRNSYS simulation results to CSV format.

        Parameters
        __________
            input_path: :class:`pathlib.Path`
                Path to input file or directory containing input files

            output_dir: :class:`pathlib.Path`
                Directory where CSV files will be saved

        Raises
        ______
            ValueError: If a file doesn't match any known pattern
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        input_files = (
            [input_path] if input_path.is_file() else input_path.iterdir()
        )

        for input_file in input_files:
            if input_file.is_dir():
                continue

            if ftd.has_pattern(input_file, conf.FileType.MONTHLY):
                df = read.PrtReader().read_monthly(input_file)
                output_stem = self._refactor_filename(
                    input_file.stem,
                    conf.FileType.MONTHLY.value.patterns,
                    conf.FileType.MONTHLY.value.prefix,
                )
            elif ftd.has_pattern(input_file, conf.FileType.HOURLY):
                df = read.PrtReader().read_hourly(input_file)
                output_stem = self._refactor_filename(
                    input_file.stem,
                    conf.FileType.HOURLY.value.patterns,
                    conf.FileType.HOURLY.value.prefix,
                )
            elif ftd.has_pattern(input_file, conf.FileType.TIMESTEP):
                df = read.PrtReader().read_step(input_file)
                output_stem = self._refactor_filename(
                    input_file.stem,
                    conf.FileType.TIMESTEP.value.patterns,
                    conf.FileType.TIMESTEP.value.prefix,
                )
            else:
                logger.warning(
                    "Unknown file type: %s, will try to detect via timestamps",
                    input_file.name,
                )
                output_stem, df = self.using_file_content_read_appropriately(
                    input_file
                )

            output_file = output_dir / f"{output_stem}.csv"
            df.to_csv(output_file, index=True, encoding="UTF8")

    @staticmethod
    def using_file_content_read_appropriately(
        file_path: _pl.Path,
        logger: _logging.Logger = log.default_console_logger,
    ) -> tuple[str, _pd.DataFrame]:
        """Read the file according to the file contents."""
        prt_reader = read.PrtReader()
        file_type = ftd.get_file_type_using_file_content(file_path)
        if file_type == conf.FileType.MONTHLY:
            df_monthly = read.PrtReader().read_monthly(file_path)
            monthly_file = (
                f"{conf.FileType.MONTHLY.value.prefix}{file_path.stem}".lower()
            )
            logger.info(
                "Converted %s to monthly file: %s", file_path, monthly_file
            )
            return monthly_file, df_monthly
        if file_type == conf.FileType.HOURLY:
            df_hourly = prt_reader.read_hourly(file_path)
            hourly_file = (
                f"{conf.FileType.HOURLY.value.prefix}{file_path.stem}".lower()
            )
            logger.info(
                "Converted %s to hourly file: %s", file_path, hourly_file
            )
            return hourly_file, df_hourly
        if file_type == conf.FileType.TIMESTEP:
            df_step = prt_reader.read_step(file_path, skipfooter=23, header=1)
            timestamp_file = f"{conf.FileType.TIMESTEP.value.prefix}{file_path.stem}".lower()
            logger.info(
                "Converted %s to timestamp file: %s", file_path, timestamp_file
            )
            return timestamp_file, df_step
        if file_type == conf.FileType.HYDRAULIC:
            df_step = prt_reader.read_step(file_path)
            timestamp_file = f"{conf.FileType.TIMESTEP.value.prefix}{file_path.stem}".lower()
            logger.info(
                "Converted %s to timestamp file: %s", file_path, timestamp_file
            )
            return timestamp_file, df_step
        raise ValueError(
            f"Could not determine appropriate file type for {file_path}"
        )

    @staticmethod
    def _refactor_filename(
        filename: str, patterns: list[str], prefix: str
    ) -> str:
        """Process filename by removing patterns and adding appropriate prefix.

        Parameters
        __________
            filename:
                The original filename to process

            patterns:
                List of regex patterns to remove from filename

            prefix:
                Prefix to add to the processed filename

        Returns
        _______
            The processed filename with patterns removed and prefix added
        """
        processed_name = filename.lower()
        for pattern in patterns:
            if pattern not in ("_mfr$", "_t$"):
                processed_name = _re.sub(pattern, "", processed_name)
        return f"{prefix}{processed_name}"

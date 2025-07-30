import typing as _tp
from abc import abstractmethod
from dataclasses import dataclass

import matplotlib.pyplot as _plt
import numpy as _np
import pandas as _pd

from pytrnsys_process import config as conf

# TODO: provide A4 and half A4 plots to test sizes in latex # pylint: disable=fixme
# TODO: provide height as input for plot?  # pylint: disable=fixme
# TODO: deal with legends (curve names, fonts, colors, linestyles) # pylint: disable=fixme
# TODO: clean up old stuff by refactoring # pylint: disable=fixme
# TODO: make issue for docstrings of plotting # pylint: disable=fixme
# TODO: Add colormap support # pylint: disable=fixme


# TODO find a better place for this to live in # pylint : disable=fixme
plot_settings = conf.global_settings.plot
"Settings shared by all plots"


class ChartBase:
    cmap: str | None = None

    def plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        **kwargs,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = self._do_plot(df, columns, **kwargs)
        return fig, ax

    @abstractmethod
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        """Implement actual plotting logic in subclasses"""

    def check_for_cmap(self, kwargs, plot_kwargs):
        if "cmap" not in kwargs and "colormap" not in kwargs:
            plot_kwargs["cmap"] = self.cmap
        return plot_kwargs

    def get_cmap(self, kwargs) -> str | None:
        if not kwargs:
            return self.cmap

        if "cmap" not in kwargs and "colormap" not in kwargs:
            return self.cmap

        if "cmap" in kwargs:
            return kwargs["cmap"]

        if "colormap" in kwargs:
            return kwargs["colormap"]

        raise ValueError  # pragma: no cover

    @staticmethod
    def get_fig_and_ax(kwargs, size):
        if "fig" not in kwargs and "ax" not in kwargs:
            fig, ax = _plt.subplots(
                figsize=size,
                layout="constrained",
            )
            kwargs["ax"] = ax
        else:
            fig = kwargs["fig"]
            ax = kwargs["ax"]
        return fig, ax


class StackedBarChart(ChartBase):
    cmap: str | None = "inferno_r"

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = self.get_fig_and_ax(kwargs, size)

        plot_kwargs = {
            "stacked": True,
            "legend": use_legend,
            **kwargs,
        }
        self.check_for_cmap(kwargs, plot_kwargs)
        ax = df[columns].plot.bar(**plot_kwargs)
        ax.set_xticklabels(
            _pd.to_datetime(df.index).strftime(plot_settings.date_format)
        )

        return fig, ax


class BarChart(ChartBase):
    cmap = None

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        # TODO: deal with colors  # pylint: disable=fixme
        fig, ax = self.get_fig_and_ax(kwargs, size)

        x = _np.arange(len(df.index))
        width = 0.8 / len(columns)

        cmap = self.get_cmap(kwargs)
        if cmap:
            cm = _plt.cm.get_cmap(cmap)
            colors = cm(_np.linspace(0, 1, len(columns)))
        else:
            colors = [None] * len(columns)

        for i, col in enumerate(columns):
            ax.bar(x + i * width, df[col], width, label=col, color=colors[i])

        if use_legend:
            ax.legend()

        ax.set_xticks(x + width * (len(columns) - 1) / 2)
        ax.set_xticklabels(
            _pd.to_datetime(df.index).strftime(plot_settings.date_format)
        )
        ax.tick_params(axis="x", labelrotation=90)
        return fig, ax


class LinePlot(ChartBase):
    cmap: str | None = None

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = self.get_fig_and_ax(kwargs, size)

        plot_kwargs = {
            "legend": use_legend,
            **kwargs,
        }
        self.check_for_cmap(kwargs, plot_kwargs)

        df[columns].plot.line(**plot_kwargs)
        return fig, ax


@dataclass()
class Histogram(ChartBase):
    bins: int = 50

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = self.get_fig_and_ax(kwargs, size)

        plot_kwargs = {
            "legend": use_legend,
            "bins": self.bins,
            **kwargs,
        }
        self.check_for_cmap(kwargs, plot_kwargs)
        df[columns].plot.hist(**plot_kwargs)
        return fig, ax


def _validate_inputs(
    current_class,
    columns: list[str],
) -> None:
    if len(columns) != 2:
        raise ValueError(
            f"\n{type(current_class).__name__} requires exactly 2 columns (x and y)"
        )


class ScatterPlot(ChartBase):
    cmap = "Paired"  # This is ignored when no categorical groupings are used.

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        _validate_inputs(self, columns)
        x_column, y_column = columns

        fig, ax = self.get_fig_and_ax(kwargs, size)
        df.plot.scatter(x=x_column, y=y_column, **kwargs)

        return fig, ax


class ScalarComparePlot(ChartBase):
    """Handles comparative scatter plots with dual grouping by color and markers."""

    cmap = "Paired"  # This is ignored when no categorical groupings are used.

    # pylint: disable=too-many-arguments,too-many-locals, too-many-positional-arguments
    def _do_plot(  # type: ignore[override]
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        group_by_color: str | None = None,
        group_by_marker: str | None = None,
        line_kwargs: dict[str, _tp.Any] | None = None,
        scatter_kwargs: dict[str, _tp.Any] | None = None,
    ) -> tuple[_plt.Figure, _plt.Axes]:

        _validate_inputs(self, columns)
        x_column, y_column = columns

        # ===========================================
        # The following simplifies the code later on,
        # while being compatible with linting.
        if not line_kwargs:
            line_kwargs = {}
        if not scatter_kwargs:
            scatter_kwargs = {}
        # ===========================================

        if group_by_color and group_by_marker:
            # See: https://stackoverflow.com/questions/4700614/
            # how-to-put-the-legend-outside-the-plot
            # This is required to place the legend in a dedicated subplot
            fig, (ax, lax) = _plt.subplots(
                layout="constrained",
                figsize=size,
                ncols=2,
                gridspec_kw={"width_ratios": [4, 1]},
            )
            secondary_axis_used = True
        else:
            secondary_axis_used = False
            fig, ax = self.get_fig_and_ax({}, size)
            lax = ax

        df_grouped, group_values = self._prepare_grouping(
            df, group_by_color, group_by_marker
        )
        cmap = self.get_cmap(line_kwargs)
        color_map, marker_map = self._create_style_mappings(
            *group_values, cmap=cmap
        )

        self._plot_groups(
            df_grouped,
            x_column,
            y_column,
            color_map,
            marker_map,
            ax,
            line_kwargs,
            scatter_kwargs,
        )

        use_color_legend = False
        if group_by_color:
            use_color_legend = True

        if use_legend:
            self._create_legends(
                lax,
                color_map,
                marker_map,
                group_by_color,
                group_by_marker,
                use_color_legend=use_color_legend,
                secondary_axis_used=secondary_axis_used,
            )

        return fig, ax

    @staticmethod
    def _prepare_grouping(
        df: _pd.DataFrame,
        by_color: str | None,
        by_marker: str | None,
    ) -> tuple[
        _pd.core.groupby.generic.DataFrameGroupBy, tuple[list[str], list[str]]
    ]:
        group_by = []
        if by_color:
            group_by.append(by_color)
        if by_marker:
            group_by.append(by_marker)

        df_grouped = df.groupby(group_by)

        color_values = sorted(df[by_color].unique()) if by_color else []
        marker_values = sorted(df[by_marker].unique()) if by_marker else []

        return df_grouped, (color_values, marker_values)

    @staticmethod
    def _create_style_mappings(
        color_values: list[str],
        marker_values: list[str],
        cmap: str | None,
    ) -> tuple[dict[str, _tp.Any], dict[str, str]]:
        if color_values:
            cm = _plt.get_cmap(cmap, len(color_values))
            color_map = {val: cm(i) for i, val in enumerate(color_values)}
        else:
            cm = _plt.get_cmap(cmap, len(marker_values))
            color_map = {val: cm(i) for i, val in enumerate(marker_values)}
        if marker_values:
            marker_map = dict(zip(marker_values, plot_settings.markers))
        else:
            marker_map = {}

        return color_map, marker_map

    # pylint: disable=too-many-arguments
    @staticmethod
    def _plot_groups(
        df_grouped: _pd.core.groupby.generic.DataFrameGroupBy,
        x_column: str,
        y_column: str,
        color_map: dict[str, _tp.Any],
        marker_map: dict[str, str] | str,
        ax: _plt.Axes,
        line_kwargs: dict[str, _tp.Any],
        scatter_kwargs: dict[str, _tp.Any],
    ) -> None:
        ax.set_xlabel(x_column, fontsize=plot_settings.label_font_size)
        ax.set_ylabel(y_column, fontsize=plot_settings.label_font_size)
        for val, group in df_grouped:
            sorted_group = group.sort_values(x_column)
            x = sorted_group[x_column]
            y = sorted_group[y_column]

            plot_args = {"color": "black"}
            if color_map:
                plot_args["color"] = color_map[val[0]]

            for key, value in line_kwargs.items():
                if key not in ["cmap", "colormap"]:
                    plot_args[key] = value

            scatter_args = {"marker": "None", "color": "black", "alpha": 0.5}
            if marker_map:
                scatter_args["marker"] = marker_map[val[-1]]

            for key, value in scatter_kwargs.items():
                if key in ["marker"] and marker_map:
                    continue

                scatter_args[key] = value

            ax.plot(x, y, **plot_args)  # type: ignore
            ax.scatter(x, y, **scatter_args)  # type: ignore

    def _create_legends(
        self,
        lax: _plt.Axes,
        color_map: dict[str, _tp.Any],
        marker_map: dict[str, str],
        color_legend_title: str | None,
        marker_legend_title: str | None,
        use_color_legend: bool,
        secondary_axis_used: bool,
    ) -> None:

        if secondary_axis_used:
            # Secondary axis should be turned off.
            # Primary axis should stay the same.
            lax.axis("off")

        if use_color_legend:
            self._create_color_legend(
                lax,
                color_map,
                color_legend_title,
                bool(marker_map),
                secondary_axis_used,
            )
        if marker_map:
            self._create_marker_legend(
                lax,
                marker_map,
                marker_legend_title,
                bool(use_color_legend),
                secondary_axis_used,
            )

    @staticmethod
    def _create_color_legend(
        lax: _plt.Axes,
        color_map: dict[str, _tp.Any],
        color_legend_title: str | None,
        has_markers: bool,
        secondary_axis_used: bool,
    ) -> None:
        color_handles = [
            _plt.Line2D([], [], color=color, linestyle="-", label=label)
            for label, color in color_map.items()
        ]

        if secondary_axis_used:
            loc = "upper left"
            alignment = "left"
        else:
            loc = "best"
            alignment = "center"

        legend = lax.legend(
            handles=color_handles,
            title=color_legend_title,
            bbox_to_anchor=(0, 0, 1, 1),
            loc=loc,
            alignment=alignment,
            fontsize=plot_settings.legend_font_size,
            borderaxespad=0,
        )

        if has_markers:
            lax.add_artist(legend)

    @staticmethod
    def _create_marker_legend(
        lax: _plt.Axes,
        marker_map: dict[str, str],
        marker_legend_title: str | None,
        has_colors: bool,
        secondary_axis_used: bool,
    ) -> None:
        marker_position = 0.7 if has_colors else 1
        marker_handles = [
            _plt.Line2D(
                [],
                [],
                color="black",
                marker=marker,
                linestyle="None",
                label=label,
            )
            for label, marker in marker_map.items()
            if label is not None
        ]

        if secondary_axis_used:
            loc = "upper left"
            alignment = "left"
        else:
            loc = "best"
            alignment = "center"

        lax.legend(
            handles=marker_handles,
            title=marker_legend_title,
            bbox_to_anchor=(0, 0, 1, marker_position),
            loc=loc,
            alignment=alignment,
            fontsize=plot_settings.legend_font_size,
            borderaxespad=0,
        )

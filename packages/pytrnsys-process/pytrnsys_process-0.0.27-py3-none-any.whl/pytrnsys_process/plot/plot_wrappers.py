"""Plotting wrappers to provide a simplified interface to the User, while allow development of reusable OOP structures.

Note
____
    Many of these plotting routines do not add labels and legends.
    This should be done using the figure and axis handles afterwards.
"""

import typing as _tp
from collections import abc as _abc

import matplotlib.pyplot as _plt
import pandas as _pd

from pytrnsys_process import config as conf
from pytrnsys_process.plot import plotters as pltrs


def line_plot(
    df: _pd.DataFrame,
    columns: list[str],
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a line plot using the provided DataFrame columns.

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments are documented in
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.line_plot(simulation.hourly, ["QSrc1TIn", "QSrc1TOut"])
    """
    _validate_column_exists(df, columns)
    plotter = pltrs.LinePlot()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def bar_chart(
    df: _pd.DataFrame,
    columns: list[str],
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a bar chart with multiple columns displayed as grouped bars.
    The **kwargs are currently not passed on.

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.bar_chart(simulation.monthly, ["QSnk60P","QSnk60PauxCondSwitch_kW"])
    """
    _validate_column_exists(df, columns)
    plotter = pltrs.BarChart()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def stacked_bar_chart(
    df: _pd.DataFrame,
    columns: list[str],
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Bar chart with stacked bars

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.stacked_bar_chart(simulation.monthly, ["QSnk60P","QSnk60PauxCondSwitch_kW"])
    """
    _validate_column_exists(df, columns)
    plotter = pltrs.StackedBarChart()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def histogram(
    df: _pd.DataFrame,
    columns: list[str],
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    bins: int = 50,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a histogram from the given DataFrame columns.

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    bins: int
        number of histogram bins to be used

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.histogram(simulation.hourly, ["QSrc1TIn"], ylabel="")
    """
    _validate_column_exists(df, columns)
    plotter = pltrs.Histogram(bins)
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def energy_balance(
    df: _pd.DataFrame,
    q_in_columns: list[str],
    q_out_columns: list[str],
    q_imb_column: _tp.Optional[str] = None,
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a stacked bar chart showing energy balance with inputs, outputs and imbalance.
    This function creates an energy balance visualization where:

    - Input energies are shown as positive values
    - Output energies are shown as negative values
    - Energy imbalance is either provided or calculated as (sum of inputs + sum of outputs)

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    q_in_columns: list of str
        column names representing energy inputs

    q_out_columns: list of str
        column names representing energy outputs

    q_imb_column: list of str, optional
        column name containing pre-calculated energy imbalance

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.energy_balance(
        >>> simulation.monthly,
        >>> q_in_columns=["QSnk60PauxCondSwitch_kW"],
        >>> q_out_columns=["QSnk60P", "QSnk60dQlossTess", "QSnk60dQ"],
        >>> q_imb_column="QSnk60qImbTess",
        >>> xlabel=""
        >>> )
    """
    all_columns_vor_validation = (
        q_in_columns
        + q_out_columns
        + ([q_imb_column] if q_imb_column is not None else [])
    )
    _validate_column_exists(df, all_columns_vor_validation)

    df_modified = df.copy()

    for col in q_out_columns:
        df_modified[col] = -df_modified[col]

    if q_imb_column is None:
        q_imb_column = "Qimb"
        df_modified[q_imb_column] = df_modified[
            q_in_columns + q_out_columns
        ].sum(axis=1)

    columns_to_plot = q_in_columns + q_out_columns + [q_imb_column]

    plotter = pltrs.StackedBarChart()
    return plotter.plot(
        df_modified,
        columns_to_plot,
        use_legend=use_legend,
        size=size,
        **kwargs,
    )


def scatter_plot(
    df: _pd.DataFrame,
    x_column: str,
    y_column: str,
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a scatter plot to show numerical relationships between x and y variables.

    Note
    ____
    Use color and not cmap!

    See: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.scatter.html


    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    x_column: str
        coloumn name for x-axis values

    y_column: str
        coloumn name for y-axis values


    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot.scatter`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        Simple scatter plot

        >>> api.scatter_plot(
        ...     simulation.monthly, x_column="QSnk60dQlossTess", y_column="QSnk60dQ"
        ... )

    """
    if "cmap" in kwargs:
        raise ValueError(
            "\nscatter_plot does not take a 'cmap'."
            "\nPlease use color instead."
        )

    columns_to_validate = [x_column, y_column]
    _validate_column_exists(df, [x_column, y_column])
    df = df[columns_to_validate]
    plotter = pltrs.ScatterPlot()

    return plotter.plot(
        df,
        columns=[x_column, y_column],
        use_legend=use_legend,
        size=size,
        **kwargs,
    )


# pylint: disable=too-many-arguments, too-many-positional-arguments
def scalar_compare_plot(
    df: _pd.DataFrame,
    x_column: str,
    y_column: str,
    group_by_color: str | None = None,
    group_by_marker: str | None = None,
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    scatter_kwargs: dict[str, _tp.Any] | None = None,
    line_kwargs: dict[str, _tp.Any] | None = None,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a scalar comparison plot with up to two grouping variables.
    This visualization allows simultaneous analysis of:

    - Numerical relationships between x and y variables
    - Categorical grouping through color encoding
    - Secondary categorical grouping through marker styles

    Note
    ____
    To change the figure properties a separation is included.
    scatter_kwargs are used to change the markers.
    line_kwargs are used to change the lines.

    See:
    - markers: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.scatter.html
    - lines: https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html


    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    x_column: str
        column name for x-axis values

    y_column: str
        column name for y-axis values

    group_by_color: str, optional
        column name for color grouping

    group_by_marker: str, optional
        column name for marker style grouping

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    line_kwargs:
        Additional keyword arguments to pass on to
        :meth:`matplotlib.axes.Axes.plot`.

    scatter_kwargs:
        Additional keyword arguments to pass on to
        :meth:`matplotlib.axes.Axes.scatter`.

    **kwargs :
        Should never be used!
        Use 'line_kwargs' or 'scatter_kwargs' instead.


    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        Compare plot

        >>> api.scalar_compare_plot(
        ...     comparison_data,
        ...     x_column="VIceSscaled",
        ...     y_column="VIceRatioMax",
        ...     group_by_color="yearly_demand_GWh",
        ...     group_by_marker="ratioDHWtoSH_allSinks",
        ... )


    """
    if kwargs:
        raise ValueError(
            f"\nTo adjust the figure properties, \nplease use the scatter_kwargs "
            f"to change the marker properties, \nand please use the line_kwargs "
            f"to change the line properties."
            f"\nReceived: {kwargs}"
        )

    if not group_by_marker and not group_by_color:
        raise ValueError(
            "\nAt least one of 'group_by_marker' or 'group_by_color' has to be set."
            f"\nFor a normal scatter plot, please use '{scatter_plot.__name__}'."
        )

    columns_to_validate = [x_column, y_column]
    if group_by_color:
        columns_to_validate.append(group_by_color)
    if group_by_marker:
        columns_to_validate.append(group_by_marker)
    _validate_column_exists(df, columns_to_validate)
    df = df[columns_to_validate]
    plotter = pltrs.ScalarComparePlot()
    return plotter.plot(
        df,
        columns=[x_column, y_column],
        group_by_color=group_by_color,
        group_by_marker=group_by_marker,
        use_legend=use_legend,
        size=size,
        scatter_kwargs=scatter_kwargs,
        line_kwargs=line_kwargs,
    )


def _validate_column_exists(
    df: _pd.DataFrame, columns: _abc.Sequence[str]
) -> None:
    """Validate that all requested columns exist in the DataFrame.

    Since PyTRNSYS is case-insensitive but Python is case-sensitive, this function
    provides helpful suggestions when columns differ only by case.

    Parameters
    __________
        df: DataFrame to check
        columns: Sequence of column names to validate

    Raises
    ______
        ColumnNotFoundError: If any columns are missing, with suggestions for case-mismatched names
    """
    missing_columns = set(columns) - set(df.columns)
    if not missing_columns:
        return

    # Create case-insensitive mapping of actual column names
    column_name_mapping = {col.casefold(): col for col in df.columns}

    # Categorize missing columns
    suggestions = []
    not_found = []

    for col in missing_columns:
        if col.casefold() in column_name_mapping:
            correct_name = column_name_mapping[col.casefold()]
            suggestions.append(f"'{col}' did you mean: '{correct_name}'")
        else:
            not_found.append(f"'{col}'")

    # Build error message
    parts = []
    if suggestions:
        parts.append(
            f"Case-insensitive matches found:\n{', \n'.join(suggestions)}\n"
        )
    if not_found:
        parts.append(f"No matches found for:\n{', \n'.join(not_found)}")

    error_msg = "Column validation failed. " + "".join(parts)
    raise ColumnNotFoundError(error_msg)


def get_figure_with_twin_x_axis() -> tuple[_plt.Figure, _plt.Axes, _plt.Axes]:
    """
    Used to make figures with different y axes on the left and right.
    To create such a figure, pass the lax to one plotting method and pass the rax to another.

    Warning
    _______
    Be careful when combining plots. MatPlotLib will not complain when you provide incompatible x-axes.
    An example:
    combining a time-series with dates with a histogram with temperatures.
    In this case, the histogram will disappear without any feedback.

    Note
    ____
    The legend of a twin_x plot is a special case:
    To have all entries into a single plot, use `fig.legend`
    https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.legend.html

    To instead have two separate legends, one for each y-axis, use `lax.legend` and `rax.legend`.
    https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.legend.html


    Returns
    -------
    fig:
        Figure object

    lax:
        Axis object for the data on the left y-axis.

    rax:
        Axis object for the data on the right y-axis.

    Examples
    ________
    .. plot::
        :context: close-figs

        Twin axis plot with a single legend

        >>> fig, lax, rax = api.get_figure_with_twin_x_axis()
        >>> api.line_plot(simulation.monthly, ["QSnk60P",], ylabel="Power [kWh]", use_legend=False, fig=fig, ax=lax)
        >>> api.line_plot(simulation.monthly, ["QSnk60qImbTess", "QSnk60dQlossTess", "QSnk60dQ"], marker="*",
        ...     ylabel="Fluxes [kWh]", use_legend=False, fig=fig, ax=rax)
        >>> fig.legend(loc="center", bbox_to_anchor=(0.6, 0.7))

    .. plot::
        :context: close-figs

        Twin axis plot with two legends

        >>> fig, lax, rax = api.get_figure_with_twin_x_axis()
        >>> api.line_plot(simulation.monthly, ["QSnk60P",], ylabel="Power [kWh]", use_legend=False, fig=fig, ax=lax)
        >>> api.line_plot(simulation.monthly, ["QSnk60qImbTess", "QSnk60dQlossTess", "QSnk60dQ"], marker="*",
        ...     ylabel="Fluxes [kWh]", use_legend=False, fig=fig, ax=rax)
        >>> lax.legend(loc="center left")
        >>> rax.legend(loc="center right")
    """
    fig, lax = pltrs.ChartBase.get_fig_and_ax({}, conf.PlotSizes.A4.value)
    rax = lax.twinx()
    return fig, lax, rax


class ColumnNotFoundError(Exception):
    """This exception is raised when given column names are not available in the dataframe"""

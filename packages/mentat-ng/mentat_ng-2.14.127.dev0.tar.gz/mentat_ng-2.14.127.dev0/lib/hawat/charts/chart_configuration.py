"""
This file contains functions for generating JSON objects for rendering charts using plotly.
"""

import datetime
import json
from collections.abc import Iterable
from math import ceil, isnan
from typing import TYPE_CHECKING, Literal, Optional, cast

import flask
import pandas as pd
import plotly.express as px
import plotly.graph_objects as pgo
import pytz
from flask_babel import gettext
from plotly.colors import sequential, unlabel_rgb

from . import const
from .const import ChartJSONType, DataComplexity
from mentat.stats.idea import TimeBoundType, TimelineCFG

if TYPE_CHECKING:
    from .model import PivotTableChartConfig, SecondaryChartConfig, TimelineChartConfig


def get_chart_json_no_data() -> ChartJSONType:
    """
    Generate a JSON object for rendering a chart to be rendered when no data is available.
    """
    fig = px.scatter([])
    fig.update_layout(
        annotations=[
            {
                "text": gettext("There is no data to be displayed"),
                "showarrow": False,
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "font": {"size": 20},
            }
        ],
        xaxis=pgo.layout.XAxis(
            visible=False,
            fixedrange=True,  # Disable zooming of the chart
        ),
        yaxis=pgo.layout.YAxis(
            visible=False,
            fixedrange=True,  # Disable zooming of the chart
        ),
        autosize=True,
        plot_bgcolor=const.TRANSPARENT,
        paper_bgcolor=const.TRANSPARENT,
    )
    return _chart_set_config_and_get_dict(fig)


def get_chart_json_timeline(
    df: pd.DataFrame,
    config: "TimelineChartConfig",
    timeline_cfg: TimelineCFG,
    x_axis_label_override: Optional[str] = None,
    forced_timezone: Optional[str] = None,
) -> ChartJSONType:
    """
    Generate a timeline chart as a JSON object for rendering using plotly.
    """

    buckets: list[pd.Timestamp] = list(df.index)

    all_buckets_formatted = [b.isoformat() + "Z" for b in buckets]

    column_name = str(config.column_name)
    value_name = str(config.value_name)

    hover_data: dict[str, bool | list[str]] = {"bucket": all_buckets_formatted}
    column_labels: dict[str, str] = {"bucket": gettext("Time")}

    if config.data_complexity == DataComplexity.NONE:
        hover_data.update(variable=False)
        column_labels.update(value=column_name)
    else:
        column_labels.update(set=column_name, variable=column_name, value=value_name)

    fig = px.bar(
        df,
        y=df.columns,
        labels={"bucket": gettext("Time"), **column_labels},
        color_discrete_sequence=const.COLOR_LIST,
        hover_data=hover_data,
    )

    nth_bucket = ceil(len(buckets) / const.NUMBER_OF_LABELED_TICKS)

    tick_values = all_buckets_formatted[::nth_bucket]
    ticks_formatted = _format_ticks(buckets[::nth_bucket], forced_timezone=forced_timezone)
    fig.update_layout(
        xaxis=pgo.layout.XAxis(
            type="category",  # Otherwise, when the first bucket is misaligned, the x-axis is scaled improperly
            linecolor=const.AXIS_LINE_COLOR,
            tickmode="array",  # tickmode, tickvals, and ticktext are set due to plot.ly not allowing
            tickvals=tick_values,  # a sane method for automatically formatting tick labels.
            ticktext=ticks_formatted,  # (tickformat does not allow for custom timezone formatting)
            fixedrange=True,  # Disable zooming of the chart
            title_text=x_axis_label_override or _get_x_axis_label(timeline_cfg),
        ),
        yaxis=pgo.layout.YAxis(
            linecolor=const.AXIS_LINE_COLOR,
            gridcolor=const.GRID_COLOR,
            fixedrange=True,  # Disable zooming of the chart
            title_text=gettext("count"),
        ),
        legend=pgo.layout.Legend(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        autosize=True,
        plot_bgcolor=const.TRANSPARENT,
        paper_bgcolor=const.TRANSPARENT,
    )

    return _chart_set_config_and_get_dict(fig)


def get_chart_json_bar(df: pd.DataFrame, config: "SecondaryChartConfig") -> ChartJSONType:
    """
    Generate a bar chart as a JSON object for rendering using plotly.
    """
    fig = px.bar(
        df,
        orientation="h",
        x="count",
        y="set",
        labels={
            "set": str(config.column_name),
            "count": str(config.value_name),
        },
    )
    fig.update_layout(
        xaxis=pgo.layout.XAxis(
            linecolor=const.AXIS_LINE_COLOR,
            gridcolor=const.GRID_COLOR,
            fixedrange=True,  # Disable zooming of the chart
            title_text=gettext("count"),
        ),
        yaxis=pgo.layout.YAxis(
            linecolor=const.AXIS_LINE_COLOR,
            fixedrange=True,  # Disable zooming of the chart
            autorange="reversed",  # Show highest counts first
        ),
        autosize=True,
        plot_bgcolor=const.TRANSPARENT,
        paper_bgcolor=const.TRANSPARENT,
    )

    return _chart_set_config_and_get_dict(fig)


def get_chart_json_pie(df: pd.DataFrame, config: "SecondaryChartConfig") -> ChartJSONType:
    """
    Generate a pie chart as a JSON object for rendering using plotly.
    """
    custom_percentage_labels = [_get_pie_percentage(row) for _, row in df.iterrows()]

    fig = px.pie(
        df,
        values="count",
        names="set",
        labels={
            "set": str(config.column_name),
            "count": str(config.value_name),
        },
        color_discrete_sequence=const.COLOR_LIST,
        hole=0.5,
        hover_data={"count": config.d3_format},
        category_orders={"set": df["set"].tolist()},  # Enforce original order of values
    )

    fig.update_traces(text=custom_percentage_labels, textinfo="text")

    fig.update_layout(showlegend=False)
    return _chart_set_config_and_get_dict(fig)


def _get_color(val: float) -> str:
    if isnan(val):
        return "rgb(255, 255, 255)"
    scale: list[str] = sequential.Blues
    color_index = min(round(val * (len(scale) - 1)), len(scale) - 1)
    return scale[color_index]


def _get_contrasting_font_color(rgb_color_str: str) -> Literal["black", "white"]:
    """
    Calculates whether black or white font has better contrast with a given hex background color.
    Handles common named colors by converting them to hex.
    """
    r, g, b = unlabel_rgb(rgb_color_str)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "black" if luminance > 128 else "white"


def get_chart_json_pivot_table(
    config: "PivotTableChartConfig", observed_df: pd.DataFrame, residuals_df: Optional[pd.DataFrame] = None
) -> ChartJSONType:
    """
    Generate a pivot table as a JSON object for rendering using plotly.
    The table cells are colored based on the Pearson residuals in residuals_df.
    """
    table_headers = [""] + list(observed_df.columns)
    table_cells_text = []

    for idx in observed_df.index:
        row_text = [str(idx)] + [str(val) for val in observed_df.loc[idx]]
        table_cells_text.append(row_text)

    table_text_transposed = list(map(list, zip(*table_cells_text)))

    # Default colors
    header_color = "rgb(240, 240, 240)"
    index_color = "rgb(240, 240, 240)"
    cell_fill_color = "rgb(255, 255, 255)"

    # The first column in our transposed color list is for the row index
    table_color_transposed = [[index_color] * len(observed_df.index)]

    if residuals_df is not None:
        max_residual: float = residuals_df.max().max()
        min_residual: float = residuals_df.min().min()
        residual_scaler = max_residual - min_residual
        if residual_scaler == 0:
            norm_residuals = residuals_df.copy()
        else:
            norm_residuals = (residuals_df - min_residual) / residual_scaler

        color_df = norm_residuals.map(_get_color)
        table_color_transposed += [list(color_df[col]) for col in color_df.columns]
    else:
        table_color_transposed += [[cell_fill_color] * len(observed_df.index)] * len(observed_df.columns)

    table_font_color_transposed = [
        [_get_contrasting_font_color(color) for color in row] for row in table_color_transposed
    ]

    fig = pgo.Figure(
        data=pgo.Table(
            header={
                "values": table_headers,
                "fill_color": header_color,
                "align": "center",
                "height": config.header_height,
            },
            cells={
                "values": table_text_transposed,
                "fill_color": table_color_transposed,
                "font": {"color": table_font_color_transposed},
                "align": "center",
                "height": config.cell_height,
            },
        )
    )

    return _chart_set_config_and_get_dict(fig)


def _chart_set_config_and_get_dict(fig: pgo.Figure) -> ChartJSONType:
    """
    Get JSON encodable dict representation of chart,
    disable rendering of mode bar, and make the chart responsive.

    The default dict export method for plotly figure is not json encodable,
    and there is no other way to set config than directly modifying the dict object.
    """
    fig_dict = ChartJSONType(json.loads(fig.to_json()))

    config = fig_dict.setdefault("config", {})
    config["displayModeBar"] = False
    config["responsive"] = True

    return fig_dict


def _format_ticks(buckets: Iterable[datetime.datetime], forced_timezone: Optional[str] = None) -> list[str]:
    """
    Format the bucket ticks for the timeline chart.
    """
    tz = pytz.timezone(forced_timezone or flask.session.get("timezone") or "UTC")
    localized_buckets = [
        b.replace(tzinfo=datetime.UTC).astimezone(tz).replace(tzinfo=None).isoformat(sep=" ") for b in buckets
    ]

    # offsets in isoformat for year, month, day, minute, second and fractions of second
    for i in (4, 7, 10, 16, 19, *range(21, 26)):
        res = [b[:i] for b in localized_buckets]
        if len(set(res)) == len(res):
            return res
    return localized_buckets


def _get_pie_percentage(row: pd.Series) -> str:
    if row[const.KEY_SHARE] < const.PIE_CHART_SHOW_PERCENTAGE_CUTOFF:
        return ""
    return f"{row[const.KEY_SHARE]:.2%}"


def _get_x_axis_label(timeline_cfg: TimelineCFG) -> str:
    """
    Get the x-axis label for the timeline chart.
    """
    if timeline_cfg.time_type == TimeBoundType.DETECTION_TIME:
        return cast(str, gettext("detection time"))
    if timeline_cfg.time_type == TimeBoundType.STORAGE_TIME:
        return cast(str, gettext("storage time"))
    return cast(str, gettext("time"))

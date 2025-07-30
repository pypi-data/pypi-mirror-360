"""
This file contains data models for the charts module.
"""

import dataclasses
import typing
from abc import ABC
from collections.abc import Callable, Hashable, Iterable, Iterator
from typing import Any, Literal, NamedTuple, Optional, Self, overload

import pandas as pd
from flask_babel import format_decimal, lazy_gettext
from flask_babel.speaklater import LazyString

from . import chart_configuration, const
from .const import (
    ChartJSONType,
    ChartRenderer,
    ChartType,
    DataComplexity,
    InputDataFormat,
    InputDataFormatLong,
    InputDataFormatWide,
    PivotItems,
    TableType,
)
from mentat.stats.idea import (
    ST_SKEY_REST,
    DataLongType,
    DataRowType,
    DataWideType,
    StatisticsDataType,
    StatType,
    TimelineCFG,
)


class ChartData(ABC):
    """Class representing data required to render a chart."""

    renderer: ChartRenderer
    """Renderer to be used for rendering the chart."""

    chart_type: ChartType
    """Name of the type"""

    chart: ChartJSONType
    """JSON of chart to be rendered on the frontend."""

    df: pd.DataFrame
    """Pandas DataFrame to be used for rendering a table for the chart."""

    config: "ChartConfig"
    """Configuration for the chart."""

    def to_dict(self) -> list[dict[Hashable, Any]]:
        """Returns json-serializable representation of the data."""
        return self.df.reset_index().to_dict("records")

    def __iter__(self) -> Iterator[ChartJSONType | pd.DataFrame]:
        """Iterate over the rows of the data frame."""
        yield from (self.chart, self.df)

    def get_css_style(self) -> str:
        """
        Returns CSS style for the chart.
        This is used to set the height of the chart container.
        """
        return "height: 700px; width: 100%;"


class TimelineChartData(ChartData):
    renderer: Literal[ChartRenderer.PLOTLY] = ChartRenderer.PLOTLY
    chart_type: Literal[ChartType.TIMELINE] = ChartType.TIMELINE
    config: "TimelineChartConfig"

    timeline_cfg: TimelineCFG

    @overload
    def __init__(
        self,
        data: DataWideType,
        config: "TimelineChartConfig",
        timeline_cfg: TimelineCFG,
        data_format: InputDataFormatWide,
        add_rest: bool = False,
        x_axis_label_override: LazyString | str | None = None,
        forced_timezone: Optional[str] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        data: DataLongType,
        config: "TimelineChartConfig",
        timeline_cfg: TimelineCFG,
        data_format: InputDataFormatLong,
        add_rest: bool = False,
        x_axis_label_override: LazyString | str | None = None,
        forced_timezone: Optional[str] = None,
    ) -> None: ...

    def __init__(
        self,
        data: DataWideType | DataLongType,
        config: "TimelineChartConfig",
        timeline_cfg: TimelineCFG,
        data_format: InputDataFormat,
        add_rest: bool = False,
        x_axis_label_override: LazyString | str | None = None,
        forced_timezone: Optional[str] = None,
    ) -> None:
        """
        Expects `data` to be sorted by bucket in ascending order.

        if add_rest is true, the data is modified so it only contains `const.MAX_VALUE_COUNT`
        columns, and the rest will be stored under `__REST__` (Useful, when the source statistics do not
        already contain `__REST__`, and need to be abridged)
        """

        if data_format == InputDataFormat.LONG_SIMPLE and config.data_complexity != DataComplexity.NONE:
            raise ValueError("LONG_SIMPLE data format can only support data complexity of NONE")

        self.timeline_cfg = timeline_cfg
        self.config = config

        if data_format == InputDataFormat.WIDE_SIMPLE:
            data = typing.cast(DataWideType, data)
            df = self._from_wide_simple(data, config)
        elif data_format == InputDataFormat.WIDE_COMPLEX:
            data = typing.cast(DataWideType, data)
            df = self._from_wide_complex(data, config)
        elif data_format == InputDataFormat.LONG_SIMPLE:
            data = typing.cast(DataLongType, data)
            df = self._from_long_simple(data, config)
        elif data_format == InputDataFormat.LONG_COMPLEX:
            data = typing.cast(DataLongType, data)
            df = self._from_long_complex(data)
        else:
            raise ValueError(f"Invalid value '{data_format}' for type InputDataFormat")

        df = self._move_rest_to_end(df)

        if add_rest:
            df = self._add_rest(df)

        if df.empty:
            self.chart = chart_configuration.get_chart_json_no_data()
        else:
            self.chart = chart_configuration.get_chart_json_timeline(
                df,
                config,
                timeline_cfg,
                forced_timezone=forced_timezone,
                x_axis_label_override=None if x_axis_label_override is None else str(x_axis_label_override),
            )

        df[const.KEY_SUM] = df.sum(axis=1)  # add sum of each bucket as a last column
        self.df = df

    @staticmethod
    def _from_long_simple(data: DataLongType, config: "TimelineChartConfig") -> pd.DataFrame:
        """
        Converts from `InputDataFormat.LONG_SIMPLE` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(data)
        df.set_index("bucket", inplace=True)
        df.rename(columns={"count": str(config.column_name)}, inplace=True)
        return df

    @staticmethod
    def _from_long_complex(data: DataLongType) -> pd.DataFrame:
        """
        Converts from `InputDataFormat.LONG_COMPLEX` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(data)

        # Similar to:
        # df = pd.DataFrame(data).pivot(
        #     columns='set',
        #     index='bucket',
        #     values='count'
        # )
        # But retains the order of columns
        return df.groupby(["bucket", "set"], sort=False)["count"].sum().unstack()

    @staticmethod
    def _from_wide_simple(data: DataWideType, config: "TimelineChartConfig") -> pd.DataFrame:
        """
        Converts from `InputDataFormat.WIDE_SIMPLE` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(TimelineChartData._iter_wide_simple_data(data, config))
        df.set_index("bucket", inplace=True)
        return df

    @staticmethod
    def _from_wide_complex(data: DataWideType, config: "TimelineChartConfig") -> pd.DataFrame:
        """
        Converts from `InputDataFormat.WIDE_COMPLEX` to a unified pandas DataFrame for timeline.
        """
        df = pd.DataFrame(TimelineChartData._iter_wide_complex_data(data, config))
        df.fillna(0, inplace=True)
        df.set_index("bucket", inplace=True)
        return df

    @staticmethod
    def _iter_wide_simple_data(data: DataWideType, config: "TimelineChartConfig") -> Iterator[DataRowType]:
        for bucket, stat in data:
            row: DataRowType = {"bucket": bucket}
            for data_key in config.iter_data_keys():
                row[str(data_key.display_name)] = typing.cast(int | float, stat.get(data_key.key, 0))
            yield row

    @staticmethod
    def _iter_wide_complex_data(data: DataWideType, config: "TimelineChartConfig") -> Iterator[DataRowType]:
        for bucket, stat in data:
            yield {
                "bucket": bucket,
                **typing.cast(DataRowType, stat.get(config.key, {})),
            }

    @staticmethod
    def _move_rest_to_end(df: pd.DataFrame) -> pd.DataFrame:
        """
        Moves the `__REST__` column to the end of the timeline dataframe.
        """
        if ST_SKEY_REST in df.columns:
            df.insert(len(df.columns) - 1, ST_SKEY_REST, df.pop(ST_SKEY_REST))
        return df

    @staticmethod
    def _add_rest(df: pd.DataFrame) -> pd.DataFrame:
        """
        Abridges the dataframe for secondary charts to contain only `const.MAX_VALUE_COUNT`
        columns, and stores the rest under `__REST__` column.
        """
        if df.shape[1] > const.MAX_VALUE_COUNT:
            kept_columns = df.iloc[:, : const.MAX_VALUE_COUNT - 1]
            df[ST_SKEY_REST] = df.iloc[:, const.MAX_VALUE_COUNT - 1 :].sum(axis=1)
            return pd.concat([kept_columns, df[[ST_SKEY_REST]]], axis=1)

        return df


class SecondaryChartData(ChartData):
    renderer: Literal[ChartRenderer.PLOTLY] = ChartRenderer.PLOTLY
    chart_type: Literal[ChartType.SECONDARY] = ChartType.SECONDARY
    config: "SecondaryChartConfig"

    def __init__(
        self,
        statistics: StatisticsDataType,
        config: "SecondaryChartConfig",
        data_format: InputDataFormat,
        total_count: Optional[int] = None,
        add_rest: bool = False,
        sort: bool = False,
    ) -> None:
        """
        if total count not provided, it is calculated as the sum of all counts in the data frame.

        if add_rest is true, the data is modified so it only contains `const.MAX_VALUE_COUNT`
        rows, and the rest will be stored under `__REST__` (Useful, when the source statistics do
        not already contain `__REST__`, and need to be abridged)

        sort should be set to True, if the source data is not yet sorted.
        """

        self.config = config

        if data_format == InputDataFormat.WIDE_SIMPLE:
            data_iter: Iterable[dict[str, str | int | float]] = (
                {
                    "set": str(data_key.display_name),
                    "count": typing.cast(int | float, statistics.get(data_key.key)),
                }
                for data_key in config.iter_data_keys()
            )
        elif config.key in statistics:
            data_iter = (
                {"set": key, "count": val} for key, val in typing.cast(StatType, statistics[config.key]).items()
            )
        else:
            data_iter = []

        df = pd.DataFrame(data_iter)

        if sort and not df.empty:
            df = df.sort_values(by="count", ascending=False)

        df = self._move_rest_to_end(df)

        if add_rest:
            df = self._add_rest(df)

        if total_count is None and "count" in df.columns:
            total_count = df["count"].sum()

        if total_count and "count" in df.columns:
            df[const.KEY_SHARE] = df["count"] / total_count
        else:
            df[const.KEY_SHARE] = 0.0

        if df.empty:
            self.chart = chart_configuration.get_chart_json_no_data()
        elif config.data_complexity == DataComplexity.SINGLE:
            self.chart = chart_configuration.get_chart_json_pie(df, config)
        elif config.data_complexity == DataComplexity.MULTI:
            self.chart = chart_configuration.get_chart_json_bar(df, config)

        if "set" in df.columns:
            df.set_index("set", inplace=True)

        self.df = df

    @staticmethod
    def _move_rest_to_end(df: pd.DataFrame) -> pd.DataFrame:
        """
        Moves the `__REST__` row to the end of the secondary dataframe.
        """
        if "set" not in df.columns:
            return df

        rest_row = df[df["set"] == ST_SKEY_REST]
        df = df[df["set"] != ST_SKEY_REST]
        return pd.concat([df, rest_row])

    @staticmethod
    def _add_rest(df: pd.DataFrame) -> pd.DataFrame:
        """
        Abridges the dataframe for secondary charts to contain only `const.MAX_VALUE_COUNT`
        rows, and stores the rest under `__REST__`.
        """
        if df.shape[0] > const.MAX_VALUE_COUNT:
            kept_rows = df.iloc[: const.MAX_VALUE_COUNT - 1]
            rest_sum = df.iloc[const.MAX_VALUE_COUNT - 1 :]["count"].sum()
            sum_row = pd.DataFrame({"set": [ST_SKEY_REST], "count": [rest_sum]})
            return pd.concat([kept_rows, sum_row])
        return df


class PivotTableChartData(ChartData):
    renderer: Literal[ChartRenderer.PLOTLY] = ChartRenderer.PLOTLY
    chart_type: Literal[ChartType.PIVOT_TABLE] = ChartType.PIVOT_TABLE
    config: "PivotTableChartConfig"
    table_shape: tuple[int, int]

    def __init__(
        self,
        data: PivotItems,
        config: "PivotTableChartConfig",
    ) -> None:
        df = pd.DataFrame(data)
        if df.empty:
            self.chart = chart_configuration.get_chart_json_no_data()
        elif "standardized_residual" in df.columns:
            df_main = df.pivot(index="row_category", columns="col_category", values="observed")
            self.table_shape = df_main.shape
            df_res = df.pivot(index="row_category", columns="col_category", values="standardized_residual")
            self.chart = chart_configuration.get_chart_json_pivot_table(config, df_main, df_res)
            df = pd.concat([df_main, df_res])
        else:
            df = df.pivot(index="row_category", columns="col_category", values="observed")
            self.table_shape = df.shape
            self.chart = chart_configuration.get_chart_json_pivot_table(config, df)
        self.df = df
        self.config = config

    def get_css_style(self) -> str:
        base_height = 180  # Plotly automatically adds some padding
        height = base_height + self.config.header_height + self.config.cell_height * self.table_shape[0]
        width = self.config.cell_width * (self.table_shape[1] + 1)
        return f"min-height: 700px; max-height: 1400px; height: {height}px; min-width: 100%; width: {width}px;"


class DataKey(NamedTuple):
    key: str
    display_name: LazyString | str


@dataclasses.dataclass(frozen=True, kw_only=True)
class TableConfig:
    table_type: TableType
    """Type of the table to be shown next to the chart."""

    column_name: LazyString | str
    """Name for the column containing the aggregated categories."""

    value_name: LazyString | str = lazy_gettext("Count")
    """Name for the column containing the counts for aggregated category."""

    csag_group: Optional[str] = None
    """
    Context search group the table headers belong to.
    """

    allow_table_aggregation: Optional[bool] = None
    """
    Enables/disables aggregation footers in the chart tables.
    If unset, timeline charts, and pie charts will contain aggregation footer,
    secondary bar charts will not.
    """

    format_function: Callable = format_decimal
    """Function to be used for formatting values in the table."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class ChartConfigBase(TableConfig):
    """Defines the base configuration for all charts."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class TimelineSecondaryChartConfigBase(ChartConfigBase):
    key: str
    """Key, under which chart and table date is expected to be stored in the response context."""

    data_complexity: DataComplexity
    """Used to determine which secondary chart to use and to structure hover labels for timeline charts."""

    d3_format: str | bool = True
    """
    D3 format string to be used for formatting values in hover text for charts.
    If True, the plotly default format is used. If False, value is ommited.
    """

    data_keys: Optional[list[DataKey]] = None
    """
    Keys which store the data for visualization in WIDE SIMPLE data format.
    If the data format is not WIDE_SIPMLE, this is ignored.
    If None, only the single key stored in `key` will be used.
    """

    def iter_data_keys(self) -> Iterator[DataKey]:
        """Iterate over all data keys for the chart section"""
        if self.data_keys is not None:
            yield from self.data_keys
        else:
            yield DataKey(self.key, self.column_name)


@dataclasses.dataclass(frozen=True, kw_only=True)
class TimelineChartConfig(TimelineSecondaryChartConfigBase):
    table_type: TableType = TableType.TOGGLEABLE
    chart_type: Literal[ChartType.TIMELINE] = ChartType.TIMELINE


@dataclasses.dataclass(frozen=True, kw_only=True)
class SecondaryChartConfig(TimelineSecondaryChartConfigBase):
    data_complexity: Literal[DataComplexity.SINGLE, DataComplexity.MULTI]
    table_type: TableType = TableType.COLUMNS
    chart_type: Literal[ChartType.SECONDARY] = ChartType.SECONDARY


@dataclasses.dataclass(frozen=True, kw_only=True)
class PivotTableChartConfig(ChartConfigBase):
    chart_type: Literal[ChartType.PIVOT_TABLE] = ChartType.PIVOT_TABLE
    """Key, under which chart and table date is expected to be stored in the response context."""
    table_type: TableType = TableType.NONE
    cell_height: int = 30  # px
    header_height: int = 30  # px
    cell_width: int = 200  # px


ChartConfig = TimelineChartConfig | SecondaryChartConfig | PivotTableChartConfig


class ChartSection(NamedTuple):
    key: str
    """Key of the chart section."""

    label: LazyString | str
    """Name shown on the tab label."""

    short_description: LazyString | str | None
    """Text shown as the header of the tab."""

    description: LazyString | str | None
    """Long, descriptive text shown right under the header of the tab."""

    chart_configs: tuple[ChartConfig, ...]
    """Configurations for the charts in the section."""

    data: tuple[ChartData, ...] = ()

    def add_data(self, *args: ChartData) -> "ChartSection":
        """Add provided chart data to the chart section"""

        assert len(self.data) + len(args) <= len(self.chart_configs), "Too many chart data provided for the section"
        assert all(chc == data.config for chc, data in zip(self.chart_configs[len(self.data) :], args)), (
            "Mismatched chart config"
        )

        return self._replace(data=self.data + args)

    @classmethod
    def new_common(
        cls: type[Self],
        key: str,
        label: LazyString | str,
        short_description: LazyString | str,
        description: LazyString | str,
        data_complexity: DataComplexity,
        column_name: LazyString | str,
        csag_group: Optional[str] = None,
        data_keys: Optional[list[DataKey]] = None,
    ) -> Self:
        """
        Create a new chart section with the most common configuration of
        one timeline and an optional secondary chart.
        """
        return cls(
            key=key,
            label=label,
            short_description=short_description,
            description=description,
            chart_configs=(
                TimelineChartConfig(
                    key=key,
                    data_complexity=data_complexity,
                    column_name=column_name,
                    csag_group=csag_group or key,
                    data_keys=data_keys,
                ),
                *(
                    [
                        SecondaryChartConfig(
                            key=key,
                            data_complexity=data_complexity,
                            column_name=column_name,
                            csag_group=csag_group or key,
                            data_keys=data_keys,
                        ),
                    ]
                    if data_complexity != DataComplexity.NONE
                    else []
                ),
            ),
        )

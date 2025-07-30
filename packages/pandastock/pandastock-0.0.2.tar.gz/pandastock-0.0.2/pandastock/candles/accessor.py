from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from pandastock.indicators.base import Indicator, PlotPosition


@pd.api.extensions.register_dataframe_accessor('candles')
class CandlesAccessor:

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

        self._indicators: dict[str, Indicator] = {}

        # {RSI(...): {'rsi_14__rsi': 'rsi'}}
        self._indicators_col_names_mappings: dict[Indicator, dict[str, str]] = defaultdict(dict)

    def _validate(self, pandas_obj):
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in pandas_obj.columns for col in required_columns):
            raise AttributeError(
                'DataFrame must have columns: {}'.format(', '.join(required_columns)),
            )

    def add_indicators(self, **kwargs: Indicator) -> None:
        self._indicators.update(kwargs)
        for name, indicator in kwargs.items():
            indicator_values = indicator.build(self._obj)
            for col in indicator.build(self._obj):
                new_col = f'{name}__{col}'
                self._obj[new_col] = indicator_values[col]
                self._indicators_col_names_mappings[indicator][new_col] = col  # type: ignore

    def _plot_candles(self, left: int, right: int, axis: Axes) -> None:
        for idx, (time, row) in enumerate(self._obj[left:right].iterrows()):
            color = 'g' if row['close'] >= row['open'] else 'r'
            axis.plot([idx, idx], [row['low'], row['high']], color='black', linewidth=1)
            axis.add_patch(
                Rectangle(
                    (idx-0.3, min(row['open'], row['close'])),
                    0.6,
                    abs(row['close'] - row['open']),
                    color=color,
                    alpha=0.7,
                ),
            )
        axis.set_ylabel('Price')

    def _plot_volume(self, left: int, right: int, axes: Axes) -> None:
        axes.bar(
            range(right - left),
            self._obj[left:right]['volume'],
            color='skyblue',
            width=0.8,
            alpha=0.7,
            label='Volume',
        )
        axes.set_ylabel('Volume')
        axes.legend()

    def _plot_indicators_over(self, left: int, right: int, axes: Axes) -> None:
        indicators = {
            n: i
            for n, i in self._indicators.items()
            if i.plot_position == PlotPosition.over
        }

        for _, indicator in indicators.items():
            indicator.plot(
                (
                    self
                    ._obj[left:right][list(self._indicators_col_names_mappings[indicator].keys())]
                    .rename(columns=self._indicators_col_names_mappings[indicator])
                ),
                axes,
            )

    def _plot_indicators_under(self, left: int, right: int, axes_list: list[Axes]) -> None:
        indicators = {
            n: i
            for n, i in self._indicators.items()
            if i.plot_position == PlotPosition.under
        }
        for axes, (_, indicator) in zip(axes_list, indicators.items()):
            indicator.plot(
                (
                    self
                    ._obj[left:right][list(self._indicators_col_names_mappings[indicator].keys())]
                    .rename(columns=self._indicators_col_names_mappings[indicator])
                ),
                axes,
            )

    def plot(
        self,
        center_time: pd.Timestamp | str,
        from_: pd.Timestamp | str | None = None,
        to_: pd.Timestamp | str | None = None,
        window: int = 30,
        figsize: tuple[int, int] = (14, 10),
    ) -> None:
        center_loc: int = self._obj.index.get_loc(center_time)  # type: ignore
        left = (
            max(center_loc - window, 0)
            if not from_
            else self._obj.index.get_loc(from_)
        )
        right = (
            min(center_loc + window + 1, len(self._obj))
            if not to_
            else self._obj.index.get_loc(to_)
        )

        subplots_count = (
            2
            + sum(1 for i in self._indicators.values() if i.plot_position == PlotPosition.under)
        )
        _, axes = plt.subplots(
            nrows=subplots_count,  # +1 for volume
            ncols=1,
            sharex=True,
            figsize=figsize,
            gridspec_kw={'height_ratios': [3, 1] + [1 for _ in range(subplots_count - 2)]},
        )

        self._plot_candles(left, right, axes[0])
        self._plot_volume(left, right, axes[1])
        self._plot_indicators_over(left, right, axes[0])
        self._plot_indicators_under(left, right, axes[2:])

        # --- xticks с поворотом ---
        xticks_idx = range(0, (right - left), max(1, (right - left) // 10))
        xticks_labels = [self._obj[left:right].index[i].strftime('%m-%d %H:%M') for i in xticks_idx]
        axes[-1].set_xticks(xticks_idx)
        axes[-1].set_xticklabels(xticks_labels, rotation=45)

        # --- Вертикальная линия по центру ---
        center_rel = center_loc - left
        for subax in axes:
            subax.axvline(center_rel, color='orange', linestyle='--', linewidth=1)

        plt.tight_layout()
        plt.show()

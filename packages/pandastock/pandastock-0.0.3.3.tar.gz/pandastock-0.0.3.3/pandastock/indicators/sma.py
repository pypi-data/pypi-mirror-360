from collections import deque

import numpy as np
import pandas as pd

from matplotlib.axes import Axes

from pandastock.indicators.base import Indicator, PlotPosition


class SMA(Indicator):

    plot_position = PlotPosition.over

    def __init__(self, window: int = 15, col: str = 'close'):
        self.window = window
        self.col = col

        # Для потоковой обработки
        self._buffer = deque(maxlen=window)

    def next_value(self, candle: pd.Series) -> pd.Series:
        price = candle[self.col]

        self._buffer.append(price)

        if len(self._buffer) < self.window:
            return pd.Series({'sma': np.nan})

        sma_value = sum(self._buffer) / self.window

        return pd.Series({'sma': sma_value})

    def build(self, data: pd.DataFrame) -> pd.DataFrame:
        self._buffer.clear()

        return (
            data[self.col]
            .rolling(window=self.window, min_periods=self.window)
            .mean()
            .to_frame('sma')
        )

    def plot(self, data: pd.DataFrame, axes: Axes) -> None:
        axes.plot(
            range(len(data['sma'])),
            data,
            color='lightsteelblue',
            alpha=0.6,
            linewidth=2,
            label='SMA',
        )
        axes.legend()

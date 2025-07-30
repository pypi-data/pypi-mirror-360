import numpy as np
import pandas as pd

from matplotlib.axes import Axes

from .base import Indicator, PlotPosition


class MACD(Indicator):

    plot_position = PlotPosition.under

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9, col: str = 'close'):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.col = col
        self._fast_ema = None
        self._slow_ema = None
        self._signal_ema = None
        self._macd_line = None

    def _update_ema(self, value: float, current_ema: float | None, window: int) -> float:
        if current_ema is None:
            return value
        alpha = 2 / (window + 1)
        return value * alpha + current_ema * (1 - alpha)

    def next_value(self, candle: pd.Series) -> pd.Series:
        value = candle[self.col]

        # Update EMAs
        self._fast_ema = self._update_ema(value, self._fast_ema, self.fast)
        self._slow_ema = self._update_ema(value, self._slow_ema, self.slow)

        if self._fast_ema is None or self._slow_ema is None:
            return pd.Series({
                'macd': np.nan,
                'signal': np.nan,
                'histogram': np.nan,
            })

        # Calculate MACD line
        self._macd_line = self._fast_ema - self._slow_ema

        # Update signal line
        self._signal_ema = self._update_ema(self._macd_line, self._signal_ema, self.signal)

        if self._signal_ema is None:
            return pd.Series({
                'macd': self._macd_line,
                'signal': np.nan,
                'histogram': np.nan,
            })

        return pd.Series({
            'macd': self._macd_line,
            'signal': self._signal_ema,
            'histogram': self._macd_line - self._signal_ema,
        })

    def build(self, data: pd.DataFrame) -> pd.DataFrame:
        result = []
        for _, row in data.iterrows():
            result.append(self.next_value(row))
        df = pd.concat(result, axis=1).T
        df.index = data.index
        return df

    def plot(self, data: pd.DataFrame, axes: Axes) -> None:
        axes.plot(
            range(len(data['macd'])),
            data['macd'],
            color='blue',
            alpha=0.8,
            linewidth=1,
            label='MACD',
        )
        axes.plot(
            range(len(data['signal'])),
            data['signal'],
            color='orange',
            alpha=0.8,
            linewidth=1,
            label='Signal',
        )
        axes.bar(
            range(len(data['histogram'])),
            data['histogram'],
            color=np.where(data['histogram'] >= 0, 'green', 'red'),
            alpha=0.3,
            width=0.8,
            label='Histogram',
        )
        axes.legend()

import numpy as np
import pandas as pd

from matplotlib.axes import Axes

from .base import Indicator, PlotPosition


class LSMA(Indicator):

    plot_position = PlotPosition.over

    def __init__(self, window: int = 15, col: str = 'close'):
        self.window = window
        self.col = col

        self.window = window
        self._values = []
        self._idx = np.arange(window)

    def next_value(self, candle: pd.Series) -> pd.Series:
        value = candle[self.col]

        self._values.append(value)

        if len(self._values) < self.window:
            return pd.Series({'lsma': np.nan})

        # Keep only the most recent window values
        window_values = self._values[-self.window:]

        # Calculate linear regression with proper type handling
        window_arr = np.asarray(window_values, dtype=np.float64)
        A = np.vstack([self._idx, np.ones(self.window)]).T.astype(np.float64)
        a, b = np.linalg.lstsq(A, window_arr, rcond=None)[0]

        # Return predicted value at end of window
        return pd.Series({'lsma': a * (self.window - 1) + b})

    def build(self, data: pd.DataFrame) -> pd.DataFrame:
        result = []
        for _, row in data.iterrows():
            result.append(self.next_value(row))
        df = pd.concat(result, axis=1).T
        df.index = data.index
        return df

    def plot(self, data: pd.DataFrame, axes: Axes) -> None:
        axes.plot(
            range(len(data['lsma'])),
            data,
            color='lightsteelblue',
            alpha=0.6,
            linewidth=2,
            label='LSMA',
        )
        axes.legend()

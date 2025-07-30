import numpy as np
import pandas as pd

from matplotlib.axes import Axes

from pandastock.indicators.base import Indicator, PlotPosition


class RSI(Indicator):

    plot_position = PlotPosition.under

    def __init__(
        self,
        period: int = 14,
        col: str = 'close',
    ):
        self.period = period
        self.col = col

        self._prev_value = None
        self._prev_gains = []
        self._prev_losses = []
        self._first_full_calculation = False

    def _process_row(self, candle: pd.Series) -> float:
        current_value = candle[self.col]

        if self._prev_value is None:
            self._prev_value = current_value
            return np.nan

        delta = current_value - self._prev_value
        self._prev_value = current_value

        gain = max(delta, 0)
        loss = max(-delta, 0)

        self._prev_gains.append(gain)
        self._prev_losses.append(loss)

        if len(self._prev_gains) > self.period:
            self._prev_gains.pop(0)
            self._prev_losses.pop(0)

        if len(self._prev_gains) < self.period:
            return np.nan

        if not self._first_full_calculation:
            avg_gain = sum(self._prev_gains) / self.period
            avg_loss = sum(self._prev_losses) / self.period
            self._first_full_calculation = True
        else:
            prev_avg_gain = (
                sum(self._prev_gains[:-1]) / (self.period - 1)
                if len(self._prev_gains) > 1
                else 0
            )
            prev_avg_loss = (
                sum(self._prev_losses[:-1]) / (self.period - 1)
                if len(self._prev_losses) > 1
                else 0
            )

            alpha = 1 / self.period
            avg_gain = gain * alpha + prev_avg_gain * (1 - alpha)
            avg_loss = loss * alpha + prev_avg_loss * (1 - alpha)

        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        return np.round(rsi, 2)

    def next_value(self, candle: pd.Series) -> pd.Series:
        rsi_value = self._process_row(candle)
        return pd.Series({'rsi': rsi_value})

    def build(self, data: pd.DataFrame, name: str = 'rsi') -> pd.DataFrame:
        self._reset_state()

        delta = data[self.col].diff()

        up = delta.copy()
        up[up < 0] = 0  # type: ignore
        up = pd.Series.ewm(up, alpha=1 / self.period).mean()

        down = delta.copy()
        down[down > 0] = 0  # type: ignore
        down *= -1
        down = pd.Series.ewm(down, alpha=1 / self.period).mean()

        rsi = np.where(up == 0, 0, np.where(down == 0, 100, 100 - (100 / (1 + up / down))))

        result = pd.Series(np.round(rsi, 2))
        result.index = data.index

        return result.to_frame('rsi')

    def _reset_state(self):
        self._prev_value = None
        self._prev_gains = []
        self._prev_losses = []
        self._first_full_calculation = False

    @property
    def name(self) -> str:
        return f'RSI {self.period}'

    def plot(self, data: pd.DataFrame, axes: Axes) -> None:
        axes.plot(
            range(len(data['rsi'])),
            data['rsi'],
            label=self.name,
            color='purple',
        )

        axes.axhline(y=100, color='white')
        axes.axhline(y=0, color='white')

        axes.set_ylabel(self.name)
        axes.legend()

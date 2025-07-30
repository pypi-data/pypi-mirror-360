import numpy as np
import pandas as pd

from matplotlib.axes import Axes

from pandastock.indicators.base import Indicator, PlotPosition
from pandastock.indicators.rsi import RSI


class StochasticRSI(Indicator):

    plot_position = PlotPosition.under

    def __init__(self, period: int = 14, k: int = 3, d: int = 3, col: str = 'close'):
        self.period = period
        self.k = k
        self.d = d
        self.col = col

        # Для потоковой обработки
        self.rsi_indicator = RSI(period=period, col=col)
        self._rsi_values = []
        self._k_values = []

    def next_value(self, candle: pd.Series) -> pd.Series:
        """Обрабатывает новую свечу и возвращает текущее значение Stochastic RSI."""
        # Получаем текущее значение RSI
        rsi_value = self.rsi_indicator.next_value(candle)['rsi']

        # Если RSI еще не рассчитан, возвращаем NaN
        if np.isnan(rsi_value):
            return pd.Series({'stoch_rsi': np.nan})

        # Добавляем RSI в историю
        self._rsi_values.append(rsi_value)

        # Если у нас недостаточно RSI значений, возвращаем NaN
        if len(self._rsi_values) < self.period:
            return pd.Series({'stoch_rsi': np.nan})

        # Оставляем только последние period значений
        if len(self._rsi_values) > self.period:
            self._rsi_values = self._rsi_values[-self.period:]

        # Вычисляем Stochastic RSI
        min_rsi = min(self._rsi_values)
        max_rsi = max(self._rsi_values)

        # Проверка деления на ноль
        if max_rsi == min_rsi:
            stoch_rsi = 100  # Если все значения равны, считаем, что StochRSI = 100
        else:
            stoch_rsi = 100 * (rsi_value - min_rsi) / (max_rsi - min_rsi)

        # Добавляем в историю значений K
        self._k_values.append(stoch_rsi)

        # Если у нас недостаточно K значений, возвращаем NaN
        if len(self._k_values) < self.k:
            return pd.Series({'stoch_rsi': np.nan})

        # Оставляем только последние k значений для K
        if len(self._k_values) > self.k:
            self._k_values = self._k_values[-self.k:]

        # Вычисляем K (среднее за k периодов)
        k_value = sum(self._k_values) / self.k

        # Добавляем K в историю для D
        if not hasattr(self, '_d_values'):
            self._d_values = []
        self._d_values.append(k_value)

        # Если у нас недостаточно D значений, возвращаем NaN
        if len(self._d_values) < self.d:
            return pd.Series({'stoch_rsi': np.nan})

        # Оставляем только последние d значений для D
        if len(self._d_values) > self.d:
            self._d_values = self._d_values[-self.d:]

        # Вычисляем D (среднее за d периодов)
        d_value = sum(self._d_values) / self.d

        return pd.Series({'stoch_rsi': d_value})

    def build(self, data: pd.DataFrame) -> pd.DataFrame:
        """Векторизованная версия для исторических данных."""
        # Сбрасываем состояние
        self._rsi_values = []
        self._k_values = []
        if hasattr(self, '_d_values'):
            self._d_values = []

        # Используем векторизованный подход для исторических данных
        rsi = RSI(self.period).build(data)
        stochastic_rsi = (
            100
            * (rsi - rsi.rolling(self.period).min())
            / (rsi.rolling(self.period).max() - rsi.rolling(self.period).min())
        )

        k_values = stochastic_rsi.rolling(self.k).mean()
        result = pd.Series(k_values.rolling(self.d).mean()['rsi'])
        result.index = data.index

        return result.to_frame('stoch_rsi')

    @property
    def name(self) -> str:
        return f'StochRSI {self.d} {self.k}'

    def plot(self, data: pd.DataFrame, axes: Axes) -> None:
        axes.plot(
            range(len(data['stoch_rsi'])),
            data['stoch_rsi'],
            label=self.name,
            color='blue',
        )

        axes.axhline(y=100, color='white')
        axes.axhline(y=0, color='white')
        axes.axhline(y=80, color='gray', linestyle='--', linewidth=0.9)
        axes.axhline(y=20, color='gray', linestyle='--', linewidth=0.9)

        axes.set_ylabel(self.name)
        axes.legend()

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import auto, StrEnum

import pandas as pd

from matplotlib.axes import Axes


class PlotPosition(StrEnum):
    over = auto()
    under = auto()


@dataclass
class PlotStyle:
    color: str
    position: PlotPosition
    levels: tuple[float] | None = None
    minmax: tuple[float, float] | None = None


class Indicator(ABC):

    plot_position: PlotPosition = NotImplemented

    def __init__(self):
        pass

    @abstractmethod
    def build(self, data: pd.DataFrame) -> pd.DataFrame:
        ...

    @abstractmethod
    def next_value(self, candle: pd.Series) -> pd.Series:
        ...

    @abstractmethod
    def plot(self, data: pd.DataFrame, axes: Axes):
        ...

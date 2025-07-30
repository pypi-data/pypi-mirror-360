from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pandastock.trades.accessor import TradesAccessor


class TradesDataFrame(pd.DataFrame):

    candles: 'TradesAccessor'

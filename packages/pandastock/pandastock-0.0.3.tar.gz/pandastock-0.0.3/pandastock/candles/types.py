import pandas as pd


from pandastock.candles.accessor import CandlesAccessor


class CandlesDataFrame(pd.DataFrame):

    candles: CandlesAccessor

import os

import pandas as pd

from pandastock.candles.types import CandlesDataFrame


def _prepare_dataframe(
    df: pd.DataFrame,
    agg: str | None = None,
    remove_weekend: bool = False,
) -> CandlesDataFrame:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if remove_weekend:
        df = df[
            df['timestamp']
            .apply(lambda x: (x.weekday() < 5))
        ]
    df.set_index('timestamp', inplace=True)

    if agg:
        return (  # type: ignore
            df
            .resample(agg)
            .agg(
                {
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum',
                },
            )
            .dropna()
        )
    return df.dropna()  # type: ignore


def read_candles_from_csv(
    path: str,
    agg: str | None = None,
    remove_weekend: bool = False,
) -> CandlesDataFrame:
    df = pd.read_csv(path)
    return _prepare_dataframe(df, agg, remove_weekend)


def read_candles_from_csv_list(
    path_list: list[str],
    agg: str | None = None,
    remove_weekend: bool = False,
) -> CandlesDataFrame:
    df_list = [pd.read_csv(path) for path in path_list]
    return _prepare_dataframe(pd.concat(df_list), agg, remove_weekend)


def read_candles_csv_range(
    dir: str,
    from_: str | None = None,
    to_: str | None = None,
    agg: str | None = None,
    remove_weekend: bool = False,
    extension: str = 'csv',
) -> CandlesDataFrame:
    if dir[-1] == '/':
        dir = dir[:-1]

    files = os.listdir(dir)
    from_ = from_ or min(files)
    to_ = to_ or max(files)

    return read_candles_from_csv_list(
        [f'{dir}/{f}' for f in files if (from_ <= f.split(f'.{extension}')[0] <= to_)],
        agg,
        remove_weekend,
    )

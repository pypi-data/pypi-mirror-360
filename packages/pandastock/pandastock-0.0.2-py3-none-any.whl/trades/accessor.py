import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pandastock.trades.types import TradesDataFrame


@pd.api.extensions.register_dataframe_accessor('trades')
class TradesAccessor:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)

        pandas_obj['timestamp_in'] = pd.to_datetime(pandas_obj['timestamp_in'])
        pandas_obj['timestamp_out'] = pd.to_datetime(pandas_obj['timestamp_out'])

        self._obj = pandas_obj

        if 'profit' not in pandas_obj.columns:
            self._add_profit_columns()

    def _validate(self, pandas_obj):
        required_columns = ['timestamp_in', 'timestamp_out', 'direction', 'price_in', 'price_out']
        if not all(col in pandas_obj.columns for col in required_columns):
            raise AttributeError(
                'DataFrame must have columns: {}'.format(', '.join(required_columns)),
            )

    def _add_profit_columns(self):
        self._obj['profit'] = self._obj.apply(
            lambda row: (
                row['price_out'] - row['price_in']
                if row['direction'] == 'long'
                else row['price_in'] - row['price_out']
            ),
            axis=1,
        )
        self._obj['profit_percent'] = self._obj['profit'] / self._obj['price_in'] * 100
        self._obj['duration'] = self._obj['timestamp_out'] - self._obj['timestamp_in']

    @classmethod
    def from_list_of_dicts(cls, trades: list[dict]) -> TradesDataFrame:
        return pd.DataFrame(  # type: ignore
            data={
                'direction': [trade['direction'] for trade in trades],
                'timestamp_in': [trade['timestamp_in'] for trade in trades],
                'price_in': [trade['price_in'] for trade in trades],
                'timestamp_out': [trade['timestamp_out'] for trade in trades],
                'price_out': [trade['price_out'] for trade in trades],
            },
        )

    def print_stats(self) -> None:
        p = self._obj.copy()

        total_duration = p['timestamp_out'].iloc[-1] - p['timestamp_in'].iloc[0]
        total_profit = p['profit'].sum()
        total_trades = len(p)
        profit_trades_count = len(p[p['profit'] > 0])
        loss_trades_count = len(p[p['profit'] < 0])

        p.set_index('timestamp_out', inplace=True)
        expected_daily_profit = p['profit'].resample('1d').sum().mean()

        print(f'Total profit: {total_profit:.2f}')
        print(f'Total duration: {total_duration}')
        print(f'Total trades: {total_trades}')
        print(f'Profit / loss trades: {profit_trades_count} / {loss_trades_count}')
        print(f'Success rate: {profit_trades_count / total_trades * 100:.2f}%')
        print(f'Expected daily profit: {expected_daily_profit:.2f}')

    def plot_profit_by_time(
        self,
        agg_interval: str = '1d',
        from_: pd.Timestamp | str | None = None,
        to_: pd.Timestamp | str | None = None,
    ) -> None:
        p = self._obj.copy()
        p.set_index('timestamp_out', inplace=True)
        p = p.loc[from_:to_]
        agg = p['profit'].resample(agg_interval).sum()

        colors = np.where(agg >= 0, 'green', 'red')
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.bar(agg.index.astype(str), agg.values, color=colors, width=0.8, edgecolor='black')

        ax.set_title(f'Aggregated PnL by {agg_interval}')
        ax.set_ylabel('Profit')
        ax.set_xlabel('Interval')
        ax.axhline(y=0, color='black', linewidth=1)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

import pandas as pd

from pandastock.indicators import LSMA, MACD, RSI, SMA, StochasticRSI


TEST_DATAFRAME = pd.DataFrame(
    data={
        'open': [
            4081.5,
            4081.0,
            4072.0,
            4074.0,
            4072.0,
            4071.5,
            4072.0,
            4063.0,
            4056.5,
            4062.0,
            4064.0,
            4055.0,
            4057.5,
            4052.5,
            4040.0,
            4051.5,
            4044.5,
            4055.0,
            4043.5,
            4055.0,
        ],
        'close': [
            4081.5,
            4071.0,
            4074.0,
            4072.5,
            4074.5,
            4071.5,
            4063.0,
            4055.0,
            4061.5,
            4064.0,
            4056.0,
            4057.0,
            4052.5,
            4040.0,
            4051.5,
            4045.0,
            4054.5,
            4043.5,
            4055.0,
            4048.0,
        ],
        'low': [
            4081.5,
            4065.0,
            4069.0,
            4069.5,
            4071.0,
            4071.5,
            4063.0,
            4050.0,
            4050.5,
            4060.0,
            4055.0,
            4053.0,
            4052.5,
            4035.5,
            4039.5,
            4039.5,
            4044.5,
            4035.5,
            4043.0,
            4042.5,
        ],
        'high': [
            4081.5,
            4089.5,
            4078.5,
            4076.5,
            4074.5,
            4074.0,
            4074.5,
            4064.5,
            4061.5,
            4070.0,
            4071.5,
            4059.5,
            4058.0,
            4055.5,
            4058.5,
            4051.5,
            4058.0,
            4060.0,
            4060.0,
            4059.0,
        ],
    },
    index=pd.DatetimeIndex(
        [
            pd.Timestamp('2025-02-03 03:45:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 04:00:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 04:15:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 04:30:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 04:45:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 05:00:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 05:15:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 05:30:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 05:45:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 06:00:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 06:15:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 06:30:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 06:45:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 07:00:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 07:15:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 07:30:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 07:45:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 08:00:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 08:15:00+0000', tz='UTC'),
            pd.Timestamp('2025-02-03 08:30:00+0000', tz='UTC'),
        ],
    ),
)


def test_lsma():
    lsma = LSMA(window=5)
    expected_values = [
        'nan',
        'nan',
        'nan',
        'nan',
        '4072.20',
        '4073.00',
        '4066.50',
        '4058.00',
        '4056.60',
        '4059.70',
        '4058.90',
        '4058.40',
        '4053.20',
        '4043.60',
        '4046.20',
        '4044.20',
        '4050.50',
        '4048.90',
        '4051.00',
        '4050.50',
    ]
    actual_result = lsma.build(TEST_DATAFRAME)

    for expected, actual in zip(expected_values, actual_result['lsma']):
        assert expected == f'{actual:.2f}'


def test_rsi():
    rsi = RSI(period=5)
    expected_values = [
        'nan',
        '0.00',
        '26.32',
        '22.60',
        '37.35',
        '27.52',
        '14.24',
        '9.08',
        '33.53',
        '41.14',
        '28.22',
        '31.58',
        '25.00',
        '14.51',
        '42.34',
        '34.42',
        '51.12',
        '37.35',
        '53.66',
        '44.79',
    ]
    actual_result = rsi.build(TEST_DATAFRAME)

    for expected, actual in zip(expected_values, actual_result['rsi']):
        assert expected == f'{actual:.2f}'


def test_stoch_rsi():
    stoch_rsi = StochasticRSI(period=5, k=3, d=3)
    expected_values = [
        'nan',
        'nan',
        'nan',
        'nan',
        'nan',
        'nan',
        'nan',
        'nan',
        'nan',
        '38.52',
        '57.68',
        '73.62',
        '67.33',
        '47.77',
        '33.34',
        '37.97',
        '60.34',
        '75.22',
        '85.32',
        '79.18',
    ]

    actual_result = stoch_rsi.build(TEST_DATAFRAME)

    for expected, actual in zip(expected_values, actual_result['stoch_rsi']):
        assert expected == f'{actual:.2f}'


def test_sma():
    sma = SMA(window=5)
    expected_values = [
        'nan',
        'nan',
        'nan',
        'nan',
        '4074.70',
        '4072.70',
        '4071.10',
        '4067.30',
        '4065.10',
        '4063.00',
        '4059.90',
        '4058.70',
        '4058.20',
        '4053.90',
        '4051.40',
        '4049.20',
        '4048.70',
        '4046.90',
        '4049.90',
        '4049.20',
    ]

    actual_result = sma.build(TEST_DATAFRAME)

    for expected, actual in zip(expected_values, actual_result['sma']):
        assert expected == f'{actual:.2f}'


def test_macd():
    macd = MACD(fast=5, slow=10, signal=3)
    expected_values = [
        ('0.00', '0.00', '0.00'),
        ('-1.59', '-0.80', '-0.80'),
        ('-1.91', '-1.35', '-0.56'),
        ('-2.19', '-1.77', '-0.42'),
        ('-1.91', '-1.84', '-0.07'),
        ('-2.10', '-1.97', '-0.13'),
        ('-3.36', '-2.66', '-0.69'),
        ('-5.06', '-3.86', '-1.20'),
        ('-4.69', '-4.28', '-0.42'),
        ('-3.83', '-4.05', '0.22'),
        ('-4.34', '-4.19', '-0.14'),
        ('-4.20', '-4.20', '-0.00'),
        ('-4.55', '-4.38', '-0.18'),
        ('-6.36', '-5.37', '-0.99'),
        ('-5.22', '-5.30', '0.07'),
        ('-5.27', '-5.28', '0.01'),
        ('-3.54', '-4.41', '0.87'),
        ('-4.04', '-4.23', '0.18'),
        ('-2.33', '-3.28', '0.95'),
        ('-2.32', '-2.80', '0.48'),
    ]

    actual_result = macd.build(TEST_DATAFRAME)

    for expected, actual in zip(
        expected_values,
        actual_result[['macd', 'signal', 'histogram']].values,
    ):
        assert expected == tuple(f'{value:.2f}' for value in actual)

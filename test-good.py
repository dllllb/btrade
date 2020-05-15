import datetime

from baselines import test_strategies, buy_and_hold_strategy, simple_buy_sell_strategy, random_strategy

import backtrader as bt

import pandas_datareader as pdr

import requests_cache
session = requests_cache.CachedSession(cache_name='stocks-cache', backend='sqlite')

nvda_df = pdr.DataReader("NVDA", start='1999-01-22', end='2020-05-01', data_source='yahoo', session=session)
btc_df = pdr.DataReader("BTC-USD", start='2010-07-16', end='2020-05-01', data_source='yahoo', session=session)

test_strategies(
    {
        buy_and_hold_strategy,
        simple_buy_sell_strategy,
        random_strategy
    },
    {
        'NVDA': nvda_df,
        'BTC-USD': btc_df
    },
    from_date=datetime.datetime(2014, 1, 1),
    to_date=datetime.datetime(2019, 5, 1),
    n_steps=50,
    step_size=1,
)

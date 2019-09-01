import datetime
import pandas as pd

from baselines import buy_and_hold_strategy, strategy_quality, simple_buy_sell_strategy, random_strategy

pd.options.display.float_format = '{:,.2f}'.format

cerebro = buy_and_hold_strategy()

stat = strategy_quality(
    cerebro,
    'NVDA.csv',
    from_date=datetime.datetime(2014, 1, 1),
    to_date=datetime.datetime(2019, 5, 1),
    steps=50,
    step_size=10).rename('buy_and_hold')

print(stat.describe())

cerebro = simple_buy_sell_strategy()

stat = strategy_quality(
    cerebro,
    'NVDA.csv',
    from_date=datetime.datetime(2014, 1, 1),
    to_date=datetime.datetime(2019, 5, 1),
    steps=50,
    step_size=10).rename('simple_buy_sell')

print(stat.describe())

cerebro = random_strategy()

stat = strategy_quality(
    cerebro,
    'NVDA.csv',
    from_date=datetime.datetime(2014, 1, 1),
    to_date=datetime.datetime(2019, 5, 1),
    steps=50,
    step_size=10).rename('random')

print(stat.describe())

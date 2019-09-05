import datetime

from baselines import test_strategies, buy_and_hold_strategy, simple_buy_sell_strategy, random_strategy, YahooDS

test_strategies(
    {
        buy_and_hold_strategy,
        simple_buy_sell_strategy,
        random_strategy
    },
    {'NVDA': YahooDS('NVDA.csv'), 'BTC-USD': YahooDS('BTC-USD.csv')},
    from_date=datetime.datetime(2014, 1, 1),
    to_date=datetime.datetime(2019, 5, 1),
    n_steps=50,
    step_size=1,
)

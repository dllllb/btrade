import datetime

from baselines import test_strategies, buy_and_hold_strategy, simple_buy_sell_strategy, random_strategy, FinamDS

test_strategies(
    {
        buy_and_hold_strategy,
        simple_buy_sell_strategy,
        random_strategy
    },
    {
        'FXDE': FinamDS('FXDE_100101_190816.csv'),
        'FXGD': FinamDS('FXGD_100101_190816.csv'),
        'FXIT': FinamDS('FXIT_100101_190816.csv'),
        'FXMM': FinamDS('FXMM_100101_190816.csv')
    },
    from_date=datetime.datetime(2014, 1, 1),
    to_date=datetime.datetime(2019, 5, 1),
    n_steps=50,
    step_size=1,
)

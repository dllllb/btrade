import datetime

from baselines import test_strategies, buy_and_hold_strategy, simple_buy_sell_strategy, random_strategy, FinamDS

test_strategies(
    {
        buy_and_hold_strategy,
        simple_buy_sell_strategy,
        random_strategy
    },
    {
        'FXDE': FinamDS('data/FXDE.finam.csv'),
        'FXGD': FinamDS('data/FXGD.finam.csv'),
        'FXIT': FinamDS('data/FXIT.finam.csv'),
        'FXMM': FinamDS('data/FXMM.finam.csv')
    },
    from_date=datetime.datetime(2014, 1, 1),
    to_date=datetime.datetime(2019, 5, 1),
    n_steps=50,
    step_size=1,
)

import pandas as pd
import numpy as np
from bt_strategy import evaluate_strategies, buy_and_hold_strategy, random_strategy

def random_ticker(date_from, date_to):
    dates = pd.date_range(date_from, date_to)
    close = pd.Series(np.random.randint(0, 100, len(dates)), index=dates)
    res = pd.DataFrame({'close': close})
    return res

def test_evaluate_strategies():
    nvda = random_ticker('1999-01-22', '2000-01-22')
    btc = random_ticker('2010-07-16', '2011-07-16')
    
    res = evaluate_strategies(
        {
            buy_and_hold_strategy,
            random_strategy
        },
        {
            'NVDA': nvda,
            'BTC-USD': btc
        },
        n_trials=1
    )

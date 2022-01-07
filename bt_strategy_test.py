import pandas as pd
import numpy as np
from bt_strategy import evaluate_strategies, buy_and_hold_strategy, random_strategy

def random_ticker(date_from, date_to):
    dates = pd.date_range(date_from, date_to)

    res = pd.DataFrame(
        data={
            'close': np.arange(1, len(dates)+1),
            'open': np.arange(0, len(dates)),
        },
        index=dates)
    return res

def test_evaluate_strategies():
    nvda = random_ticker('1999-01-22', '2000-01-22')
    btc = random_ticker('2010-07-16', '2011-07-16')
    
    stats = evaluate_strategies(
        {
            buy_and_hold_strategy,
            random_strategy
        },
        {
            'NVDA': nvda,
            'BTC-USD': btc
        },
        n_trials=2,
        n_jobs=1
    )

    stats.groupby('strategy').value.mean()
    stats.groupby('strategy').dropdown.max()

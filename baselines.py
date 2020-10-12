import datetime
import random
import pandas as pd
import backtrader as bt
from tqdm import tqdm
from typing import Dict, List, Callable

def strategy_quality(
    cer: bt.Cerebro,
    data_source: pd.DataFrame,
    from_date: str,
    to_date: str,
    steps: int,
    step_size: int
):
    from_date = datetime.datetime.fromisoformat(from_date)
    to_date = datetime.datetime.fromisoformat(to_date)

    from copy import deepcopy
    vals = []
    first_start_date = to_date - datetime.timedelta(days=steps*step_size)
    cash = 100000.0
    for s in tqdm(range(steps)):
        c = deepcopy(cer)
        c.broker.setcash(cash)

        start = from_date + datetime.timedelta(days=s*step_size)
        end = first_start_date + datetime.timedelta(days=s*step_size)
        data = bt.feeds.PandasData(dataname=data_source.loc[start: end])
        c.adddata(data)
        
        c.run()
        val = c.broker.get_value()
        vals.append(val)
        norm_vals = pd.Series(vals)/cash
    return norm_vals


def buy_and_hold_strategy():
    cerebro = bt.Cerebro()
    cerebro.add_signal(bt.SIGNAL_LONG, bt.indicators.AllN)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro


class CloseVsSmaSignal(bt.Indicator):
    lines = ('signal',)

    params = (
        ('window', 30),
        ('gap', .1),
        ('mdir', 'down')
    )

    def __init__(self):
        sma = bt.indicators.SMA(period=self.p.window)
        min_gap_val = sma*self.p.gap
        gap = self.data - sma

        if self.p.mdir == 'down':
            self.lines.signal = gap < -min_gap_val
        elif self.p.mdir == 'up':
            self.lines.signal = -(gap > min_gap_val)


def simple_buy_sell_strategy():
    cerebro = bt.Cerebro()

    cerebro.add_signal(bt.SIGNAL_LONG, CloseVsSmaSignal, window=15, mdir='down', gap=.05)
    cerebro.add_signal(bt.SIGNAL_LONGEXIT, CloseVsSmaSignal, window=60, mdir='up', gap=.05)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro


class PrevPeakStrategy(bt.Strategy):
    params = (
        ('window', 90),
        ('max_thresold', .9),
        ('min_thresold', 1.1),
    )

    def __init__(self):
        self.acquired = False
        self.win_max = bt.indicators.Highest(period=self.p.window)
        self.win_min = bt.indicators.Lowest(period=self.p.window)


    def next(self):
        max_percents = (self.data - self.win_max)/self.win_max
        min_percents = (self.data - self.win_min)/self.win_min

        if max_percents > self.p.max_thresold and self.acquired:
            self.close()
            self.acquired = False
        elif min_percents < self.p.min_thresold and not self.acquired:
            self.buy()
            self.acquired = True


class RandomStrategy(bt.Strategy):
    params = (
        ('prob', .1),
    )

    def __init__(self):
        self.acquired = False

    def next(self):
        if not self.acquired:
            if random.random() < self.p.prob:
                self.buy()
                self.acquired = True
        else:
            if random.random() < self.p.prob:
                self.close()
                self.acquired = False


def random_strategy():
    cerebro = bt.Cerebro()

    cerebro.addstrategy(RandomStrategy)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro


def test_strategies(
    strategies: List[Callable[[], bt.Cerebro]],
    logs: Dict[str, pd.DataFrame],
    from_date: str,
    to_date: str,
    n_steps: int,
    step_size: int
):
    res = []
    for strategy in strategies:
        stats = [
            strategy_quality(
                strategy(),
                log,
                from_date=from_date,
                to_date=to_date,
                steps=n_steps,
                step_size=step_size).rename(f'{strategy.__name__}-{log_name}')
            for log_name, log in logs.items()]
        stat_df = pd.concat(stats, axis=1)
        res.append(stat_df)

    for stat in res:
        print(stat.describe())
    print(pd.concat(s.mean() for s in res))
    strategy_names = [s.__name__ for s in strategies]
    print(pd.Series([s.mean().mean() for s in res], index=strategy_names))

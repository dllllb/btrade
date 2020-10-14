import datetime
import random
import pandas as pd
import numpy as np
import backtrader as bt
from tqdm import tqdm
from typing import Dict, List, Callable

def strategy_quality(
    cer: Callable[[], bt.Cerebro],
    data_source: pd.DataFrame,
    n_trials: int
):
    from_date = data_source.index.min()
    to_date = data_source.index.max()
    days = (to_date - from_date).days

    vals = []
    cash = 100000.0
    for _ in tqdm(range(n_trials)):
        c = cer()
        c.broker.setcash(cash)

        interval_len = np.random.randint(150, days-30)
        start_day = np.random.randint(0, days - interval_len)

        start = from_date + datetime.timedelta(days=start_day)
        end = start + datetime.timedelta(days=interval_len)
        data = bt.feeds.PandasData(dataname=data_source.loc[start: end])
        c.adddata(data)
        
        c.run()
        val = c.broker.get_value()
        vals.append(val)

    norm_vals = pd.Series(vals)/cash
    return norm_vals


def evaluate_strategies(
    strategies: List[Callable[[], bt.Cerebro]],
    logs: Dict[str, pd.DataFrame],
    n_trials: int
):
    res = []
    for strategy in strategies:
        stats = []
        for log_name, log in logs.items():
            stat = strategy_quality(strategy, log, n_trials).rename(f'{log_name}')
            stats.append(stat)
        stat_df = pd.concat(stats, axis=1)
        stat_df['strategy'] = strategy.__name__
        res.append(stat_df)

    res_df = pd.concat(res, axis=0)
    return res_df


def buy_and_hold_strategy():
    cerebro = bt.Cerebro()
    cerebro.add_signal(bt.SIGNAL_LONG, bt.indicators.AllN)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro


class CloseVsSma(bt.Indicator):
    lines = ('signal',)

    params = (
        ('window', 30),
        ('gap', .1),
        ('mdir', 'down')
    )

    def __init__(self):
        self.sma = bt.indicators.SMA(period=self.p.window)

    def next(self):
        sma_share = self.data/self.sma
        if sma_share < 1-self.p.gap:
            self.lines.signal[0] = 1
        elif sma_share > 1+self.p.gap:
            self.lines.signal[0] = -1
        else:
            self.lines.signal[0] = 0


def close_vs_sma_strategy():
    cerebro = bt.Cerebro()

    cerebro.add_signal(bt.SIGNAL_LONG, CloseVsSma, window=15, gap=.05)
    cerebro.add_signal(bt.SIGNAL_LONGEXIT, CloseVsSma, window=60, gap=.05)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro


class MeanReversion(bt.Indicator):
    lines = ('signal',)

    params = (
        ('window_small', 30),
        ('window_large', 90),
    )

    def __init__(self):
        self.sma = bt.indicators.SMA(period=self.p.window_small)
        self.lma = bt.indicators.SMA(period=self.p.window_large)

    def next(self):
        if self.sma < self.lma:
            self.lines.signal[0] = 1
        elif self.sma > self.lma:
            self.lines.signal[0] = -1


def mean_reversion_strategy():
    cerebro = bt.Cerebro()

    cerebro.add_signal(bt.SIGNAL_LONG, MeanReversion)
    cerebro.add_signal(bt.SIGNAL_LONGEXIT, MeanReversion)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro


class PrevPeak(bt.Indicator):
    lines = ('signal',)

    params = (
        ('window', 90),
        ('max_thresold', .9),
        ('min_thresold', 1.1),
    )

    def __init__(self):
        self.win_max = bt.indicators.Highest(period=self.p.window)
        self.win_min = bt.indicators.Lowest(period=self.p.window)

    def next(self):
        max_percents = self.data/self.win_max
        min_percents = self.data/self.win_min

        if max_percents > self.p.max_thresold:
            self.lines.signal[0] = -1
        elif min_percents < self.p.min_thresold:
            self.lines.signal[0] = 1


def prev_peak_strategy():
    cerebro = bt.Cerebro()

    cerebro.add_signal(bt.SIGNAL_LONG, PrevPeak)
    cerebro.add_signal(bt.SIGNAL_LONGEXIT, PrevPeak)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro


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

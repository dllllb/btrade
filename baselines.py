import datetime
import random
import pandas as pd
import backtrader as bt
from tqdm import tqdm


class FinamCSV(bt.feeds.GenericCSVData):
    params = (
        ('headers', True),
        ('separator', '\t'),
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y%m%d'),

        ('datetime', 2),
        ('open', 4),
        ('high', 5),
        ('low', 6),
        ('close', 7),
        ('volume', 8),
    )


class FinamDS:
    def __init__(self, path):
        self.path = path

    def __call__(self, from_date, to_date):
        return FinamCSV(
            dataname=self.path,
            fromdate=from_date,
            todate=to_date)


class YahooDS:
    def __init__(self, path):
        self.path = path

    def __call__(self, from_date, to_date):
        return bt.feeds.YahooFinanceCSVData(
            dataname=self.path,
            fromdate=from_date,
            todate=to_date,
            reverse=False)


def strategy_quality(cer, data_source, from_date, to_date, steps, step_size):
    from copy import deepcopy
    vals = []
    first_start_date = to_date - datetime.timedelta(days=steps*step_size)
    cash = 100000.0
    for s in tqdm(range(steps)):
        c = deepcopy(cer)
        c.broker.setcash(cash)

        start = from_date + datetime.timedelta(days=s*step_size)
        end = first_start_date + datetime.timedelta(days=s*step_size)
        ds_slice = data_source[(data_source.index > start) & (data_source.index < end)]
        data = bt.feeds.PandasData(dataname=ds_slice)
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


def test_strategies(strategies, logs, from_date, to_date, n_steps, step_size):
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

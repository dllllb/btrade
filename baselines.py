import datetime
import random
import pandas as pd
import backtrader as bt


def strategy_quality(cer, data_file, from_date, to_date, steps, step_size):
    from copy import deepcopy
    vals = []
    first_start_date = to_date - datetime.timedelta(days=steps*step_size)
    cash = 100000.0
    for s in range(steps):
        c = deepcopy(cer)
        c.broker.setcash(cash)
        data = bt.feeds.YahooFinanceCSVData(
            dataname=data_file,
            fromdate=from_date + datetime.timedelta(days=s*step_size),
            todate=first_start_date + datetime.timedelta(days=s*step_size),
            reverse=False)
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

    def next(self):
        if random.random() < self.p.prob:
            self.buy()
        elif random.random() < self.p.prob:
            self.sell()


def random_strategy():
    cerebro = bt.Cerebro()

    cerebro.addstrategy(RandomStrategy)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    return cerebro

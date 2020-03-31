import datetime
import backtrader as bt
import matplotlib as mpl

from baselines import buy_and_hold_strategy

cerebro = buy_and_hold_strategy()
cerebro.broker.setcash(100000.0)

data = bt.feeds.YahooFinanceCSVData(
    dataname='data/NVDA.yahoo.csv',
    fromdate=datetime.datetime(2017, 1, 1),
    todate=datetime.datetime(2019, 1, 1),
    reverse=False)
cerebro.adddata(data)

cerebro.run()

mpl.rc("figure", figsize=(12, 10))
cerebro.plot()

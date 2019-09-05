import datetime
import matplotlib as mpl
import backtrader as bt
from baselines import simple_buy_sell_strategy

cerebro = simple_buy_sell_strategy()
cerebro.broker.setcash(100000.0)

data = bt.feeds.YahooFinanceCSVData(
    dataname='NVDA.csv',
    fromdate=datetime.datetime(2017, 1, 1),
    todate=datetime.datetime(2019, 1, 1),
    reverse=False)
cerebro.adddata(data)

cerebro.run()

mpl.rc("figure", figsize=(12, 10))
cerebro.plot()

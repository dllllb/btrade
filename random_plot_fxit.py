import datetime
import matplotlib as mpl

from baselines import random_strategy, FinamCSV

cerebro = random_strategy()
cerebro.broker.setcash(100000.0)

data = FinamCSV(
    dataname='data/FXIT.finam.csv',
    fromdate=datetime.datetime(2017, 1, 1),
    todate=datetime.datetime(2019, 1, 1))
cerebro.adddata(data)

cerebro.run()

mpl.rc("figure", figsize=(12, 10))
cerebro.plot()

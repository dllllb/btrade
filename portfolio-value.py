import pandas as pd
import matplotlib as mpl

data = [
    'FXGD_100101_190816.csv',
    'FXDE_100101_190816.csv',
    'FXIT_100101_190816.csv',
    'FXMM_100101_190816.csv'
]

prices = []
for e in data:
    hist = pd.read_csv(e, sep='\t')
    dt = pd.to_datetime(hist["<DATE>"].astype(str), format='%Y%m%d').rename('date')
    hist = hist.set_index(dt)
    price = ((hist['<CLOSE>'] + hist['<OPEN>']) / 2).rename(e[:4])
    prices.append(price)

price_df = pd.DataFrame(prices).T
price_df = price_df[~price_df.isnull().any(axis=1)]

portfolios = pd.DataFrame([
    [.25]*4,
    [1., 0, 0, 0],
    [0, 1., 0, 0],
    [0, 0, 1., 0],
    [0, 0, 0, 1.]
], columns=price_df.columns)

pvalue = price_df.dot(portfolios.T)
pvalue = pvalue/pvalue.iloc[0]

pvalue.plot()
mpl.pyplot.show()

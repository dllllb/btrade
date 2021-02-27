import os
import sys
import csv
import pandas as pd
from datetime import datetime
import argparse
import ccxt


parser = argparse.ArgumentParser()
parser.add_argument('csv')
parser.add_argument('exchange')
parser.add_argument('symbol')
parser.add_argument('timeframe')
parser.add_argument('since')
parser.add_argument('until')
args = parser.parse_args()

max_retries = 3
limit = 100

# instantiate the exchange by id
exchange = getattr(ccxt, args.exchange)({
    'enableRateLimit': True,  # required by the Manual
})
# convert since from string to milliseconds integer if needed
since = pd.to_datetime(args.since, utc=True)
until = pd.to_datetime(args.until, utc=True)

# preload all markets from the exchange
exchange.load_markets()

# fetch all candles
earliest_timestamp = int(since.timestamp()*1000)
latest_timestamp = int(until.timestamp()*1000)
timeframe_duration_in_seconds = exchange.parse_timeframe(args.timeframe)
timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
timedelta = limit * timeframe_duration_in_ms
all_ohlcv = []
while True:
    fetch_since = latest_timestamp - timedelta

    num_retries = 0
    try:
        num_retries += 1
        ohlcv = exchange.fetch_ohlcv(args.symbol, args.timeframe, fetch_since, limit)
    except Exception:
        if num_retries > max_retries:
            raise

    # if we have reached the beginning of history
    if ohlcv[0][0] >= latest_timestamp:
        break
    latest_timestamp = ohlcv[0][0]
    all_ohlcv = ohlcv + all_ohlcv

    print(f'{len(all_ohlcv)} candles in total from {exchange.iso8601(all_ohlcv[0][0])} to {exchange.iso8601(all_ohlcv[-1][0])}')

    # if we have reached the checkpoint
    if fetch_since < earliest_timestamp:
        break
ohlcv = exchange.filter_by_since_limit(all_ohlcv, earliest_timestamp, None, key=0)

df = pd.DataFrame(ohlcv, columns=['dt', 'open', 'high', 'low', 'close', 'volume'])
df['dt'] = pd.to_datetime(df.dt, unit='ms')
df = df.set_index('dt')
df.to_csv(args.csv)

print(f'Saved {len(ohlcv)} candles from {exchange.iso8601(ohlcv[0][0])} to {exchange.iso8601(ohlcv[-1][0])} to {args.csv}')

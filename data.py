import ccxt
from ta import volatility
import pandas as pd
from statistics import stdev
from decimal import Decimal

def price_history(market):
    market = market.replace("-", "/")+"T"
    exchange = ccxt.binance()
    history = pd.DataFrame(exchange.fetch_ohlcv(market, "15m", limit=20), columns=['ts', 'o', 'h', 'l', 'c', 'v'])
    return history

def keltner(market, multiplier):
    df = price_history(market)
    h,l,c = df['h'],df['l'], df['c']
    keltner = volatility.KeltnerChannel(high=h,low=l,close=c, window=20, window_atr=10, original_version=False, multiplier=multiplier)
    lband = float(keltner.keltner_channel_lband().iloc[-1])
    mband = float(keltner.keltner_channel_mband().iloc[-1])
    hband = float(keltner.keltner_channel_hband().iloc[-1])
    std_dev = float(standard_deviation(c))
    return lband, mband, hband, std_dev

def standard_deviation(data):

    mean = data.mean()
    close = data.tolist()

    std_deviation = stdev(close, mean)

    return std_deviation

# keltner("SOL-USD", 2)

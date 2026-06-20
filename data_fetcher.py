"""
DATA FETCHER - Live price data laata hai.
Crypto ke liye ccxt (Binance public data, NO API key needed for prices).
Stocks ke liye yfinance (Yahoo Finance, bilkul free).
"""

import pandas as pd

def get_crypto_data(symbol, timeframe="1h", limit=100):
    """
    Crypto ka OHLCV data laata hai Binance se (public data, API key ki zaroorat nahi).
    symbol example: 'BTC/USDT'
    """
    import ccxt
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def get_stock_data(symbol, period="3mo", interval="1d"):
    """
    Stock ka OHLCV data laata hai Yahoo Finance se.
    symbol example: 'AAPL'
    """
    import yfinance as yf
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    df = df.reset_index()
    df.columns = [c.lower() if isinstance(c, str) else c[0].lower() for c in df.columns]
    return df


def get_latest_price(symbol, asset_type="crypto"):
    """Sirf current/latest price chahiye to ye use karo."""
    if asset_type == "crypto":
        df = get_crypto_data(symbol, timeframe="1m", limit=1)
        return float(df["close"].iloc[-1])
    else:
        df = get_stock_data(symbol, period="1d", interval="1m")
        return float(df["close"].iloc[-1])

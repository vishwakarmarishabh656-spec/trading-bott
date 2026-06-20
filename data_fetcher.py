"""
DATA FETCHER - Live price data laata hai.
Crypto ke liye CoinGecko API (free, koi region-block nahi hai, Binance ki tarah).
Stocks ke liye yfinance (Yahoo Finance, bilkul free).
"""

import pandas as pd
import requests

# CoinGecko symbol mapping - hamare config symbols (BTC/USDT) ko
# CoinGecko ke coin-id (bitcoin) mein convert karta hai
COINGECKO_ID_MAP = {
    "BTC/USDT": "bitcoin",
    "ETH/USDT": "ethereum",
}


def get_crypto_data(symbol, timeframe="1h", limit=100):
    """
    Crypto ka price history laata hai CoinGecko se (free, koi API key nahi chahiye,
    aur Binance ki tarah cloud servers ko block nahi karta).
    symbol example: 'BTC/USDT'
    """
    coin_id = COINGECKO_ID_MAP.get(symbol)
    if coin_id is None:
        raise ValueError(f"Symbol {symbol} CoinGecko mapping mein nahi mila")

    # 'days' decide karo timeframe ke hisaab se - hum hourly granularity ke liye
    # kaafi din ka data lete hain taaki 50-period moving average ban sake
    days = 10 if timeframe == "1h" else 2

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    prices = data["prices"]  # list of [timestamp_ms, price]
    df = pd.DataFrame(prices, columns=["timestamp", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # CoinGecko sirf closing price deta hai (free tier mein), to OHLC ko
    # close ke barabar rakhte hain - strategy ke liye ye theek hai kyunki
    # hum sirf 'close' column use karte hain moving average ke liye
    df["open"] = df["close"]
    df["high"] = df["close"]
    df["low"] = df["close"]
    df["volume"] = 0

    df = df.tail(limit).reset_index(drop=True)
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

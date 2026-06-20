"""
STRATEGY - Moving Average Crossover
Simple aur beginner-friendly: jab fast average slow average ko cross 
kare upar se, BUY signal; neeche se, SELL signal.
"""

import pandas as pd
from config import SHORT_MA_WINDOW, LONG_MA_WINDOW


def add_moving_averages(df):
    """DataFrame mein short aur long moving average columns add karta hai."""
    df = df.copy()
    df["ma_short"] = df["close"].rolling(window=SHORT_MA_WINDOW).mean()
    df["ma_long"] = df["close"].rolling(window=LONG_MA_WINDOW).mean()
    return df


def generate_signal(df):
    """
    Latest data dekh ke signal deta hai: 'BUY', 'SELL', ya 'HOLD'.
    
    Logic:
    - Agar pehle short_ma < long_ma tha, aur ab short_ma > long_ma ho gaya -> BUY
    - Agar pehle short_ma > long_ma tha, aur ab short_ma < long_ma ho gaya -> SELL
    - Warna -> HOLD (kuch nahi karna)
    """
    df = add_moving_averages(df)

    # Enough data hona chahiye dono averages calculate karne ke liye
    if len(df) < LONG_MA_WINDOW + 2:
        return "HOLD", df

    df = df.dropna(subset=["ma_short", "ma_long"])
    if len(df) < 2:
        return "HOLD", df

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    crossed_up = prev["ma_short"] <= prev["ma_long"] and curr["ma_short"] > curr["ma_long"]
    crossed_down = prev["ma_short"] >= prev["ma_long"] and curr["ma_short"] < curr["ma_long"]

    if crossed_up:
        return "BUY", df
    elif crossed_down:
        return "SELL", df
    else:
        return "HOLD", df

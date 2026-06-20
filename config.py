"""
CONFIG FILE - Sab settings yahan hain. Ise edit karke aap symbols, 
capital, ya risk limits change kar sakte ho.
"""

# ============ PAPER TRADING SETTINGS ============
STARTING_BALANCE = 10000.0   # Virtual money - REAL paisa nahi hai
RISK_PER_TRADE = 0.02        # Har trade mein max 2% capital risk karega

# ============ SYMBOLS TO WATCH ============
CRYPTO_SYMBOLS = ["BTC/USDT", "ETH/USDT"]      # Binance format (via ccxt)
STOCK_SYMBOLS = ["AAPL", "MSFT", "TSLA"]       # Yahoo Finance format

# ============ STRATEGY SETTINGS ============
SHORT_MA_WINDOW = 20   # Short-term moving average (20 periods)
LONG_MA_WINDOW = 50    # Long-term moving average (50 periods)

# ============ SAFETY / CIRCUIT BREAKER SETTINGS ============
# Ye sabse IMPORTANT section hai - Knight Capital jaisa disaster na ho isliye
MAX_DRAWDOWN_PERCENT = 10.0     # Agar balance 10% gir jaye, bot RUK jayega
MAX_TRADES_PER_DAY = 10         # Ek din mein max itne trades (runaway loop se bachne ke liye)
MAX_TRADES_PER_HOUR = 5         # Ek ghante mein max itne trades

# ============ DATA REFRESH ============
CHECK_INTERVAL_SECONDS = 300    # Har 5 minute mein naya price check karega

# ============ FILES ============
TRADE_LOG_FILE = "trade_log.csv"
STATE_FILE = "bot_state.json"

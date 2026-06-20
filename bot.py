"""
MAIN BOT - Ye sab files ko jodta hai aur har symbol ke liye check karta hai
ki BUY/SELL/HOLD karna hai ya nahi.

YE FILE REAL ORDERS KABHI NAHI BHEJTI. Sab kuch paper_trading_engine 
ke through virtual hai.
"""

from data_fetcher import get_crypto_data, get_stock_data
from strategy import generate_signal
from risk_manager import RiskManager
from paper_trading_engine import PaperTradingEngine
from config import CRYPTO_SYMBOLS, STOCK_SYMBOLS


class TradingBot:
    def __init__(self):
        self.engine = PaperTradingEngine()
        self.risk_manager = RiskManager()
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(message)

    def process_symbol(self, symbol, asset_type):
        """Ek symbol ke liye data fetch karo, signal generate karo, aur trade karo agar zaroori ho."""

        # STEP 1: Safety check sabse pehle - circuit breaker aur rate limits
        can_trade, reason = self.risk_manager.can_trade(self.engine.balance)
        if not can_trade:
            self.log(f"⛔ TRADE BLOCKED: {reason}")
            return

        # STEP 2: Data fetch karo
        try:
            if asset_type == "crypto":
                df = get_crypto_data(symbol, timeframe="1h", limit=100)
            else:
                df = get_stock_data(symbol, period="3mo", interval="1d")
        except Exception as e:
            self.log(f"⚠️ {symbol}: Data fetch fail hua - {e}")
            return

        if df is None or len(df) == 0:
            self.log(f"⚠️ {symbol}: Koi data nahi mila")
            return

        # STEP 3: Strategy se signal lo
        signal, df_with_ma = generate_signal(df)
        current_price = float(df["close"].iloc[-1])

        self.log(f"📊 {symbol}: Price=${current_price:.2f} | Signal={signal}")

        # STEP 4: Signal ke hisaab se virtual trade execute karo
        if signal == "BUY":
            # Stop loss 2% neeche rakha for position sizing calculation
            stop_loss = current_price * 0.98
            quantity = self.risk_manager.calculate_position_size(
                self.engine.balance, current_price, stop_loss
            )
            if quantity > 0:
                success, msg = self.engine.buy(symbol, quantity, current_price)
                if success:
                    self.risk_manager.record_trade()
                    self.log(f"✅ {msg}")

        elif signal == "SELL":
            success, msg = self.engine.sell(symbol, current_price)
            if success:
                self.risk_manager.record_trade()
                self.log(f"✅ {msg}")

    def run_once(self):
        """Sab symbols ko ek baar check karta hai (crypto + stocks dono)."""
        self.log("=" * 50)
        self.log(f"🔄 Bot cycle shuru ho rahi hai...")

        for symbol in CRYPTO_SYMBOLS:
            self.process_symbol(symbol, "crypto")

        for symbol in STOCK_SYMBOLS:
            self.process_symbol(symbol, "stock")

        self.log("✅ Cycle complete.")
        return self.engine.get_summary()


if __name__ == "__main__":
    bot = TradingBot()
    summary = bot.run_once()
    print("\n--- SUMMARY ---")
    print(summary)

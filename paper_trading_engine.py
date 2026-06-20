"""
PAPER TRADING ENGINE - Real order kabhi nahi jaata. Sab kuch virtual hai.
Ye file balance, open positions, aur trade history track karti hai.
"""

import json
import csv
import os
from datetime import datetime
from config import STARTING_BALANCE, TRADE_LOG_FILE, STATE_FILE


class PaperTradingEngine:
    def __init__(self):
        self.balance = STARTING_BALANCE
        self.positions = {}   # symbol -> {"quantity": x, "entry_price": y}
        self.trade_history = []
        self._load_state()

    def _load_state(self):
        """Agar pehle se saved state hai to wahan se resume karo."""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
                    self.balance = state.get("balance", STARTING_BALANCE)
                    self.positions = state.get("positions", {})
            except Exception:
                pass

    def _save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump({"balance": self.balance, "positions": self.positions}, f, indent=2)

    def _log_trade(self, symbol, action, quantity, price):
        file_exists = os.path.exists(TRADE_LOG_FILE)
        with open(TRADE_LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "symbol", "action", "quantity", "price", "balance_after"])
            writer.writerow([
                datetime.now().isoformat(), symbol, action,
                round(quantity, 6), round(price, 2), round(self.balance, 2)
            ])

    def buy(self, symbol, quantity, price):
        """Virtual BUY - real paisa kahin nahi jaata."""
        cost = quantity * price
        if cost > self.balance:
            quantity = self.balance / price  # Jitna afford ho sake
            cost = quantity * price

        if quantity <= 0:
            return False, "Insufficient balance"

        self.balance -= cost
        if symbol in self.positions:
            self.positions[symbol]["quantity"] += quantity
        else:
            self.positions[symbol] = {"quantity": quantity, "entry_price": price}

        self._log_trade(symbol, "BUY", quantity, price)
        self._save_state()
        return True, f"BUY {quantity:.4f} {symbol} @ ${price:.2f}"

    def sell(self, symbol, price):
        """Virtual SELL - poori position close karta hai."""
        if symbol not in self.positions or self.positions[symbol]["quantity"] <= 0:
            return False, "Koi open position nahi hai is symbol mein"

        quantity = self.positions[symbol]["quantity"]
        proceeds = quantity * price
        self.balance += proceeds

        entry_price = self.positions[symbol]["entry_price"]
        pnl = (price - entry_price) * quantity
        pnl_percent = ((price - entry_price) / entry_price) * 100

        del self.positions[symbol]
        self._log_trade(symbol, "SELL", quantity, price)
        self._save_state()

        return True, f"SELL {quantity:.4f} {symbol} @ ${price:.2f} | P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)"

    def get_portfolio_value(self, current_prices):
        """Total value = cash balance + open positions ki current value."""
        total = self.balance
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                total += pos["quantity"] * current_prices[symbol]
        return total

    def get_summary(self, current_prices=None):
        portfolio_value = self.get_portfolio_value(current_prices) if current_prices else self.balance
        total_return = ((portfolio_value - STARTING_BALANCE) / STARTING_BALANCE) * 100
        return {
            "cash_balance": self.balance,
            "portfolio_value": portfolio_value,
            "total_return_percent": total_return,
            "open_positions": self.positions,
        }

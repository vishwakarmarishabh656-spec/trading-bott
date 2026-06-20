"""
RISK MANAGER - Ye file bot ko "khud ko zero" hone se bachati hai.
Yahi Knight Capital disaster wali report ka sabse important lesson hai:
circuit breakers HONA CHAHIYE, optional nahi hai.
"""

from datetime import datetime, timedelta
from config import (
    RISK_PER_TRADE,
    MAX_DRAWDOWN_PERCENT,
    MAX_TRADES_PER_DAY,
    MAX_TRADES_PER_HOUR,
    STARTING_BALANCE,
)


class RiskManager:
    def __init__(self):
        self.trade_timestamps = []   # Har trade ka time track karta hai
        self.is_disabled = False     # Circuit breaker trip hone par True ho jata hai
        self.disable_reason = None

    def calculate_position_size(self, balance, entry_price, stop_loss_price):
        """
        Fixed-fractional risk model: har trade mein balance ka sirf
        RISK_PER_TRADE (default 2%) hi risk hota hai.
        
        Note: Kelly Criterion is liye nahi use kiya kyunki usko sahi se 
        use karne ke liye aapke paas accurate win-rate aur payoff-ratio ka 
        REAL historical data chahiye. Bina us data ke Kelly formula lagana 
        galat aur khatarnak hai - ye safer, simpler approach hai jo 
        beginners ke liye better hai.
        """
        risk_amount = balance * RISK_PER_TRADE
        price_risk_per_unit = abs(entry_price - stop_loss_price)

        if price_risk_per_unit == 0:
            return 0

        position_size = risk_amount / price_risk_per_unit
        return position_size

    def check_circuit_breaker(self, current_balance):
        """
        Drawdown check karta hai. Agar loss MAX_DRAWDOWN_PERCENT se
        zyada ho gaya, bot ko permanently disable kar deta hai.
        """
        drawdown_percent = ((STARTING_BALANCE - current_balance) / STARTING_BALANCE) * 100

        if drawdown_percent >= MAX_DRAWDOWN_PERCENT:
            self.is_disabled = True
            self.disable_reason = (
                f"CIRCUIT BREAKER TRIPPED: Drawdown {drawdown_percent:.2f}% "
                f"ne max limit {MAX_DRAWDOWN_PERCENT}% cross kar diya. "
                f"Bot ROOK gaya hai - sabhi positions close ho jayengi."
            )
            return False
        return True

    def check_rate_limits(self):
        """
        Runaway trading loop se bachata hai (jaisa Knight Capital mein hua tha
        jab system ne 45 minute mein 40 lakh galat trades kar diye the).
        """
        now = datetime.now()

        # Purane timestamps clean karo (24 ghante se purane)
        self.trade_timestamps = [
            t for t in self.trade_timestamps if now - t < timedelta(days=1)
        ]

        trades_today = len([t for t in self.trade_timestamps if now - t < timedelta(days=1)])
        trades_this_hour = len([t for t in self.trade_timestamps if now - t < timedelta(hours=1)])

        if trades_today >= MAX_TRADES_PER_DAY:
            return False, f"Daily trade limit ({MAX_TRADES_PER_DAY}) reach ho gayi hai."
        if trades_this_hour >= MAX_TRADES_PER_HOUR:
            return False, f"Hourly trade limit ({MAX_TRADES_PER_HOUR}) reach ho gayi hai."

        return True, None

    def record_trade(self):
        """Naya trade hone par timestamp record karta hai."""
        self.trade_timestamps.append(datetime.now())

    def can_trade(self, current_balance):
        """
        Master safety check - trade karne se PEHLE ye function call hona
        chahiye. Sab safety checks ek jagah.
        """
        if self.is_disabled:
            return False, self.disable_reason

        breaker_ok = self.check_circuit_breaker(current_balance)
        if not breaker_ok:
            return False, self.disable_reason

        rate_ok, rate_reason = self.check_rate_limits()
        if not rate_ok:
            return False, rate_reason

        return True, None

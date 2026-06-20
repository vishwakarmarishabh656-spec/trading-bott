"""
DASHBOARD - Ye Streamlit app hai jo phone browser mein khulega.
Run karne ke liye terminal mein: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import os
import time

from bot import TradingBot
from config import STARTING_BALANCE, TRADE_LOG_FILE, MAX_DRAWDOWN_PERCENT

st.set_page_config(page_title="Paper Trading Bot", page_icon="📈", layout="centered")

st.title("📈 Paper Trading Bot")
st.caption("⚠️ Ye VIRTUAL money hai. Koi real trade nahi ho raha.")

# Session state mein bot store karo taaki refresh par reset na ho
if "bot" not in st.session_state:
    st.session_state.bot = TradingBot()

bot = st.session_state.bot

col1, col2 = st.columns(2)
with col1:
    run_button = st.button("🔄 Check Market & Trade Now", use_container_width=True)
with col2:
    reset_button = st.button("♻️ Reset Account", use_container_width=True)

if reset_button:
    for f in [TRADE_LOG_FILE, "bot_state.json"]:
        if os.path.exists(f):
            os.remove(f)
    st.session_state.bot = TradingBot()
    st.success("Account reset ho gaya! $10,000 se fresh start.")
    st.rerun()

if run_button:
    with st.spinner("Market check kar rahe hain..."):
        summary = bot.run_once()
    st.success("Done! Neeche logs dekho.")

# ---- Account Summary ----
st.subheader("💰 Account Summary")
summary = bot.engine.get_summary()

m1, m2, m3 = st.columns(3)
m1.metric("Cash Balance", f"${summary['cash_balance']:.2f}")
m2.metric("Portfolio Value", f"${summary['portfolio_value']:.2f}")
m3.metric("Total Return", f"{summary['total_return_percent']:+.2f}%")

drawdown = ((STARTING_BALANCE - summary['portfolio_value']) / STARTING_BALANCE) * 100
if drawdown > 0:
    progress = min(drawdown / MAX_DRAWDOWN_PERCENT, 1.0)
    st.progress(progress, text=f"Drawdown: {drawdown:.1f}% (Circuit breaker @ {MAX_DRAWDOWN_PERCENT}%)")

if bot.risk_manager.is_disabled:
    st.error(f"🛑 {bot.risk_manager.disable_reason}")

# ---- Open Positions ----
st.subheader("📂 Open Positions")
if summary["open_positions"]:
    pos_df = pd.DataFrame([
        {"Symbol": sym, "Quantity": p["quantity"], "Entry Price": p["entry_price"]}
        for sym, p in summary["open_positions"].items()
    ])
    st.dataframe(pos_df, use_container_width=True, hide_index=True)
else:
    st.info("Koi open position nahi hai abhi.")

# ---- Recent Logs ----
st.subheader("📝 Activity Log")
if bot.logs:
    for line in reversed(bot.logs[-30:]):
        st.text(line)
else:
    st.info("Abhi tak koi activity nahi. 'Check Market & Trade Now' dabao.")

# ---- Trade History ----
st.subheader("📜 Trade History")
if os.path.exists(TRADE_LOG_FILE):
    history_df = pd.read_csv(TRADE_LOG_FILE)
    st.dataframe(history_df.tail(20).iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.info("Abhi koi trade nahi hua hai.")

st.divider()
st.caption("Disclaimer: Ye sirf seekhne/practice ke liye hai. Real paisa risk mein nahi hai. "
           "Past performance future returns ki guarantee nahi deta.")

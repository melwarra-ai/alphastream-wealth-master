import streamlit as st
import yfinance as yf
import pd as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import os

# ===== CONFIGURATION & STYLING =====
st.set_page_config(page_title="AlphaStream Wealth Master", page_icon="🛡️", layout="wide")

# (Keep your existing CSS here - omitted for brevity in this block, but included in the logic)

# ===== OPTIMIZED DATA LAYER =====
DB_FILE = "alphastream_wealth.json"

@st.cache_data(ttl=600)  # Cache prices for 10 minutes to prevent API rate limits
def get_market_data(tickers):
    if not tickers:
        return {}
    try:
        data = yf.download(list(tickers), period="1d", progress=False)['Close']
        if isinstance(data, pd.Series):
            return {tickers[0]: float(data.iloc[-1])}
        return {k: float(v) for k, v in data.iloc[-1].to_dict().items()}
    except Exception:
        return {}

def load_db():
    base = {"profiles": {}, "global_logs": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                data = json.load(f)
                return data
            except: return base
    return base

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ===== LOGIC ENHANCEMENT: THE REBALANCE CALCULATOR =====
def calculate_rebalance_orders(prof, current_prices):
    assets = prof.get("assets", {})
    total_val = sum(assets[t]["units"] * current_prices.get(t, 0) for t in assets)
    
    # If no value (new portfolio), use Principal as the base
    base_value = total_val if total_val > 0 else prof["principal"]
    
    orders = []
    for ticker, data in assets.items():
        price = current_prices.get(ticker, 0)
        if price <= 0: continue
        
        target_val = (data["target"] / 100) * base_value
        current_val = data["units"] * price
        diff_val = target_val - current_val
        diff_units = diff_val / price
        
        orders.append({
            "ticker": ticker,
            "action": "BUY" if diff_units > 0 else "SELL",
            "units": abs(diff_units),
            "value": abs(diff_val),
            "target_pct": data["target"],
            "current_pct": (current_val / total_val * 100) if total_val > 0 else 0
        })
    return orders, total_val

# ===== MAIN APP LOGIC =====
db = load_db()

# [Sidebar Logic remains largely the same, but ensure we pass 'db' correctly]

# ===== THE MISSING REBALANCE EXECUTION ENGINE =====
# This replaces the bottom section of your code to make the "Execute" button actually work

if st.session_state.current_page == "📊 Portfolio Manager":
    prof = db["profiles"].get(st.session_state.active_profile)
    if prof:
        tickers = list(prof["assets"].keys())
        prices = get_market_data(tickers)
        orders, current_total = calculate_rebalance_orders(prof, prices)
        
        # Check drift
        max_drift = 0
        if current_total > 0:
            max_drift = max([abs(o['target_pct'] - o['current_pct']) for o in orders])
        
        needs_rebalance = (prof.get("last_rebalanced") is None) or (max_drift > prof.get("drift_tolerance", 5.0))

        if needs_rebalance:
            st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.1); border: 2px solid #ef4444; padding: 20px; border-radius: 12px;">
                    <h3 style="color: #ef4444; margin-top:0;">🚨 Strategy Drift Detected</h3>
                    <p>Current drift is <b>{max_drift:.2f}%</b> (Tolerance: {prof['drift_tolerance']}%). 
                    Execute the following trades to return to target allocation.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Display Trade Table
            df_orders = pd.DataFrame(orders)
            st.table(df_orders[['ticker', 'action', 'units', 'value']].style.format({"units": "{:.4f}", "value": "${:,.2f}"}))
            
            if st.button("🚀 Execute Smart Rebalance", use_container_width=True, type="primary"):
                # Logic: Update units in DB to match targets exactly
                for ticker in prof["assets"]:
                    price = prices.get(ticker)
                    target_val = (prof["assets"][ticker]["target"] / 100) * (current_total if current_total > 0 else prof["principal"])
                    prof["assets"][ticker]["units"] = target_val / price
                
                prof["last_rebalanced"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                save_db(db)
                st.success("Portfolio successfully rebalanced to target weights!")
                st.rerun()

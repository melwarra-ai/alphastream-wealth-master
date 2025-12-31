import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import os

# ===== 1. ENHANCED CONFIGURATION & PERSISTENCE =====
st.set_page_config(
    page_title="AlphaStream Wealth Master",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "alphastream_wealth.json"

@st.cache_data(ttl=300)  # Optimization: Cache market data for 5 minutes
def fetch_market_prices(tickers):
    """Fetch latest prices with error handling for delisted/invalid tickers."""
    if not tickers:
        return {}
    try:
        data = yf.download(list(tickers), period="1d", progress=False)['Close']
        if data.empty:
            return {}
        if isinstance(data, pd.Series):
            return {list(tickers)[0]: float(data.iloc[-1])}
        return {k: float(v) for k, v in data.iloc[-1].to_dict().items() if not pd.isna(v)}
    except Exception:
        return {}

def load_db():
    base_schema = {"profiles": {}, "global_logs": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: 
                data = json.load(f)
                # Ensure schema integrity
                data.setdefault("profiles", {})
                for p in data["profiles"].values():
                    p.setdefault("drift_tolerance", 5.0)
                    p.setdefault("rebalance_logs", [])
                    p.setdefault("last_rebalanced", None)
                return data
            except: return base_schema
    return base_schema

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_profile(prof, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    prof.setdefault("rebalance_logs", []).insert(0, {"date": timestamp, "event": str(message)})
    prof["rebalance_logs"] = prof["rebalance_logs"][:50]

# ===== 2. PREMIUM STYLING (YOUR ORIGINAL CSS) =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%); }
    .premium-card { background: white; padding: 28px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 24px; border: 1px solid #e2e8f0; }
    .desc-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; }
    .profile-tile-warning { border-left: 4px solid #ef4444; animation: pulse-border 2s infinite; background: white; padding: 24px; border-radius: 12px; }
    .profile-tile-optimized { border-left: 4px solid #10b981; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 24px; border-radius: 12px; }
    @keyframes pulse-border { 0%, 100% { border-left-color: #f59e0b; } 50% { border-left-color: #ef4444; } }
    .drift-badge { background: #ef4444; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; animation: pulse-badge 1.5s infinite; }
    @keyframes pulse-badge { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.8; transform: scale(1.05); } }
    .stat-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600; }
    .stat-value { font-size: 1.5rem; font-weight: 700; color: #1e293b; }
    </style>
""", unsafe_allow_html=True)

# ===== 3. SESSION STATE =====
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

# ===== 4. SIDEBAR (STRATEGY & ASSETS) =====
with st.sidebar:
    st.markdown("### 🛡️ AlphaStream")
    nav = st.radio("Navigation", ["🏠 Global Dashboard", "📊 Portfolio Manager"])
    
    st.divider()
    
    # New Profile Form
    with st.expander("🆕 Create New Profile"):
        with st.form("new_prof"):
            n_name = st.text_input("Profile Name")
            n_p = st.number_input("Principal ($)", value=10000.0)
            if st.form_submit_button("Initialize"):
                if n_name and n_name not in st.session_state.db["profiles"]:
                    st.session_state.db["profiles"][n_name] = {
                        "currency": "USD", "principal": n_p, "yearly_goal_pct": 10.0,
                        "start_date": str(date.today()), "assets": {}, "drift_tolerance": 5.0
                    }
                    save_db(st.session_state.db)
                    st.rerun()

    # Asset Management (Only if in Manager View)
    if nav == "📊 Portfolio Manager" and st.session_state.active_profile:
        st.divider()
        prof = st.session_state.db["profiles"][st.session_state.active_profile]
        st.markdown(f"### 🎯 Manage: {st.session_state.active_profile}")
        
        a_sym = st.text_input("Ticker Symbol").upper()
        if a_sym:
            px_data = fetch_market_prices([a_sym])
            if a_sym in px_data:
                price = px_data[a_sym]
                st.success(f"Price: ${price:,.2f}")
                target = st.number_input("Target %", 0.0, 100.0, step=1.0)
                units = st.number_input("Units Owned", 0.0, step=0.01)
                
                if st.button("💾 Save Asset"):
                    prof["assets"][a_sym] = {"units": units, "target": target}
                    save_db(st.session_state.db)
                    st.rerun()
            else:
                st.error("Invalid Ticker")

# ===== 5. MAIN CONTENT LIGIC =====
if nav == "🏠 Global Dashboard":
    st.title("🏠 Global Dashboard")
    profiles = st.session_state.db["profiles"]
    
    # Fetch all prices at once (Optimization)
    all_tickers = set()
    for p in profiles.values(): all_tickers.update(p["assets"].keys())
    prices = fetch_market_prices(all_tickers)
    
    cols = st.columns(2)
    for i, (name, p_data) in enumerate(profiles.items()):
        # Calculate Value & Drift
        val = sum(p_data["assets"][t]["units"] * prices.get(t, 0) for t in p_data["assets"])
        
        has_drift = False
        if val > 0:
            for t, d in p_data["assets"].items():
                actual = (d["units"] * prices.get(t, 0) / val) * 100
                if abs(actual - d["target"]) > p_data["drift_tolerance"]:
                    has_drift = True
        
        # Display Tile
        with cols[i % 2]:
            tile_style = "profile-tile-warning" if has_drift or not p_data["last_rebalanced"] else "profile-tile-optimized"
            status = "🚨 REBALANCE REQUIRED" if has_drift else "✅ OPTIMIZED"
            
            st.markdown(f"""
                <div class="{tile_style}">
                    <div style="text-align:center">{status}</div>
                    <div class="stat-label">Value</div>
                    <div class="stat-value">${val:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Manage {name}", key=f"btn_{name}"):
                st.session_state.active_profile = name
                st.rerun()

else: # Portfolio Manager View
    if not st.session_state.active_profile:
        st.warning("Select a profile")
    else:
        name = st.session_state.active_profile
        prof = st.session_state.db["profiles"][name]
        st.title(f"📊 {name}")
        
        # Optimization: Detailed Analysis & Rebalance Logic
        tickers = list(prof["assets"].keys())
        prices = fetch_market_prices(tickers)
        total_val = sum(prof["assets"][t]["units"] * prices.get(t, 0) for t in tickers)
        
        # REBALANCE CALCULATOR
        st.subheader("⚖️ Rebalance Analysis")
        rebalance_data = []
        for t in tickers:
            curr_val = prof["assets"][t]["units"] * prices.get(t, 0)
            target_val = (prof["assets"][t]["target"] / 100) * (total_val if total_val > 0 else prof["principal"])
            diff = target_val - curr_val
            rebalance_data.append({
                "Ticker": t,
                "Current %": (curr_val/total_val*100) if total_val > 0 else 0,
                "Target %": prof["assets"][t]["target"],
                "Action": "BUY" if diff > 0 else "SELL",
                "Value": abs(diff),
                "Units": abs(diff / prices[t]) if prices.get(t, 0) > 0 else 0
            })
        
        st.table(pd.DataFrame(rebalance_data))
        
        if st.button("🚀 Execute & Sync All Assets", type="primary"):
            # The "Execution" logic updates the JSON units to perfectly match target %
            for t in prof["assets"]:
                target_v = (prof["assets"][t]["target"] / 100) * (total_val if total_val > 0 else prof["principal"])
                prof["assets"][t]["units"] = target_v / prices[t]
            
            prof["last_rebalanced"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_db(st.session_state.db)
            st.success("Portfolio rebalanced!")
            st.rerun()

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import os
import time

# ===== CONFIGURATION =====
st.set_page_config(
    page_title="AlphaStream Wealth Master Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== PREMIUM STYLING =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background: #f8fafc; }
    .premium-card {
        background: white; padding: 24px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white; padding: 20px; border-radius: 12px; text-align: center;
    }
    .trade-buy { color: #10b981; font-weight: 700; }
    .trade-sell { color: #ef4444; font-weight: 700; }
    .drift-badge {
        background: #fee2e2; color: #dc2626; padding: 4px 12px;
        border-radius: 20px; font-size: 0.75rem; font-weight: 700;
        border: 1px solid #fecaca;
    }
    </style>
""", unsafe_allow_html=True)

# ===== ARCHITECTURAL LAYER: DATA & CACHING =====
DB_FILE = "alphastream_wealth.json"

def load_db():
    base = {"profiles": {}, "global_logs": []}
    if not os.path.exists(DB_FILE): return base
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            # Schema migrations/safety
            data.setdefault("profiles", {})
            return data
    except Exception as e:
        st.error(f"Database Error: {e}. Starting with fresh schema.")
        return base

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.db, f, indent=2)

@st.cache_data(ttl=600)  # 10-minute cache for market data
def fetch_market_prices(tickers):
    if not tickers: return {}
    try:
        data = yf.download(list(tickers), period="1d", progress=False)['Close']
        if isinstance(data, pd.Series): # Single ticker case
            return {list(tickers)[0]: float(data.iloc[-1])}
        return {t: float(data[t].iloc[-1]) for t in data.columns}
    except:
        return {}

@st.cache_data(ttl=3600) # 1-hour cache for historical data
def fetch_history(tickers, start_date):
    if not tickers: return pd.DataFrame()
    try:
        df = yf.download(tickers, start=start_date, auto_adjust=True, progress=False)['Close']
        if isinstance(df, pd.Series):
            df = df.to_frame(name=tickers[0])
        return df
    except:
        return pd.DataFrame()

# ===== SESSION INITIALIZATION =====
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

# ===== SIDEBAR LOGIC =====
with st.sidebar:
    st.title("🛡️ AlphaStream")
    nav = st.radio("Navigation", ["Global Dashboard", "Portfolio Manager"])
    
    st.divider()
    
    with st.expander("➕ New Strategy"):
        with st.form("new_prof"):
            name = st.text_input("Profile Name")
            curr = st.selectbox("Currency", ["USD", "CAD"])
            principal = st.number_input("Initial Principal", value=10000.0)
            goal = st.number_input("Yearly Goal %", value=8.0)
            if st.form_submit_button("Create"):
                if name and name not in st.session_state.db["profiles"]:
                    st.session_state.db["profiles"][name] = {
                        "currency": curr, "principal": principal,
                        "goal": goal, "assets": {}, "drift_tol": 5.0,
                        "created_at": str(date.today())
                    }
                    save_db()
                    st.rerun()

# ===== VIEW: GLOBAL DASHBOARD =====
if nav == "Global Dashboard":
    st.title("Market Overview")
    
    profiles = st.session_state.db["profiles"]
    if not profiles:
        st.info("Welcome! Start by creating a strategy in the sidebar.")
    else:
        # Aggregate data
        all_tickers = set()
        for p in profiles.values(): all_tickers.update(p["assets"].keys())
        prices = fetch_market_prices(all_tickers)
        
        total_value = 0
        portfolio_stats = []
        
        for name, data in profiles.items():
            val = sum(a["units"] * prices.get(t, 0) for t, a in data["assets"].items())
            total_value += val
            roi = ((val / data["principal"]) - 1) * 100 if data["principal"] > 0 else 0
            portfolio_stats.append({"Name": name, "Value": val, "ROI": roi})

        col1, col2 = st.columns(2)
        col1.metric("Total Assets Under Management", f"${total_value:,.2f}")
        col2.metric("Active Strategies", len(profiles))

        st.divider()
        st.subheader("Strategy Performance")
        cols = st.columns(min(len(profiles), 3))
        for i, stat in enumerate(portfolio_stats):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="premium-card">
                    <h4>{stat['Name']}</h4>
                    <h2 style="margin:0;">${stat['Value']:,.0f}</h2>
                    <p style="color:{'#10b981' if stat['ROI'] >=0 else '#ef4444'}">{stat['ROI']:.2f}% Total Return</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Manage {stat['Name']}", key=f"btn_{stat['Name']}"):
                    st.session_state.active_profile = stat['Name']
                    # Navigation trick: Streamlit reruns usually handle state changes well
                    st.toast(f"Switching to {stat['Name']}...")
                    time.sleep(0.5)
                    st.rerun()

# ===== VIEW: PORTFOLIO MANAGER =====
else:
    prof_names = list(st.session_state.db["profiles"].keys())
    selected_prof = st.selectbox("Select Strategy", prof_names, 
                               index=prof_names.index(st.session_state.active_profile) if st.session_state.active_profile in prof_names else 0)
    
    if selected_prof:
        st.session_state.active_profile = selected_prof
        prof = st.session_state.db["profiles"][selected_prof]
        
        # UI Header
        st.title(f"📊 {selected_prof}")
        
        # --- ASSET MANAGEMENT SIDEBAR ---
        with st.sidebar:
            st.subheader("Manage Assets")
            t_input = st.text_input("Add/Edit Ticker (e.g. SPY)").upper()
            if t_input:
                t_data = yf.Ticker(t_input).history(period="1d")
                if not t_data.empty:
                    st.success(f"Current Price: ${t_data['Close'].iloc[-1]:,.2f}")
                    target = st.slider("Target %", 0.0, 100.0, float(prof["assets"].get(t_input, {}).get("target", 0.0)))
                    units = st.number_input("Units Held", value=float(prof["assets"].get(t_input, {}).get("units", 0.0)))
                    
                    if st.button("Update Asset"):
                        prof["assets"][t_input] = {"target": target, "units": units}
                        save_db()
                        st.rerun()
                    if t_input in prof["assets"] and st.button("Delete Asset"):
                        del prof["assets"][t_input]
                        save_db()
                        st.rerun()

        # --- ANALYTICS ---
        tickers = list(prof["assets"].keys())
        if not tickers:
            st.warning("Add assets in the sidebar to begin analysis.")
        else:
            hist = fetch_history(tickers, prof["created_at"])
            current_prices = fetch_market_prices(tickers)
            
            # Calculations
            current_val = sum(prof["assets"][t]["units"] * current_prices.get(t, 0) for t in tickers)
            
            # Rebalance Table Logic
            rebalance_data = []
            for t in tickers:
                target_pct = prof["assets"][t]["target"]
                target_dollars = (target_pct / 100) * current_val
                actual_dollars = prof["assets"][t]["units"] * current_prices.get(t, 0)
                diff_dollars = target_dollars - actual_dollars
                diff_units = diff_dollars / current_prices.get(t, 1)
                
                rebalance_data.append({
                    "Asset": t,
                    "Current %": (actual_dollars / current_val * 100) if current_val > 0 else 0,
                    "Target %": target_pct,
                    "Action": "BUY" if diff_units > 0 else "SELL",
                    "Amount": abs(diff_units),
                    "Value": abs(diff_dollars)
                })

            # Dashboard Display
            m1, m2, m3 = st.columns(3)
            m1.metric("Portfolio Value", f"${current_val:,.2f}")
            m2.metric("Target Goal", f"{prof['goal']}%")
            m3.metric("Drift Tolerance", f"{prof['drift_tol']}%")

            st.subheader("⚖️ Rebalance Strategy")
            df_reb = pd.DataFrame(rebalance_data)
            
            # Style the table for the user
            def style_action(val):
                color = '#10b981' if val == 'BUY' else '#ef4444'
                return f'color: {color}; font-weight: bold'

            st.table(df_reb.style.format({
                "Current %": "{:.2f}%",
                "Target %": "{:.2f}%",
                "Amount": "{:.4f}",
                "Value": "${:,.2f}"
            }).applymap(style_action, subset=['Action']))

            # Performance Chart
            if not hist.empty:
                st.subheader("Growth vs Principal")
                # Calculate daily portfolio value
                daily_perf = hist.apply(lambda row: sum(row[t] * prof["assets"][t]["units"] for t in tickers if t in row), axis=1)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily_perf.index, y=daily_perf.values, name="Portfolio Value", line=dict(color='#3b82f6')))
                fig.add_trace(go.Scatter(x=daily_perf.index, y=[prof["principal"]]*len(daily_perf), name="Principal", line=dict(dash='dash', color='gray')))
                st.plotly_chart(fig, use_container_width=True)

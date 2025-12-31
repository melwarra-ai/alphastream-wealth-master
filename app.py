import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json
import os

# ===== CONFIGURATION =====
st.set_page_config(
    page_title="AlphaStream Wealth Master",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== PREMIUM STYLING =====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
    }
    
    .premium-card {
        background: white;
        padding: 28px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 24px;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .premium-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .desc-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(102, 126, 234, 0.4);
    }
    
    .desc-box h4 {
        margin-top: 0;
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    .profile-tile {
        background: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .profile-tile:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    
    .profile-tile-optimized {
        border-left: 4px solid #10b981;
    }
    
    .profile-tile-warning {
        border-left: 4px solid #f59e0b;
        animation: pulse-border 2s infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% { border-left-color: #f59e0b; }
        50% { border-left-color: #ef4444; }
    }
    
    .drift-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        animation: pulse-badge 1.5s infinite;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.4);
    }
    
    @keyframes pulse-badge {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.05); }
    }
    
    .success-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .metric-showcase {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.4);
    }
    
    .metric-showcase h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-showcase p {
        margin: 8px 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .asset-row {
        background: #f8fafc;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 4px solid #3b82f6;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }
    
    .stat-item {
        background: white;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 8px;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: #1e293b;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ===== PERSISTENCE LAYER =====
DB_FILE = "alphastream_wealth.json"

def load_db():
    base_schema = {"profiles": {}, "global_logs": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: 
                data = json.load(f)
                data.setdefault("profiles", {})
                data.setdefault("global_logs", [])
                for p in data["profiles"].values():
                    p.setdefault("drift_tolerance", 5.0)
                    p.setdefault("rebalance_stats", [])
                return data
            except: 
                return base_schema
    return base_schema

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def log_profile(prof, message):
    prof.setdefault("rebalance_logs", [])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    prof["rebalance_logs"].insert(0, {
        "date": timestamp, 
        "event": str(message)
    })
    # Keep only last 50 logs
    prof["rebalance_logs"] = prof["rebalance_logs"][:50]

def description_box(title, content):
    """Render a premium description box"""
    st.markdown(f'''
        <div class="desc-box">
            <h4>{title}</h4>
            <div style="line-height:1.7; font-weight: 300;">{content}</div>
        </div>
    ''', unsafe_allow_html=True)

# ===== SESSION STATE =====
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_page" not in st.session_state:
    st.session_state.current_page = "Global Dashboard"
if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

# ===== SIDEBAR NAVIGATION =====
with st.sidebar:
    st.markdown("### 🛡️ AlphaStream")
    st.caption("Wealth Management Suite v4.0")
    
    st.divider()
    
    # Navigation
    view_mode = st.radio(
        "Navigation",
        ["🏠 Global Dashboard", "📊 Portfolio Manager"],
        key="nav_radio"
    )
    
    st.divider()
    
    # Profile Creation
    st.markdown("### ⚙️ Strategy Setup")
    with st.expander("🆕 Create New Profile", expanded=False):
        with st.form("new_profile_form"):
            n_name = st.text_input("Profile Name", placeholder="e.g., Retirement USD")
            n_curr = st.selectbox("Currency", ["USD", "CAD"])
            n_p = st.number_input("Principal ($)", value=10000.0, step=1000.0, min_value=0.0)
            n_goal = st.number_input("Annual Growth Goal (%)", value=10.0, step=0.5, min_value=0.0)
            n_start = st.date_input("Inception Date", value=date.today() - timedelta(days=365))
            
            submitted = st.form_submit_button("🚀 Initialize Profile", use_container_width=True)
            
            if submitted:
                if n_name and n_name not in st.session_state.db["profiles"]:
                    st.session_state.db["profiles"][n_name] = {
                        "currency": n_curr,
                        "principal": n_p,
                        "yearly_goal_pct": n_goal,
                        "start_date": str(n_start),
                        "assets": {},
                        "rebalance_logs": [],
                        "drift_tolerance": 5.0,
                        "rebalance_stats": []
                    }
                    save_db(st.session_state.db)
                    log_profile(st.session_state.db["profiles"][n_name], "Profile created")
                    st.success(f"✅ Profile '{n_name}' created!")
                    st.rerun()
                elif not n_name:
                    st.error("Please enter a profile name")
                else:
                    st.warning(f"Profile '{n_name}' already exists")
    
    # Profile Selection for Portfolio Manager
    if view_mode == "📊 Portfolio Manager" and st.session_state.db["profiles"]:
        st.divider()
        st.markdown("### 🎯 Active Profile")
        
        profile_names = list(st.session_state.db["profiles"].keys())
        
        if st.session_state.active_profile and st.session_state.active_profile in profile_names:
            default_index = profile_names.index(st.session_state.active_profile)
        else:
            default_index = 0
        
        selected = st.selectbox(
            "Select Profile",
            profile_names,
            index=default_index,
            key="profile_selector"
        )
        
        if selected != st.session_state.active_profile:
            st.session_state.active_profile = selected
            st.rerun()

# ===== MAIN CONTENT =====
if view_mode == "🏠 Global Dashboard":
    st.title("🏠 Global Portfolio Dashboard")
    
    description_box(
        "Portfolio Command Center",
        "Monitor all your investment strategies at a glance. Track performance, detect drift, and manage multiple portfolios with institutional-grade precision."
    )
    
    profiles = st.session_state.db.get("profiles", {})
    
    if not profiles:
        st.info("👋 Welcome to AlphaStream! Create your first investment profile using the sidebar to get started.")
        
        st.markdown("### 🎯 Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="premium-card">
                    <h4>🎯 Drift Detection</h4>
                    <p style="color: #64748b;">
                        Automatic alerts when assets deviate from target allocation. Stay disciplined with your strategy.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="premium-card">
                    <h4>📈 Performance Tracking</h4>
                    <p style="color: #64748b;">
                        Real-time portfolio valuation vs. your target growth path. See if you're on track.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class="premium-card">
                    <h4>⚖️ Smart Rebalancing</h4>
                    <p style="color: #64748b;">
                        Automated calculations show exactly what to buy or sell to restore balance.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
    else:
        # Fetch all prices once
        all_tickers = set()
        for p in profiles.values():
            all_tickers.update(p.get("assets", {}).keys())
        
        prices = {}
        if all_tickers:
            try:
                with st.spinner("📊 Fetching market data..."):
                    raw_px = yf.download(list(all_tickers), period="1d", progress=False)['Close']
                    if len(all_tickers) == 1:
                        prices = {list(all_tickers)[0]: raw_px.iloc[-1]}
                    else:
                        prices = raw_px.iloc[-1].to_dict()
            except Exception as e:
                st.warning(f"⚠️ Could not fetch prices: {str(e)}")
        
        # Summary Metrics
        total_value = 0
        total_drift_count = 0
        
        for p_data in profiles.values():
            p_assets = p_data.get("assets", {})
            curr_v = sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets)
            total_value += curr_v
            
            # Check drift
            if curr_v > 0:
                for t in p_assets:
                    actual_pct = (p_assets[t]["units"] * prices.get(t, 0) / curr_v * 100)
                    target_pct = p_assets[t]["target"]
                    if abs(actual_pct - target_pct) >= p_data.get("drift_tolerance", 5.0):
                        total_drift_count += 1
                        break
        
        # Top Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            st.markdown(f"""
                <div class="metric-showcase">
                    <h3>${total_value:,.0f}</h3>
                    <p>Total Portfolio Value</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown(f"""
                <div class="metric-showcase" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <h3>{len(profiles)}</h3>
                    <p>Active Strategies</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_m3:
            alert_color = "#ef4444" if total_drift_count > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-showcase" style="background: linear-gradient(135deg, {alert_color} 0%, {alert_color} 100%);">
                    <h3>{total_drift_count}</h3>
                    <p>Profiles Need Rebalancing</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Portfolio Grid
        st.markdown("### 📁 Portfolio Strategies")
        
        cols = st.columns(2)
        for i, (name, p_data) in enumerate(profiles.items()):
            p_assets = p_data.get("assets", {})
            curr_v = sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets)
            
            # Check for drift
            has_drift = False
            if curr_v > 0:
                for t in p_assets:
                    actual_pct = (p_assets[t]["units"] * prices.get(t, 0) / curr_v * 100)
                    target_pct = p_assets[t]["target"]
                    if abs(actual_pct - target_pct) >= p_data.get("drift_tolerance", 5.0):
                        has_drift = True
                        break
            
            # Calculate ROI
            start_val = p_data.get('principal', 0)
            roi_pct = ((curr_v / start_val) - 1) * 100 if start_val > 0 else 0
            
            p_flag = "🇺🇸" if p_data.get("currency") == "USD" else "🇨🇦"
            tile_class = "profile-tile-warning" if has_drift else "profile-tile-optimized"
            status_badge = '<span class="drift-badge">🚨 REBALANCE</span>' if has_drift else '<span class="success-badge">✓ Optimized</span>'
            
            with cols[i % 2]:
                st.markdown(f"""
                    <div class="profile-tile {tile_class}">
                        <div>
                            <h3 style="margin: 0 0 8px 0;">{p_flag} {name}</h3>
                            {status_badge}
                        </div>
                        <div style="margin: 16px 0;">
                            <div class="stat-label">Portfolio Value</div>
                            <div class="stat-value">${curr_v:,.0f}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #64748b;">
                            <span>Goal: {p_data['yearly_goal_pct']}%/yr</span>
                            <span style="color: {'#10b981' if roi_pct >= 0 else '#ef4444'}; font-weight: 600;">
                                ROI: {roi_pct:+.1f}%
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📊 Manage {name}", key=f"btn_{name}", use_container_width=True):
                    st.session_state.active_profile = name
                    st.session_state.current_page = "Portfolio Manager"
                    st.rerun()

else:  # Portfolio Manager
    if not st.session_state.active_profile or st.session_state.active_profile not in st.session_state.db["profiles"]:
        st.warning("⚠️ No profile selected. Please select a profile from the sidebar.")
        st.stop()
    
    prof = st.session_state.db["profiles"][st.session_state.active_profile]
    p_flag = "🇺🇸" if prof.get("currency") == "USD" else "🇨🇦"
    
    st.title(f"{p_flag} {st.session_state.active_profile}")
    st.caption(f"Portfolio Manager • Inception: {prof.get('start_date', 'N/A')}")
    
    # Asset Management Section
    st.markdown("### 🎯 Asset Allocation")
    
    with st.expander("⚙️ Drift Strategy Settings", expanded=False):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            new_tolerance = st.number_input(
                "Drift Tolerance (%)",
                value=float(prof.get('drift_tolerance', 5.0)),
                min_value=0.5,
                max_value=20.0,
                step=0.5,
                help="Alert when any asset drifts this much from target"
            )
        with col_d2:
            st.write("")
            st.write("")
            if st.button("💾 Update Tolerance", use_container_width=True):
                prof['drift_tolerance'] = new_tolerance
                save_db(st.session_state.db)
                log_profile(prof, f"Updated drift tolerance to {new_tolerance}%")
                st.success("✅ Drift tolerance updated!")
                st.rerun()
    
    # Add/Edit Asset Form
    with st.expander("➕ Add or Update Asset", expanded=True):
        current_alloc = sum(a.get('target', 0) for a in prof.get("assets", {}).values())
        
        col_a1, col_a2 = st.columns([2, 1])
        
        with col_a1:
            a_sym = st.text_input(
                "Ticker Symbol",
                placeholder="e.g., AAPL, MSFT, VTI",
                help="Enter a valid stock ticker"
            ).upper().strip()
        
        with col_a2:
            st.write("")
            st.write("")
            st.metric("Current Allocation", f"{current_alloc:.1f}%")
        
        is_existing = a_sym in prof.get("assets", {})
        block_new = (not is_existing) and (current_alloc >= 100.0) and (a_sym != "")
        
        if block_new:
            st.error("🚫 Portfolio is at 100% allocation. Remove or reduce other assets first.")
        
        valid_ticker = False
        last_price = 1.0
        
        if a_sym and not block_new:
            try:
                with st.spinner(f"🔍 Validating {a_sym}..."):
                    t_check = yf.Ticker(a_sym)
                    hist = t_check.history(period="1d")
                    if not hist.empty:
                        last_price = hist['Close'].iloc[-1]
                        ticker_info = t_check.info
                        ticker_name = ticker_info.get('longName', a_sym)
                        st.success(f"✓ {ticker_name} ({p_flag} ${last_price:,.2f})")
                        valid_ticker = True
            except:
                st.warning(f"⚠️ Could not validate ticker '{a_sym}'. Check symbol and try again.")
        
        if valid_ticker:
            with st.form("asset_form"):
                default_target = prof.get("assets", {}).get(a_sym, {}).get("target", 0.0)
                other_allocs = current_alloc - default_target
                max_val = 100.0 - other_allocs
                
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    a_w = st.number_input(
                        f"Target Weight % (Max: {max_val:.1f}%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(default_target),
                        step=0.5,
                        help="Desired percentage of portfolio"
                    )
                
                with col_f2:
                    a_u = st.number_input(
                        "Units Owned",
                        min_value=0.0,
                        value=float(prof.get("assets", {}).get(a_sym, {}).get("units", 0.0)),
                        step=0.01,
                        format="%.4f",
                        help="Number of shares you currently own"
                    )
                
                if a_w > 0:
                    target_value = a_w / 100 * prof['principal']
                    suggested_units = target_value / last_price
                    st.info(f"💡 **Buying Guide:** To reach {a_w}% allocation, you need approximately **{suggested_units:.4f} units** of {a_sym} (${target_value:,.2f} value)")
                
                col_b1, col_b2 = st.columns(2)
                
                with col_b1:
                    save_asset = st.form_submit_button("💾 Save Asset", use_container_width=True, type="primary")
                
                with col_b2:
                    if a_sym in prof.get("assets", {}):
                        remove_asset = st.form_submit_button("🗑️ Remove Asset", use_container_width=True)
                    else:
                        remove_asset = False
                
                if save_asset:
                    prof.setdefault("assets", {})[a_sym] = {"units": a_u, "target": a_w}
                    action = "Updated" if is_existing else "Added"
                    log_profile(prof, f"{action} {a_sym}: {a_w}% target, {a_u:.4f} units")
                    save_db(st.session_state.db)
                    st.success(f"✅ {action} {a_sym} successfully!")
                    st.rerun()
                
                if remove_asset:
                    del prof["assets"][a_sym]
                    log_profile(prof, f"Removed {a_sym} from portfolio")
                    save_db(st.session_state.db)
                    st.success(f"✅ Removed {a_sym}")
                    st.rerun()
    
    # Portfolio Analysis
    asset_dict = prof.get("assets", {})
    tickers = list(asset_dict.keys())
    
    if not tickers:
        st.info("👆 Add your first asset above to start tracking your portfolio")
        st.stop()
    
    st.divider()
    
    # Fetch data and analyze
    with st.spinner("📊 Analyzing portfolio..."):
        try:
            raw = yf.download(tickers, start=prof["start_date"], auto_adjust=True, progress=False)
            
            if raw.empty:
                st.error("❌ Could not fetch historical data. Please check your tickers and date range.")
                st.stop()
            
            data = raw['Close']
            if len(tickers) == 1:
                data = pd.DataFrame(data, columns=tickers)
            
            v_t = [t for t in tickers if t in data.columns]
            
            # Calculate daily portfolio value
            daily_val = data[v_t].apply(
                lambda r: sum(r[t] * asset_dict[t]["units"] for t in v_t if t in r.index),
                axis=1
            )
            
            curr_v = daily_val.iloc[-1]
            start_val = prof['principal']
            
            # Calculate time-based metrics
            years = max((data.index[-1] - data.index[0]).days / 365.25, 0.01)
            target_val = start_val * (1 + (prof['yearly_goal_pct']/100))**years
            perc_diff = ((curr_v / target_val) - 1) * 100
            roi_pct = ((curr_v / start_val) - 1) * 100
            
            # Drift detection
            needs_rebalance = False
            drift_assets = []
            
            for t in v_t:
                actual_pct = (asset_dict[t]["units"] * data[t].iloc[-1] / curr_v * 100)
                target_pct = asset_dict[t]["target"]
                drift = abs(actual_pct - target_pct)
                
                if drift >= prof.get("drift_tolerance", 5.0):
                    needs_rebalance = True
                    drift_assets.append((t, drift, actual_pct, target_pct))
            
            # Header Stats
            alert_html = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>' if needs_rebalance else '<span class="success-badge">✓ Optimized</span>'
            
            st.markdown(f"""
                <div class="premium-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <h2 style="margin:0;">{p_flag} Portfolio Analytics</h2>
                        {alert_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Key Metrics
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            
            with col_s1:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">Current Value</div>
                        <div class="stat-value">${curr_v:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s2:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">Total ROI</div>
                        <div class="stat-value" style="color: {'#10b981' if roi_pct >= 0 else '#ef4444'};">
                            {roi_pct:+.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s3:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">vs Target Path</div>
                        <div class="stat-value" style="color: {'#10b981' if perc_diff >= 0 else '#ef4444'};">
                            {perc_diff:+.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s4:
                annualized = ((curr_v / start_val) ** (1/years) - 1) * 100
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">Annualized Return</div>
                        <div class="stat-value" style="color: {'#10b981' if annualized >= 0 else '#ef4444'};">
                            {annualized:.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Performance Chart
            st.markdown("### 📈 Performance vs Goal Path")
            
            fig = go.Figure()
            
            # Actual performance
            fig.add_trace(go.Scatter(
                x=data.index,
                y=daily_val,
                name='Actual Portfolio Value',
                line=dict(color='#3b82f6', width=3),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            
            # Target path
            days = np.arange(len(data.index))
            daily_rate = (prof['yearly_goal_pct'] / 100) / 365.25
            target_path = start_val * (1 + daily_rate) ** days
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=target_path,
                name=f'Target Path ({prof["yearly_goal_pct"]}%/yr)',
                line=dict(color='#10b981', width=2, dash='dash')
            ))
            
            fig.update_layout(
                hovermode='x unified',
                plot_bgcolor='white',
                height=500,
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    title='Date'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    title='Portfolio Value ($)'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Rebalance Section
            st.markdown("### ⚖️ Rebalance Analysis")
            
            if needs_rebalance:
                st.warning(f"⚠️ **{len(drift_assets)} asset(s)** have drifted beyond your {prof.get('drift_tolerance', 5.0)}% tolerance:")
                for ticker, drift, actual, target in drift_assets:
                    st.markdown(f"- **{ticker}**: {drift:.2f}% drift (Actual: {actual:.1f}%, Target: {target:.1f}%)")
            
            # Rebalance Preview Table
            rows = []
            total_turnover = 0
            
            for t in v_t:
                p = data[t].iloc[-1]
                cur_u = asset_dict[t]["units"]
                tar_w = asset_dict[t]['target']
                
                act_val = cur_u * p
                act_w = (act_val / curr_v * 100)
                drift = act_w - tar_w
                
                tar_val = (tar_w / 100) * curr_v
                tar_u = tar_val / p
                
                val_diff = tar_val - act_val
                unit_diff = tar_u - cur_u
                
                total_turnover += abs(val_diff)
                
                if abs(drift) < 0.1:
                    action = "—"
                    action_color = "#64748b"
                else:
                    action = "BUY" if drift < 0 else "SELL"
                    action_color = "#10b981" if drift < 0 else "#ef4444"
                
                rows.append({
                    "Ticker": t,
                    "Current %": f"{act_w:.2f}%",
                    "Target %": f"{tar_w:.2f}%",
                    "Drift": f"{drift:+.2f}%",
                    "Action": action,
                    "Units Change": f"{unit_diff:+.4f}",
                    "Value Change": f"${val_diff:+,.2f}"
                })
            
            df_rebalance = pd.DataFrame(rows)
            
            st.dataframe(
                df_rebalance,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "Current %": st.column_config.TextColumn("Current %", width="small"),
                    "Target %": st.column_config.TextColumn("Target %", width="small"),
                    "Drift": st.column_config.TextColumn("Drift", width="small"),
                    "Action": st.column_config.TextColumn("Action", width="small"),
                    "Units Change": st.column_config.TextColumn("Units Δ", width="medium"),
                    "Value Change": st.column_config.TextColumn("Value Δ", width="medium")
                }
            )
            
            st.metric("Total Trade Volume Required", f"${total_turnover:,.2f}")
            
            st.divider()
            
            # Execution & Logs
            col_exec1, col_exec2 = st.columns(2)
            
            with col_exec1:
                st.markdown("### 🚀 Execute Rebalance")
                
                if st.button("⚡ Execute Rebalancing Now", type="primary", use_container_width=True):
                    # Update units to target allocations
                    detail_log = f"Rebalanced {datetime.now().strftime('%Y-%m-%d %H:%M')} - "
                    changes = []
                    
                    for t in v_t:
                        old_units = asset_dict[t]["units"]
                        new_units = (asset_dict[t]["target"] / 100 * curr_v) / data[t].iloc[-1]
                        asset_dict[t]["units"] = new_units
                        changes.append(f"{t}: {new_units-old_units:+.4f}")
                    
                    detail_log += ", ".join(changes)
                    
                    prof.setdefault("rebalance_stats", []).insert(0, detail_log)
                    prof["rebalance_stats"] = prof["rebalance_stats"][:20]  # Keep last 20
                    
                    log_profile(prof, "Portfolio rebalanced to target allocations")
                    save_db(st.session_state.db)
                    
                    st.success("✅ Portfolio rebalanced successfully!")
                    st.balloons()
                    st.rerun()
                
                st.markdown("#### 📊 Recent Rebalances")
                for entry in prof.get("rebalance_stats", [])[:5]:
                    st.caption(entry)
            
            with col_exec2:
                st.markdown("### 📜 Activity Log")
                for log_entry in prof.get("rebalance_logs", [])[:10]:
                    st.caption(f"**{log_entry['date']}**: {log_entry['event']}")
        
        except Exception as e:
            st.error(f"❌ Error analyzing portfolio: {str(e)}")
            st.stop()

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 20px;">
        <p><strong>AlphaStream Wealth Master</strong> • Portfolio Management Suite v4.0</p>
        <p style="font-size: 0.85rem;">
            Real-time market data powered by Yahoo Finance. For informational purposes only.
        </p>
    </div>
""", unsafe_allow_html=True)

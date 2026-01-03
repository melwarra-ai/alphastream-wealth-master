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
        padding: 24px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .profile-tile:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    
    .profile-tile-optimized {
        border-left: 4px solid #10b981;
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    }
    
    .profile-tile-warning {
        border-left: 4px solid #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        animation: pulse-border 2s infinite;
    }
    
    @keyframes pulse-border {
        0%, 100% { 
            border-left-color: #f97316;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        50% { 
            border-left-color: #ef4444;
            box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3);
        }
    }
    
    .drift-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    
    .success-badge {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    .metric-container {
        background: white;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 4px solid #3b82f6;
    }
    
    .metric-container:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .stat-item {
        text-align: center;
        padding: 12px;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 6px;
    }
    
    .stat-value {
        color: #1e293b;
        font-size: 1.6rem;
        font-weight: 700;
    }
    
    .benchmark-note {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        padding: 16px;
        border-radius: 8px;
        margin: 16px 0;
    }
    
    .allocation-blocked {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 2px solid #ef4444;
        padding: 16px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        color: #991b1b;
        margin: 16px 0;
        font-size: 0.95rem;
    }
    
    .buying-guide {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #1e40af;
        padding: 16px;
        border-radius: 8px;
        margin: 12px 0;
        font-weight: 600;
        color: #1e40af;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    .buying-guide-highlight {
        background: #1e40af;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 1rem;
        display: inline-block;
        margin: 0 2px;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: #1e293b;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-bottom: 8px;
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
                    p.setdefault("last_rebalanced", None)
                    p.setdefault("benchmark", None)
                    # ASSET ALLOCATION: Add new tracking field
                    p.setdefault("allocated_pct", 0.0)
                    # ASSET ALLOCATION: Ensure all assets have purchases list
                    for asset_key, asset_data in p.get("assets", {}).items():
                        asset_data.setdefault("purchases", [])
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
    prof["rebalance_logs"] = prof["rebalance_logs"][:50]

def description_box(title, content):
    st.markdown(f'''
        <div class="desc-box">
            <h4>{title}</h4>
            <div style="line-height:1.7; font-weight: 300;">{content}</div>
        </div>
    ''', unsafe_allow_html=True)

def check_recently_rebalanced(last_rebalanced_str):
    """Check if portfolio was rebalanced in last 24 hours"""
    if not last_rebalanced_str:
        return False
    try:
        last_rebal_time = datetime.strptime(last_rebalanced_str, "%Y-%m-%d %H:%M:%S")
        hours_since = (datetime.now() - last_rebal_time).total_seconds() / 3600
        return hours_since < 24
    except:
        return False

# ASSET ALLOCATION: New function to calculate average cost per asset
def calculate_average_cost(asset_data, allocated_pct):
    """
    Calculate weighted average cost for an asset.
    Returns None if portfolio not fully allocated (allocated_pct < 100).
    
    Args:
        asset_data: Asset dict with 'purchases' list
        allocated_pct: Total portfolio allocation percentage
    
    Returns:
        float or None: Average cost per unit, or None if not fully allocated
    """
    # CRITICAL: Only calculate after full allocation
    if allocated_pct < 100.0:
        return None
    
    purchases = asset_data.get("purchases", [])
    if not purchases:
        return None
    
    total_invested = sum(p.get("amount", 0) for p in purchases)
    total_quantity = sum(p.get("quantity", 0) for p in purchases)
    
    if total_quantity == 0:
        return None
    
    return total_invested / total_quantity

# ASSET ALLOCATION: Modified drift detection - suppresses drift until 100% allocated
def calculate_drift_status(p_data, prices):
    """
    Calculate if portfolio needs rebalancing.
    MODIFIED: Drift detection suppressed until allocated_pct >= 100%
    """
    p_assets = p_data.get("assets", {})
    if not p_assets:
        return False, []
    
    curr_v = float(sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets))
    if curr_v == 0:
        return False, []
    
    # ASSET ALLOCATION: Check allocation completion status
    allocated_pct = p_data.get("allocated_pct", 0.0)
    if allocated_pct < 100.0:
        # Allocation in progress - suppress drift detection
        return False, []
    
    has_rebalanced = p_data.get("last_rebalanced") is not None
    recently_rebalanced = check_recently_rebalanced(p_data.get("last_rebalanced"))
    
    # Never rebalanced = needs rebalance
    if not has_rebalanced:
        return True, []
    
    # Recently rebalanced = don't check drift yet
    if recently_rebalanced:
        return False, []
    
    # Check actual drift
    drift_details = []
    for t in p_assets:
        actual_pct = float((p_assets[t]["units"] * prices.get(t, 0) / curr_v * 100))
        target_pct = float(p_assets[t]["target"])
        drift = abs(actual_pct - target_pct)
        if drift >= p_data.get("drift_tolerance", 5.0):
            drift_details.append((t, drift, actual_pct, target_pct))
    
    return len(drift_details) > 0, drift_details

# ===== SESSION STATE =====
if "db" not in st.session_state:
    st.session_state.db = load_db()
if "current_page" not in st.session_state:
    st.session_state.current_page = "Global Dashboard"
if "active_profile" not in st.session_state:
    st.session_state.active_profile = None

# ===== SIDEBAR =====
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
                        "rebalance_stats": [],
                        "last_rebalanced": None,
                        "benchmark": None,
                        "allocated_pct": 0.0  # ASSET ALLOCATION: New field
                    }
                    save_db(st.session_state.db)
                    log_profile(st.session_state.db["profiles"][n_name], "Profile created")
                    st.success(f"✅ Profile '{n_name}' created!")
                    st.rerun()
                elif not n_name:
                    st.error("Please enter a profile name")
                else:
                    st.warning(f"Profile '{n_name}' already exists")
    
    # Profile-specific sidebar content
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
        
        prof = st.session_state.db["profiles"][st.session_state.active_profile]
        p_flag = "🇺🇸" if prof.get("currency") == "USD" else "🇨🇦"
        
        st.divider()
        
        # Drift Strategy
        st.markdown("### ⚙️ Drift Strategy")
        st.caption("Set tolerance threshold for rebalance alerts")
        with st.expander("ℹ️ What is drift tolerance?", expanded=False):
            st.markdown("""
            **Drift tolerance** controls when you get rebalancing alerts.
            
            - If an asset's current % differs from target % by more than this amount, you'll see a 🚨 alert
            - **Example:** 5% tolerance means AAPL at 30% (target 25%) triggers an alert
            - **Lower tolerance** = more frequent rebalancing, tighter control
            - **Higher tolerance** = less frequent rebalancing, more flexibility
            """)
        
        new_tolerance = st.number_input(
            "Drift Tolerance (%)",
            value=float(prof.get('drift_tolerance', 5.0)),
            min_value=0.5,
            max_value=20.0,
            step=0.5,
            help="Alert when any asset drifts this much from target",
            key="drift_tolerance_input"
        )
        if st.button("💾 Update Tolerance", use_container_width=True, key="update_tolerance"):
            prof['drift_tolerance'] = new_tolerance
            save_db(st.session_state.db)
            log_profile(prof, f"Updated drift tolerance to {new_tolerance}%")
            st.success("✅ Updated!")
            st.rerun()
        
        st.divider()
        
        # Benchmark Selection
        st.markdown("### 📊 Benchmark Comparison")
        st.caption("Compare your portfolio against market benchmarks")
        with st.expander("ℹ️ Why use a benchmark?", expanded=False):
            st.markdown("""
            **Benchmarks** help you evaluate your portfolio's performance.
            
            - The chart shows what would happen if you invested 100% in the benchmark
            - **Example:** If you choose SPY, you'll see S&P 500 performance vs your allocation
            - **Outperforming** the benchmark means your strategy is adding value
            - **Underperforming** suggests passive investing might be better
            """)
        
        benchmark_options = {
            "None": None,
            "S&P 500 (SPY)": "SPY",
            "NASDAQ-100 (QQQ)": "QQQ",
            "Total Market (VTI)": "VTI",
            "Russell 2000 (IWM)": "IWM",
            "Dow Jones (DIA)": "DIA"
        }
        
        current_benchmark = prof.get('benchmark')
        benchmark_index = 0
        for idx, (key, value) in enumerate(benchmark_options.items()):
            if value == current_benchmark:
                benchmark_index = idx
                break
        
        selected_benchmark = st.selectbox(
            "Select Benchmark",
            options=list(benchmark_options.keys()),
            index=benchmark_index,
            key="benchmark_select"
        )
        
        if st.button("💾 Save Benchmark", use_container_width=True, key="save_benchmark"):
            prof['benchmark'] = benchmark_options[selected_benchmark]
            save_db(st.session_state.db)
            st.success("✅ Benchmark saved!")
            st.rerun()
        
        if prof.get('benchmark'):
            st.caption(f"📊 Active: {prof['benchmark']} - Shows 100% investment comparison")
        else:
            st.caption("No benchmark selected")
        
        st.divider()
        
        # ASSET ALLOCATION: New deployment recording section
        st.markdown("### 💰 Capital Deployment")
        st.caption("Record partial capital deployment events")
        
        allocated_pct = prof.get("allocated_pct", 0.0)
        remaining_pct = max(0, 100.0 - allocated_pct)
        
        # Progress bar
        progress_color = "#10b981" if allocated_pct >= 100 else "#f97316"
        st.markdown(f"""
            <div style="margin: 12px 0;">
                <div style="background: #e5e7eb; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="background: {progress_color}; height: 100%; width: {min(allocated_pct, 100)}%; transition: all 0.3s;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if allocated_pct >= 100.0:
            st.success(f"✅ Fully Allocated: {allocated_pct:.1f}%")
            st.caption("Drift monitoring is active")
        else:
            st.warning(f"⚠️ Deployed: {allocated_pct:.1f}% | Remaining: {remaining_pct:.1f}%")
            st.caption("Drift monitoring activates at 100%")
        
        with st.expander("➕ Record Deployment Event", expanded=False):
            st.markdown("""
            **Record new capital deployment** to track your investment journey.
            
            - Each deployment buys assets at current market prices
            - Purchase history enables accurate average cost calculation
            - Drift detection activates only after 100% deployment
            """)
            
            if remaining_pct > 0:
                deploy_pct = st.number_input(
                    "Deployment % (of total principal)",
                    min_value=0.1,
                    max_value=remaining_pct,
                    value=min(20.0, remaining_pct),
                    step=0.1,
                    help=f"Maximum available: {remaining_pct:.1f}%"
                )
                
                deploy_date = st.date_input(
                    "Deployment Date",
                    value=date.today(),
                    max_value=date.today()
                )
                
                if prof.get("assets"):
                    st.caption("**Assets will be purchased at current market prices**")
                    
                    if st.button("📥 Record Deployment", type="primary", use_container_width=True):
                        # Fetch current prices
                        tickers = list(prof["assets"].keys())
                        try:
                            with st.spinner("Fetching current prices..."):
                                prices = {}
                                for ticker in tickers:
                                    t_obj = yf.Ticker(ticker)
                                    hist = t_obj.history(period="1d")
                                    if not hist.empty:
                                        prices[ticker] = float(hist['Close'].iloc[-1])
                                
                                if len(prices) != len(tickers):
                                    st.error("Could not fetch prices for all assets")
                                else:
                                    # Record purchases for each asset
                                    deploy_amount = (deploy_pct / 100) * prof["principal"]
                                    
                                    for ticker, asset_data in prof["assets"].items():
                                        target_pct = asset_data["target"]
                                        # Allocate proportionally based on target weights
                                        asset_deploy_pct = (target_pct / 100) * deploy_pct
                                        asset_amount = (asset_deploy_pct / 100) * prof["principal"]
                                        price = prices[ticker]
                                        quantity = asset_amount / price
                                        
                                        # Add to purchase history
                                        purchase = {
                                            "date": str(deploy_date),
                                            "amount": asset_amount,
                                            "price": price,
                                            "quantity": quantity,
                                            "allocated_pct": asset_deploy_pct
                                        }
                                        asset_data.setdefault("purchases", []).append(purchase)
                                        
                                        # Update total units
                                        asset_data["units"] = asset_data.get("units", 0) + quantity
                                    
                                    # Update allocated percentage
                                    prof["allocated_pct"] = min(100.0, prof.get("allocated_pct", 0) + deploy_pct)
                                    
                                    log_profile(prof, f"Deployed {deploy_pct:.1f}% of capital (${deploy_amount:,.0f})")
                                    save_db(st.session_state.db)
                                    st.success(f"✅ Deployment recorded: {deploy_pct:.1f}%")
                                    st.rerun()
                        
                        except Exception as e:
                            st.error(f"Error recording deployment: {str(e)}")
                else:
                    st.info("Add assets first before recording deployments")
            else:
                st.info("Portfolio fully allocated (100%)")
        
        st.divider()
        
        # Asset Allocation
        st.markdown("### 🎯 Asset Allocation")
        st.caption("Add assets to your portfolio and set target percentages")
        with st.expander("ℹ️ How asset allocation works", expanded=False):
            st.markdown("""
            **Asset allocation** is your investment strategy blueprint.
            
            - **Target %**: Your desired allocation (e.g., 40% AAPL, 30% GOOGL, 30% MSFT)
            - **Total must equal 100%** to be fully allocated
            - **Buying Guide**: Shows exactly how many shares to buy
            - **Rebalancing**: When prices change, your % drifts—rebalance to restore targets
            
            💡 **Pro tip:** Diversify across sectors to reduce risk
            """)
        
        with st.expander("💡 Need help finding tickers?", expanded=False):
            st.caption("**Popular Examples:**")
            st.caption("• Stocks: AAPL, MSFT, GOOGL, AMZN, TSLA")
            st.caption("• ETFs: SPY, QQQ, VTI, VOO, IWM")
            st.caption("• Bonds: AGG, BND, TLT")
            st.caption("")
            st.caption("Find more at: finance.yahoo.com")
        
        # Calculate current allocation
        current_alloc = sum(a.get('target', 0) for a in prof.get("assets", {}).values())
        
        # Allocation progress bar with color coding
        progress_color = "🟢" if current_alloc >= 100 else "🟠"
        bar_color = "#10b981" if current_alloc >= 100 else "#f97316"
        
        st.markdown(f"""
            <div style="margin: 12px 0;">
                <div style="background: #e5e7eb; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="background: {bar_color}; height: 100%; width: {min(current_alloc, 100)}%; transition: all 0.3s;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"**{progress_color} Allocated: {current_alloc:.1f}% / 100%**")
        
        # Asset ticker input
        a_sym = st.text_input(
            "Ticker Symbol",
            placeholder="e.g., AAPL, MSFT",
            help="Enter stock ticker and press Enter",
            key="ticker_input"
        ).upper().strip()
        
        is_existing = a_sym in prof.get("assets", {})
        
        # Calculate available allocation space
        if is_existing:
            other_allocs = current_alloc - prof["assets"][a_sym].get("target", 0)
        else:
            other_allocs = current_alloc
        
        max_available = 100.0 - other_allocs
        block_new = (not is_existing) and (max_available <= 0) and (a_sym != "")
        
        # Show allocation block warning
        if block_new:
            st.markdown("""
                <div class="allocation-blocked">
                    🚫 PORTFOLIO AT 100%<br>
                    Remove or reduce existing assets first!
                </div>
            """, unsafe_allow_html=True)
        
        valid_ticker = False
        last_price = 1.0
        ticker_name = ""
        
        # Validate ticker
        if a_sym and not block_new:
            try:
                with st.spinner(f"🔍 Validating {a_sym}..."):
                    t_check = yf.Ticker(a_sym)
                    hist = t_check.history(period="1d")
                    if not hist.empty:
                        last_price = float(hist['Close'].iloc[-1])
                        try:
                            ticker_info = t_check.info
                            ticker_name = ticker_info.get('longName', a_sym)
                        except:
                            ticker_name = a_sym
                        st.success(f"✓ {ticker_name}")
                        st.caption(f"**Current Price:** {p_flag} ${last_price:,.2f}")
                        valid_ticker = True
                    else:
                        st.error(f"❌ No price data available for '{a_sym}'")
            except:
                if a_sym:
                    st.error(f"❌ Cannot validate '{a_sym}'. Please verify it's a valid stock symbol.")
                    st.caption("💡 Try: AAPL, MSFT, GOOGL, TSLA, SPY, QQQ")
        
        # Asset form
        if valid_ticker:
            st.markdown("---")
            
            default_target = prof.get("assets", {}).get(a_sym, {}).get("target", 0.0)
            default_units = prof.get("assets", {}).get(a_sym, {}).get("units", 0.0)
            
            a_w = st.number_input(
                f"Target Allocation %",
                min_value=0.0,
                max_value=max_available,
                value=min(float(default_target), max_available),
                step=0.5,
                help=f"Maximum available: {max_available:.1f}%",
                key="target_weight"
            )
            
            # Buying Guide
            if a_w > 0:
                target_value = (a_w / 100) * prof['principal']
                suggested_units = target_value / last_price
                
                st.markdown(f"""
                    <div class="buying-guide">
                        💡 <strong>Buy Guide:</strong> To reach {a_w}% → Buy <span class="buying-guide-highlight">{suggested_units:.4f} units</span> (${target_value:,.0f} @ ${last_price:,.2f}/unit)
                    </div>
                """, unsafe_allow_html=True)
            
            a_u = st.number_input(
                "Units Currently Owned",
                min_value=0.0,
                value=float(default_units),
                step=0.0001,
                format="%.4f",
                help="How many shares do you own?",
                key="units_owned"
            )
            
            st.markdown("---")
            
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                save_disabled = (a_w <= 0) or (a_w > max_available)
                if st.button("💾 Save Asset", use_container_width=True, type="primary", key="save_asset", disabled=save_disabled):
                    # ASSET ALLOCATION: Ensure purchases list exists
                    prof.setdefault("assets", {})[a_sym] = {
                        "units": a_u,
                        "target": a_w,
                        "purchases": prof.get("assets", {}).get(a_sym, {}).get("purchases", [])
                    }
                    action = "Updated" if is_existing else "Added"
                    log_profile(prof, f"{action} {a_sym}: {a_w}% target, {a_u:.4f} units")
                    save_db(st.session_state.db)
                    st.success(f"✅ {action} {a_sym}!")
                    st.rerun()
            
            with col_b2:
                if is_existing:
                    if st.button("🗑️ Remove", use_container_width=True, key="remove_asset"):
                        del prof["assets"][a_sym]
                        log_profile(prof, f"Removed {a_sym} from portfolio")
                        save_db(st.session_state.db)
                        st.success(f"✅ Removed {a_sym}!")
                        st.rerun()
        
        # Show existing assets
        if prof.get("assets"):
            st.divider()
            st.markdown("### 📋 Current Assets")
            for ticker, data in prof["assets"].items():
                st.caption(f"**{ticker}**: {data['target']}% ({data['units']:.4f} units)")
        
        # Activity Log
        st.divider()
        st.markdown("### 📜 Activity Log")
        rebalance_logs = prof.get("rebalance_logs", [])
        if rebalance_logs:
            with st.expander("📋 Recent Activity", expanded=False):
                for log_entry in rebalance_logs[:10]:
                    st.caption(f"**{log_entry['date']}**: {log_entry['event']}")
        else:
            st.caption("No activity yet")

# ===== MAIN CONTENT =====
if view_mode == "🏠 Global Dashboard":
    st.title("🏠 Global Portfolio Dashboard")
    st.caption("Overview of all your investment profiles")
    
    description_box(
        "Portfolio Command Center",
        "Monitor all your investment strategies from a single view. Track performance, detect drift, and identify rebalancing opportunities across your entire wealth ecosystem."
    )
    
    profiles = st.session_state.db["profiles"]
    
    if not profiles:
        st.info("👈 **Create your first profile** using the sidebar to get started")
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Create a Profile** in the sidebar
        2. **Add Assets** with target allocations
        3. **Track Performance** with real-time analytics
        4. **Rebalance** when drift alerts appear
        """)
        st.stop()
    
    # Fetch all prices once
    all_tickers = set()
    for prof in profiles.values():
        all_tickers.update(prof.get("assets", {}).keys())
    
    prices = {}
    if all_tickers:
        with st.spinner("📊 Loading market data..."):
            try:
                for ticker in all_tickers:
                    t_obj = yf.Ticker(ticker)
                    hist = t_obj.history(period="1d")
                    if not hist.empty:
                        prices[ticker] = float(hist['Close'].iloc[-1])
            except:
                pass
    
    # Profile grid
    st.markdown("### 📊 Active Profiles")
    
    # Calculate grid layout
    num_profiles = len(profiles)
    cols_per_row = 3
    
    profile_items = list(profiles.items())
    
    for row_start in range(0, num_profiles, cols_per_row):
        cols = st.columns(cols_per_row)
        
        for col_idx, (p_name, p_data) in enumerate(profile_items[row_start:row_start + cols_per_row]):
            with cols[col_idx]:
                p_assets = p_data.get("assets", {})
                p_flag = "🇺🇸" if p_data.get("currency") == "USD" else "🇨🇦"
                
                # Calculate metrics
                if p_assets and prices:
                    curr_val = sum(p_assets[t]["units"] * prices.get(t, 0) for t in p_assets)
                    principal = float(p_data.get("principal", 1))
                    roi = ((curr_val / principal) - 1) * 100 if principal > 0 else 0
                    
                    # ASSET ALLOCATION: Modified drift check
                    needs_rebal, drift_list = calculate_drift_status(p_data, prices)
                    
                    allocated_pct = p_data.get("allocated_pct", 0.0)  # ASSET ALLOCATION
                else:
                    curr_val = 0
                    roi = 0
                    needs_rebal = False
                    drift_list = []
                    allocated_pct = p_data.get("allocated_pct", 0.0)  # ASSET ALLOCATION
                
                # Determine tile styling
                if needs_rebal:
                    tile_class = "profile-tile profile-tile-warning"
                elif len(p_assets) > 0 and allocated_pct >= 100:  # ASSET ALLOCATION: Check allocation
                    tile_class = "profile-tile profile-tile-optimized"
                else:
                    tile_class = "profile-tile"
                
                # Profile card
                st.markdown(f"""
                    <div class="{tile_class}">
                        <h3 style="margin: 0 0 8px 0;">{p_flag} {p_name}</h3>
                        <div style="color: #64748b; font-size: 0.9rem; margin-bottom: 16px;">
                            {len(p_assets)} assets • {p_data.get('drift_tolerance', 5)}% drift tolerance
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="color: #64748b;">Value</span>
                            <span style="font-weight: 600;">${curr_val:,.0f}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
                            <span style="color: #64748b;">ROI</span>
                            <span style="font-weight: 600; color: {'#10b981' if roi >= 0 else '#ef4444'};">{roi:+.1f}%</span>
                        </div>
                """, unsafe_allow_html=True)
                
                # ASSET ALLOCATION: Show deployment status
                if allocated_pct < 100:
                    st.markdown(f"""
                        <div style="background: #fef3c7; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px;">
                            <strong>⚠️ Deployment:</strong> {allocated_pct:.0f}% / 100%
                        </div>
                    """, unsafe_allow_html=True)
                
                if needs_rebal:
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                                    color: #991b1b; padding: 12px; border-radius: 8px; 
                                    font-weight: 600; text-align: center; margin-bottom: 12px;">
                            🚨 REBALANCE REQUIRED
                        </div>
                    """, unsafe_allow_html=True)
                elif p_data.get("last_rebalanced"):
                    st.markdown("""
                        <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                                    color: #065f46; padding: 12px; border-radius: 8px; 
                                    font-weight: 600; text-align: center; margin-bottom: 12px;">
                            ✅ BALANCED
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="background: #f1f5f9; color: #475569; padding: 12px; 
                                    border-radius: 8px; font-weight: 600; text-align: center; margin-bottom: 12px;">
                            ⚪ NOT REBALANCED
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button(f"📊 Manage {p_name}", key=f"btn_{p_name}", use_container_width=True):
                    st.session_state.active_profile = p_name
                    st.session_state.current_page = "Portfolio Manager"
                    st.rerun()
    
    st.divider()
    
    # Quick stats
    st.markdown("### 📈 Portfolio Summary")
    
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    
    total_profiles = len(profiles)
    total_value = sum(
        sum(p.get("assets", {}).get(t, {}).get("units", 0) * prices.get(t, 0) 
            for t in p.get("assets", {}))
        for p in profiles.values()
    )
    profiles_with_drift = sum(1 for p in profiles.values() if calculate_drift_status(p, prices)[0])
    total_assets = sum(len(p.get("assets", {})) for p in profiles.values())
    
    with col_g1:
        st.metric("Active Profiles", total_profiles)
    with col_g2:
        st.metric("Total Value", f"${total_value:,.0f}")
    with col_g3:
        st.metric("Rebalance Alerts", profiles_with_drift)
    with col_g4:
        st.metric("Total Assets", total_assets)

else:  # Portfolio Manager
    if not st.session_state.active_profile or st.session_state.active_profile not in st.session_state.db["profiles"]:
        st.warning("⚠️ No profile selected. Please select a profile from the sidebar.")
        st.stop()
    
    prof = st.session_state.db["profiles"][st.session_state.active_profile]
    p_flag = "🇺🇸" if prof.get("currency") == "USD" else "🇨🇦"
    
    # ASSET ALLOCATION: Get allocation status
    allocated_pct = prof.get("allocated_pct", 0.0)
    is_fully_allocated = allocated_pct >= 100.0
    
    st.title(f"{p_flag} {st.session_state.active_profile}")
    st.caption(f"Portfolio Manager • Inception: {prof.get('start_date', 'N/A')} • Drift Tolerance: {prof.get('drift_tolerance', 5.0)}%")
    
    # ASSET ALLOCATION: Show deployment status banner
    if not is_fully_allocated:
        st.warning(f"⚠️ **Capital Deployment Status:** {allocated_pct:.1f}% allocated. Drift monitoring will activate at 100%.")
    
    # Portfolio Summary at top
    has_rebalanced = prof.get("last_rebalanced") is not None
    recently_rebalanced = check_recently_rebalanced(prof.get("last_rebalanced"))
    
    col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
    with col_sum1:
        asset_count = len(prof.get("assets", {}))
        st.metric("Total Assets", asset_count)
    with col_sum2:
        prof_start = datetime.strptime(prof.get('start_date', str(date.today())), '%Y-%m-%d')
        age_years = max((date.today() - prof_start.date()).days / 365.25, 0.01)
        st.metric("Portfolio Age", f"{age_years:.1f} years")
    with col_sum3:
        if prof.get("last_rebalanced"):
            st.metric("Last Rebalanced", prof["last_rebalanced"][:10])
        else:
            st.metric("Last Rebalanced", "Never")
    with col_sum4:
        # ASSET ALLOCATION: Modified status display
        if not is_fully_allocated:
            st.metric("Status", f"🟠 {allocated_pct:.0f}%", delta="Deploying", delta_color="off")
        elif has_rebalanced:
            if recently_rebalanced:
                st.metric("Status", "✅ Balanced", delta="Optimized", delta_color="normal")
            else:
                st.metric("Status", "Active", delta="Monitoring", delta_color="off")
        else:
            st.metric("Status", "⚪ New", delta="Not rebalanced", delta_color="off")
    
    st.divider()
    
    asset_dict = prof.get("assets", {})
    tickers = list(asset_dict.keys())
    
    if not tickers:
        st.info("👈 **Add your first asset using the sidebar** to start tracking your portfolio")
        st.markdown("""
        ### 📝 Quick Start Guide:
        1. Enter a ticker symbol (e.g., AAPL, MSFT, VTI)
        2. Set your target allocation percentage
        3. See the **buying guide** showing exact units needed
        4. Enter units you currently own
        5. Click **Save Asset**
        """)
        st.stop()
    
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
            
            if not v_t:
                st.error("❌ No valid ticker data found. Please check your asset symbols.")
                st.stop()
            
            if len(v_t) < len(tickers):
                missing = set(tickers) - set(v_t)
                st.warning(f"⚠️ Could not load data for: {', '.join(missing)}")
            
            # Calculate portfolio metrics
            daily_val = data[v_t].apply(
                lambda r: sum(r[t] * asset_dict[t]["units"] for t in v_t if t in r.index),
                axis=1
            )
            
            curr_v = float(daily_val.iloc[-1])
            start_val = float(prof['principal'])
            
            years = max((data.index[-1] - data.index[0]).days / 365.25, 0.01)
            target_val = start_val * (1 + (float(prof['yearly_goal_pct'])/100))**years
            perc_diff = ((curr_v / target_val) - 1) * 100
            roi_pct = ((curr_v / start_val) - 1) * 100
            
            # Calculate CAGR
            prof_start_date = datetime.strptime(prof.get('start_date', str(date.today())), '%Y-%m-%d')
            prof_years = max((date.today() - prof_start_date.date()).days / 365.25, 0.01)
            profile_cagr = ((curr_v / start_val) ** (1 / prof_years) - 1) * 100 if start_val > 0 else 0
            
            # ASSET ALLOCATION: Modified drift detection
            recently_rebalanced = check_recently_rebalanced(prof.get("last_rebalanced"))
            needs_rebalance = False
            drift_assets = []
            
            # Only check drift if fully allocated
            if is_fully_allocated and not recently_rebalanced:
                for t in v_t:
                    actual_pct = float((asset_dict[t]["units"] * data[t].iloc[-1] / curr_v * 100))
                    target_pct = float(asset_dict[t]["target"])
                    drift = float(abs(actual_pct - target_pct))
                    
                    if drift >= prof.get("drift_tolerance", 5.0):
                        needs_rebalance = True
                        drift_assets.append((t, drift, actual_pct, target_pct))
            
            # Drift alert banner
            if needs_rebalance:
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                                border: 4px solid #ef4444; border-radius: 16px; padding: 28px; 
                                margin-bottom: 28px;">
                        <h2 style="color: #991b1b; margin: 0 0 16px 0; font-size: 1.8rem;">
                            🚨 DRIFT ALERT: Immediate Rebalancing Required
                        </h2>
                        <p style="color: #7f1d1d; font-size: 1.2rem; margin: 0; line-height: 1.6;">
                            <strong>{len(drift_assets)} asset(s)</strong> have exceeded your <strong>{prof.get('drift_tolerance', 5.0)}% drift tolerance</strong>.<br>
                            Your portfolio allocation has shifted significantly. Review the analysis below and execute rebalancing.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📊 Assets Requiring Rebalancing:")
                for ticker, drift, actual, target in drift_assets:
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        st.markdown(f"**{ticker}**")
                    with col2:
                        st.markdown(f"Drift: **{drift:.2f}%** ⚠️")
                    with col3:
                        st.markdown(f"Current: **{actual:.1f}%** (Target: {target:.1f}%)")
                
                st.divider()
            
            # Determine status badge
            has_rebalanced = prof.get("last_rebalanced") is not None
            has_assets = len(asset_dict) > 0
            
            if not is_fully_allocated:
                alert_html = '<span style="background: #f97316; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">⚠️ DEPLOYING</span>'
            elif not has_rebalanced and has_assets:
                alert_html = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            elif not has_rebalanced:
                alert_html = '<span style="background: #94a3b8; color: white; padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">⚪ Not Rebalanced</span>'
            elif recently_rebalanced:
                alert_html = '<span class="success-badge">✅ Balanced</span>'
            elif needs_rebalance:
                alert_html = '<span class="drift-badge">🚨 REBALANCE REQUIRED</span>'
            else:
                alert_html = '<span class="success-badge">✅ Balanced</span>'
            
            # Header
            st.markdown(f"""
                <div class="premium-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <h2 style="margin:0;">Portfolio Analytics</h2>
                        {alert_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Key Metrics
            col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
            
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
                        <div class="stat-label">vs. Goal</div>
                        <div class="stat-value" style="color: {'#10b981' if perc_diff >= 0 else '#ef4444'};">
                            {perc_diff:+.1f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s4:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">CAGR</div>
                        <div class="stat-value" style="color: {'#10b981' if profile_cagr >= 0 else '#ef4444'};">
                            {profile_cagr:.2f}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_s5:
                st.markdown(f"""
                    <div class="stat-item">
                        <div class="stat-label">Principal</div>
                        <div class="stat-value">${start_val:,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # ASSET ALLOCATION: New Allocation Table
            st.markdown("### 📊 Asset Allocation Table")
            st.caption("Comprehensive view of target weights, actual allocations, and deployment status")
            
            allocation_rows = []
            for t in v_t:
                current_price = float(data[t].iloc[-1])
                asset_data = asset_dict[t]
                
                # Target and actual percentages
                tar_pct = float(asset_data['target'])
                cur_units = float(asset_data["units"])
                act_val = cur_units * current_price
                act_pct = (act_val / curr_v * 100) if curr_v > 0 else 0
                
                # Allocated percentage (from purchases)
                allocated_pct_asset = sum(
                    p.get("allocated_pct", 0) 
                    for p in asset_data.get("purchases", [])
                )
                
                # Average cost (only if fully allocated)
                avg_cost = calculate_average_cost(asset_data, allocated_pct)
                avg_cost_display = f"${avg_cost:.2f}" if avg_cost is not None else "Pending"
                
                # Drift
                drift = act_pct - tar_pct
                drift_display = f"{drift:+.2f}%" if is_fully_allocated else "-"
                
                allocation_rows.append({
                    "Ticker": t,
                    "Target %": f"{tar_pct:.2f}%",
                    "Actual %": f"{act_pct:.2f}%",
                    "Allocated %": f"{allocated_pct_asset:.2f}%",
                    "Avg Cost": avg_cost_display,
                    "Current Price": f"${current_price:.2f}",
                    "Drift %": drift_display
                })
            
            df_allocation = pd.DataFrame(allocation_rows)
            st.dataframe(df_allocation, use_container_width=True, hide_index=True)
            
            if not is_fully_allocated:
                st.info(f"ℹ️ **Average Cost** and **Drift %** will be calculated after 100% capital deployment. Current: {allocated_pct:.1f}%")
            
            st.divider()
            
            # Performance Chart
            st.markdown("### 📈 Performance Chart")
            st.caption("Historical portfolio value vs. initial investment")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_val.index,
                y=daily_val.values,
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#3b82f6', width=3),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=daily_val.index,
                y=[start_val] * len(daily_val),
                mode='lines',
                name='Initial Investment',
                line=dict(color='#64748b', width=2, dash='dash')
            ))
            
            # Add benchmark if selected
            if prof.get('benchmark'):
                try:
                    benchmark_ticker = prof['benchmark']
                    bench_data = yf.download(benchmark_ticker, start=prof["start_date"], auto_adjust=True, progress=False)
                    
                    if not bench_data.empty:
                        bench_close = bench_data['Close']
                        if isinstance(bench_close, pd.DataFrame):
                            bench_close = bench_close.iloc[:, 0]
                        
                        bench_start = bench_close.iloc[0]
                        bench_normalized = (bench_close / bench_start) * start_val
                        
                        fig.add_trace(go.Scatter(
                            x=bench_normalized.index,
                            y=bench_normalized.values,
                            mode='lines',
                            name=f'{benchmark_ticker} (100%)',
                            line=dict(color='#f59e0b', width=2, dash='dot')
                        ))
                except:
                    pass
            
            fig.update_layout(
                title=None,
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter, sans-serif'),
                height=500,
                margin=dict(t=20, b=40, l=60, r=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
            
            st.plotly_chart(fig, use_container_width=True)
            
            if prof.get('benchmark'):
                st.markdown(f"""
                    <div class="benchmark-note">
                        <strong>📊 Benchmark Note:</strong> The {prof['benchmark']} line shows what would happen if you invested 100% of your principal 
                        (${start_val:,.0f}) in {prof['benchmark']} on {prof['start_date']} and held it. This comparison helps evaluate 
                        whether your asset allocation strategy is outperforming passive investment.
                    </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Rebalance Analysis
            st.markdown("### ⚖️ Rebalance Analysis")
            st.caption("Review asset allocation drift and required trades to restore target percentages")
            with st.expander("ℹ️ Understanding the rebalance table", expanded=False):
                st.markdown("""
                **This table shows what trades are needed** to restore your target allocation.
                
                - **Drift**: 🔴 Red = exceeds tolerance, 🟡 Yellow = warning, 🟢 Green = good
                - **Buy/Sell**: Action needed to rebalance
                - **Buy/Sell Amt**: Dollar value of the trade
                - **Buy/Sell Shares**: Exact number of shares to trade
                
                💡 Execute rebalancing when you see 🔴 red drift indicators
                """)
            
            rows = []
            total_turnover = 0
            total_current_val = 0
            
            for t in v_t:
                current_price = float(data[t].iloc[-1])
                try:
                    prev_price = float(data[t].iloc[-2])
                    daily_change_pct = ((current_price / prev_price) - 1) * 100
                except:
                    daily_change_pct = 0.0
                
                ticker_name = t
                try:
                    ticker_obj = yf.Ticker(t)
                    info = ticker_obj.info
                    if info and 'longName' in info:
                        ticker_name = info.get('longName', t)
                except:
                    pass
                
                cur_u = float(asset_dict[t]["units"])
                tar_w = float(asset_dict[t]['target'])
                
                act_val = cur_u * current_price
                act_w = (act_val / curr_v * 100)
                drift = act_w - tar_w
                
                tar_val = (tar_w / 100) * curr_v
                tar_u = tar_val / current_price
                
                val_diff = tar_val - act_val
                unit_diff = tar_u - cur_u
                
                total_turnover += abs(val_diff)
                total_current_val += act_val
                
                if abs(drift) < 0.1:
                    action = "—"
                else:
                    action = "BUY" if drift < 0 else "SELL"
                
                # ASSET ALLOCATION: Only show drift colors if fully allocated
                if is_fully_allocated:
                    if abs(drift) >= prof.get("drift_tolerance", 5.0):
                        drift_display = f"🔴 {drift:+.2f}%"
                    elif abs(drift) > 0.5:
                        drift_display = f"🟡 {drift:+.2f}%"
                    else:
                        drift_display = f"🟢 {drift:+.2f}%"
                else:
                    drift_display = f"{drift:+.2f}%"
                
                daily_change_display = f"{daily_change_pct:+.2f}%"
                
                rows.append({
                    "Asset Class": ticker_name,
                    "Fund": t,
                    "Units": f"{cur_u:.0f}",
                    "Unit Value": f"${current_price:.2f}",
                    "%Daily Change": daily_change_display,
                    "Amount": f"${act_val:,.0f}",
                    "Allocation": f"{act_w:.2f}%",
                    "Target": f"{tar_w:.2f}%",
                    "Drift": drift_display,
                    "Buy/Sell Amt": f"${abs(val_diff):,.0f}",
                    "Buy/Sell Shares": f"{unit_diff:+.0f}"
                })
            
            # Total row
            rows.append({
                "Asset Class": "**TOTAL**",
                "Fund": "",
                "Units": "",
                "Unit Value": "",
                "%Daily Change": "",
                "Amount": f"**${total_current_val:,.0f}**",
                "Allocation": "**100.00%**",
                "Target": "**100.00%**",
                "Drift": "—",
                "Buy/Sell Amt": f"**${total_turnover:,.0f}**",
                "Buy/Sell Shares": "—"
            })
            
            df_rebalance = pd.DataFrame(rows)
            st.dataframe(df_rebalance, use_container_width=True, hide_index=True)
            
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric("CAGR", f"{profile_cagr:.2f}%", help="Compound Annual Growth Rate")
            with col_metric2:
                st.metric("Total Trade Volume", f"${total_turnover:,.0f}", help="Total dollar amount needed to rebalance")
            
            st.divider()
            
            # Execution
            col_exec1, col_exec2 = st.columns(2)
            
            with col_exec1:
                st.markdown("### 🚀 Execute Rebalance")
                st.caption("Adjust portfolio units to match target allocation")
                with st.expander("ℹ️ What happens when you rebalance?", expanded=False):
                    st.markdown("""
                    **Rebalancing** updates your portfolio to match target allocations.
                    
                    - Unit counts are automatically adjusted
                    - Status changes to ✅ **Balanced** 
                    - 24-hour grace period before drift checking resumes
                    - All trades are logged in the history below
                    
                    ⚠️ **Note:** This updates the app—you must execute trades manually in your brokerage
                    """)
                
                # ASSET ALLOCATION: Modified rebalance button logic
                rebalance_disabled = not needs_rebalance or not is_fully_allocated
                
                if not is_fully_allocated:
                    st.info(f"ℹ️ Rebalancing available after 100% deployment (current: {allocated_pct:.1f}%)")
                elif needs_rebalance:
                    st.warning("⚠️ **Rebalancing recommended**")
                
                if st.button("⚡ Execute Rebalancing", type="primary", use_container_width=True, disabled=rebalance_disabled):
                    detail_log = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} - "
                    changes = []
                    
                    for t in v_t:
                        old_units = float(asset_dict[t]["units"])
                        new_units = float((asset_dict[t]["target"] / 100 * curr_v) / data[t].iloc[-1])
                        asset_dict[t]["units"] = new_units
                        
                        change_val = new_units - old_units
                        if abs(change_val) > 0.0001:
                            action_color = "🟢" if change_val > 0 else "🔴"
                            action_text = "BUY" if change_val > 0 else "SELL"
                            changes.append(f"{action_color} {t} {action_text} {abs(change_val):.4f}")
                    
                    detail_log += ", ".join(changes) if changes else "No changes needed"
                    
                    prof.setdefault("rebalance_stats", []).insert(0, detail_log)
                    prof["rebalance_stats"] = prof["rebalance_stats"][:50]
                    prof["last_rebalanced"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    log_profile(prof, "Portfolio rebalanced to target allocations - Status: Balanced")
                    save_db(st.session_state.db)
                    
                    st.success("✅ Portfolio rebalanced successfully! Status: **Balanced** ✅")
                    st.balloons()
                    st.rerun()
                
                if not needs_rebalance and is_fully_allocated:
                    st.info("✓ Portfolio is optimally balanced")
            
            with col_exec2:
                st.markdown("### 💡 Quick Actions")
                st.caption("Helpful shortcuts and information")
                
                st.markdown("#### 📋 Current Status")
                if not is_fully_allocated:
                    st.warning(f"🟠 **Deploying** ({allocated_pct:.0f}% of capital)")
                elif recently_rebalanced:
                    st.success("✅ **Balanced** (within 24 hours)")
                elif not needs_rebalance:
                    st.success("✅ **Balanced** (all assets within tolerance)")
                elif needs_rebalance:
                    st.warning("⚠️ **Rebalancing needed**")
                else:
                    st.info("⚪ **Not yet rebalanced**")
                
                st.divider()
                
                st.markdown("#### 🎯 Quick Tips")
                st.caption("• Check drift alerts regularly")
                st.caption("• Rebalance when assets exceed tolerance")
                st.caption("• Review Activity Log in sidebar")
                st.caption("• Compare against benchmark below")
                
                st.divider()
                
                st.markdown("#### 📞 Need Help?")
                st.caption("View section descriptions (ℹ️ icons)")
                st.caption("Check rebalance history at bottom")
        
        except Exception as e:
            st.error(f"❌ Error analyzing portfolio: {str(e)}")
            st.info("💡 Please check your internet connection and verify all ticker symbols are valid.")
    
    # Rebalance History at Bottom (organized by time period)
    if tickers and st.session_state.active_profile:
        prof = st.session_state.db["profiles"][st.session_state.active_profile]
        rebalance_events = prof.get('rebalance_stats', [])
        
        if rebalance_events:
            st.divider()
            st.markdown("### 📜 Rebalancing History")
            st.caption("Complete log of all portfolio adjustments")
            
            with st.expander("📋 View Full History", expanded=False):
                for idx, event in enumerate(rebalance_events, 1):
                    st.caption(f"**{idx}.** {event}")

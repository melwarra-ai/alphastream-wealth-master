# 🛡️ AlphaStream Wealth Master

**Production-Ready Portfolio Management & Rebalancing Application**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

## 🎯 Overview

AlphaStream Wealth Master is an institutional-grade portfolio management application designed for individual investors who want to manage multiple investment strategies with precision and discipline.

## ✨ Key Features

- 📊 **Multi-Portfolio Management** - Track multiple investment strategies simultaneously
- ⚖️ **Drift Detection** - Automatic alerts when assets deviate from target allocation
- 📈 **Performance Tracking** - Real-time portfolio valuation vs. target growth path
- 🔄 **Smart Rebalancing** - Automated calculations for restoring portfolio balance
- 🌍 **Multi-Currency Support** - USD 🇺🇸 and CAD 🇨🇦
- 📜 **Activity Logging** - Complete audit trail of all portfolio changes

## 🚀 Live Demo

👉 **[Launch App](https://your-app.streamlit.app)** (Update this link after deployment)

## 📖 How to Use

### 1. Create a Profile
- Click "🆕 Create New Profile" in the sidebar
- Enter profile name, currency, principal, and growth goal
- Click "🚀 Initialize Profile"

### 2. Add Assets
- Select your profile from the dropdown
- Enter a ticker symbol (e.g., AAPL, MSFT, VTI)
- Set target allocation percentage
- Enter units owned
- Use the **Buying Guide** to see how many units you need

### 3. Monitor & Rebalance
- Watch for drift alerts when assets deviate from target
- Review the rebalance preview table
- Click "⚡ Execute Rebalancing Now" to update portfolio

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Source**: Yahoo Finance (yfinance)
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Storage**: JSON file-based persistence

## 🔒 Data Privacy

All portfolio data is stored locally in `alphastream_wealth.json`. No data is sent to external servers except for fetching real-time stock prices from Yahoo Finance.

## ⚠️ Disclaimer

This application is for informational and educational purposes only. It is not financial advice. Always consult with a qualified financial advisor before making investment decisions.

---

**Built with ❤️ for disciplined investors**

# Financial Data Analysis & Dashboard (2020-2024)

This repository contains daily returns data and an interactive dashboard for analyzing financial assets and currency pairs from January 1, 2020 to December 31, 2024.

## 📊 Interactive Dashboard

**🌐 [View Live Dashboard](https://tatsuru-kikuchi.github.io/MCP/)**

The dashboard provides real-time visualizations and analysis of:

### Traditional Assets
- **S&P 500** (^GSPC) - US stock market benchmark
- **Gold** (GC=F) - Precious metals commodity

### Cryptocurrencies
- **Bitcoin** (BTC-USD) - Leading cryptocurrency
- **Ethereum** (ETH-USD) - Second-largest cryptocurrency
- **XRP** (XRP-USD) - Digital payment cryptocurrency

### Currency Pairs & Indices
- **JPY/USD** (JPY=X) - Japanese Yen to US Dollar exchange rate
- **EUR/USD** (EURUSD=X) - Euro to US Dollar exchange rate
- **USD Index** (DX-Y.NYB) - US Dollar strength index

### Dashboard Features

- 📈 **Cumulative Returns Charts** - Track performance over time
- 📊 **Volatility Analysis** - Rolling 30-day volatility tracking
- 🎯 **Risk-Return Profiles** - Scatter plot analysis
- 🔗 **Correlation Matrix** - Asset correlation analysis with color coding
- 💱 **Currency Analysis** - Exchange rate trends and correlations
- 🏷️ **Asset Filtering** - View by category (Traditional, Crypto, Currencies)
- 📱 **Responsive Design** - Works on desktop and mobile
- ⏱️ **Time Period Filtering** - View data for different periods

## 📁 Data Files

### Individual Asset Files
- `SP500_daily_returns_2020_2024.csv` - S&P 500 daily returns
- `Gold_daily_returns_2020_2024.csv` - Gold futures daily returns
- `BTC_daily_returns_2020_2024.csv` - Bitcoin daily returns
- `ETH_daily_returns_2020_2024.csv` - Ethereum daily returns
- `XRP_daily_returns_2020_2024.csv` - XRP daily returns
- `JPY_USD_daily_returns_2020_2024.csv` - JPY/USD exchange rate returns
- `EUR_USD_daily_returns_2020_2024.csv` - EUR/USD exchange rate returns
- `USD_Index_daily_returns_2020_2024.csv` - USD Index returns

### Combined Data
- `all_assets_daily_returns_2020_2024.csv` - All assets in one file
- `all_assets_daily_returns_with_currencies_2020_2024.csv` - Extended dataset with currency pairs

### Summary Statistics & Analysis
- `returns_summary.json` - Summary statistics for all assets
- `returns_summary_with_currencies.json` - Extended summary including currencies
- `correlation_matrix_with_currencies.csv` - Correlation analysis
- `currency_specific_analysis.json` - Detailed currency pair analysis

## 📋 Data Format

Each CSV file contains:
- **Date**: Trading date (YYYY-MM-DD)
- **Close**: Closing price for that day
- **Daily_Return**: Percentage return from previous day (in %)

## 🔧 Scripts & Tools

### Data Collection
- `fetch_financial_data.py` - Main data fetcher with comprehensive analysis (updated with currencies)
- `fetch_returns_data.py` - Enhanced returns data fetcher with currency analysis
- `collect_daily_returns.py` - Comprehensive data collection including all assets

### Analysis & Visualization
- `create_visualizations.py` - Generate charts and analysis plots
- `daily_returns_analysis.ipynb` - Jupyter notebook for detailed analysis

### Automation
- `run_data_collection.bat` / `run_data_collection.sh` - Automated data collection scripts

## 🚀 Quick Start

### View the Dashboard
Simply visit: **[https://tatsuru-kikuchi.github.io/MCP/](https://tatsuru-kikuchi.github.io/MCP/)**

### Run Data Collection
```bash
# Clone the repository
git clone https://github.com/Tatsuru-Kikuchi/MCP.git
cd MCP

# Install dependencies
pip install -r requirements.txt

# Fetch latest data (including currencies)
python fetch_financial_data.py

# Or use the enhanced script for detailed currency analysis
python fetch_returns_data.py

# Create visualizations
python create_visualizations.py
```

## 📦 Requirements

- Python 3.7+
- yfinance
- pandas
- numpy
- matplotlib
- seaborn

## 📥 Installation

```bash
pip install -r requirements.txt
```

## 📊 Data Source

All data is fetched from **Yahoo Finance** using the `yfinance` Python library, ensuring reliable and up-to-date financial information.

## 💱 Currency Data Notes

- **JPY/USD**: Shows how many Japanese Yen equal 1 US Dollar (higher values = stronger USD)
- **EUR/USD**: Shows the Euro to US Dollar exchange rate
- **USD Index**: Measures USD strength against a basket of major currencies (EUR, JPY, GBP, CAD, SEK, CHF)

The currency data helps analyze:
- International market relationships
- Currency impact on asset returns
- Diversification benefits across different currency exposures

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This data is provided for research and educational purposes only. It should not be used as the sole basis for investment decisions. Always consult with financial professionals before making investment choices.

---

**📈 [Access the Interactive Dashboard](https://tatsuru-kikuchi.github.io/MCP/) | 🔧 [Explore the Code](https://github.com/Tatsuru-Kikuchi/MCP)**
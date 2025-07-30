# Financial MCP - PyPI Package

[![PyPI version](https://badge.fury.io/py/financial-mcp.svg)](https://badge.fury.io/py/financial-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/financial-mcp.svg)](https://pypi.org/project/financial-mcp/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A comprehensive Python package for financial data analysis and visualization. Fetch, analyze, and visualize financial data for stocks, cryptocurrencies, and currency pairs from Yahoo Finance.

## 🚀 Quick Start

### Installation

```bash
pip install financial-mcp
```

### Basic Usage

```python
from financial_mcp import fetch_financial_data, analyze_returns, create_visualizations

# Fetch financial data
all_data, daily_returns = fetch_financial_data()

# Analyze the data
analysis_results = analyze_returns(daily_returns_df)

# Create visualizations
create_visualizations(daily_returns_df)
```

### Command Line Interface

```bash
# Fetch data
financial-mcp-fetch

# Analyze data
financial-mcp-analyze

# Create visualizations
financial-mcp-visualize
```

## 📊 Features

### Supported Assets

- **Traditional Assets**: S&P 500, Gold
- **Cryptocurrencies**: Bitcoin, Ethereum, XRP
- **Currency Pairs**: JPY/USD, EUR/USD, USD Index

### Analysis Capabilities

- ✅ **Daily Returns Calculation**: Percentage changes in asset prices
- ✅ **Statistical Analysis**: Mean, volatility, Sharpe ratio, skewness, kurtosis
- ✅ **Risk Metrics**: Value at Risk (VaR), Conditional VaR, Maximum Drawdown
- ✅ **Correlation Analysis**: Asset correlation matrices and insights
- ✅ **Performance Metrics**: Annualized returns and volatility

### Visualization Tools

- 📈 **Cumulative Returns Charts**: Track performance over time
- 📊 **Volatility Analysis**: Rolling volatility tracking
- 🎯 **Risk-Return Profiles**: Scatter plot analysis
- 🔗 **Correlation Heatmaps**: Asset correlation visualization
- 📊 **Distribution Analysis**: Returns distribution plots

## 📁 Package Structure

```
financial_mcp/
├── __init__.py          # Package initialization
├── fetch_data.py        # Data fetching from Yahoo Finance
├── analyze.py           # Financial analysis functions
├── visualize.py         # Visualization creation
└── utils.py            # Utility functions
```

## 🔧 API Reference

### Data Fetching

```python
from financial_mcp import fetch_financial_data, save_data_to_csv

# Fetch data for default assets
all_data, daily_returns = fetch_financial_data(
    start_date='2020-01-01',
    end_date='2024-12-31'
)

# Save to CSV files
combined_df = save_data_to_csv(all_data, daily_returns)
```

### Analysis

```python
from financial_mcp import analyze_returns, calculate_correlation_matrix, calculate_risk_metrics

# Comprehensive returns analysis
analysis_results = analyze_returns(daily_returns_df)

# Correlation analysis
correlation_matrix = calculate_correlation_matrix(daily_returns_df)

# Risk metrics calculation
risk_metrics = calculate_risk_metrics(daily_returns_df)
```

### Visualization

```python
from financial_mcp import create_visualizations
from financial_mcp.visualize import (
    create_returns_plot,
    create_correlation_heatmap,
    create_volatility_plot,
    create_risk_return_scatter,
    create_distribution_plots
)

# Create all visualizations
create_visualizations(daily_returns_df, correlation_matrix)

# Or create individual plots
create_returns_plot(daily_returns_df)
create_correlation_heatmap(correlation_matrix)
```

## 🎯 Example: Complete Workflow

```python
import pandas as pd
from financial_mcp import (
    fetch_financial_data,
    save_data_to_csv,
    analyze_returns,
    calculate_correlation_matrix,
    create_visualizations
)

# 1. Fetch data
print("Fetching financial data...")
all_data, daily_returns = fetch_financial_data(
    start_date='2020-01-01',
    end_date='2024-12-31'
)

# 2. Save to CSV
print("Saving data...")
combined_returns = save_data_to_csv(all_data, daily_returns)

# 3. Analyze data
print("Analyzing returns...")
analysis_results = analyze_returns(combined_returns)
correlation_matrix = calculate_correlation_matrix(combined_returns)

# 4. Create visualizations
print("Creating visualizations...")
create_visualizations(combined_returns, correlation_matrix)

# 5. Print summary
print(f"\nAnalysis complete!")
print(f"Assets analyzed: {list(combined_returns.columns)}")
print(f"Date range: {combined_returns.index.min()} to {combined_returns.index.max()}")
print(f"Total observations: {len(combined_returns)}")
```

## 📦 Requirements

- Python 3.7+
- pandas >= 2.0.0
- numpy >= 1.24.0
- yfinance >= 0.2.28
- matplotlib >= 3.5.0
- seaborn >= 0.12.0
- scipy >= 1.10.0

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/Tatsuru-Kikuchi/MCP/blob/main/LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- 📊 **Live Dashboard**: [https://tatsuru-kikuchi.github.io/MCP/](https://tatsuru-kikuchi.github.io/MCP/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Tatsuru-Kikuchi/MCP/issues)
- 📚 **Documentation**: [GitHub Repository](https://github.com/Tatsuru-Kikuchi/MCP)

## ⚠️ Disclaimer

This package is provided for research and educational purposes only. It should not be used as the sole basis for investment decisions. Always consult with financial professionals before making investment choices.

---

**📈 [Try the Live Dashboard](https://tatsuru-kikuchi.github.io/MCP/) | 🔧 [View Source Code](https://github.com/Tatsuru-Kikuchi/MCP)**

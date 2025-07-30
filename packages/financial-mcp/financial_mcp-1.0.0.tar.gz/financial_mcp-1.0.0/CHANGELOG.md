# Changelog

All notable changes to the Financial MCP project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-07

### Added
- Initial PyPI package release
- Core financial data fetching functionality from Yahoo Finance
- Support for multiple asset classes:
  - Traditional assets (S&P 500, Gold)
  - Cryptocurrencies (Bitcoin, Ethereum, XRP)
  - Currency pairs (JPY/USD, EUR/USD, USD Index)
- Comprehensive financial analysis features:
  - Daily returns calculation
  - Statistical analysis (mean, volatility, Sharpe ratio, skewness, kurtosis)
  - Risk metrics (VaR, CVaR, Maximum Drawdown)
  - Correlation analysis
- Visualization capabilities:
  - Cumulative returns charts
  - Volatility analysis plots
  - Risk-return scatter plots
  - Correlation heatmaps
  - Distribution analysis charts
- Command-line interface (CLI) tools:
  - `financial-mcp-fetch` for data collection
  - `financial-mcp-analyze` for analysis
  - `financial-mcp-visualize` for chart generation
- Comprehensive test suite with pytest
- GitHub Actions CI/CD pipeline
- Automatic PyPI publishing workflow
- Type hints and documentation
- Utility functions for asset management
- Modular package structure for easy extension

### Features
- **Data Sources**: Yahoo Finance integration via yfinance
- **Date Range**: Configurable date ranges with validation
- **Export Formats**: CSV, JSON support for analysis results
- **Plotting**: High-quality matplotlib/seaborn visualizations
- **Risk Analysis**: Professional-grade risk metrics
- **Performance**: Optimized for large datasets
- **Error Handling**: Robust error handling and logging
- **Documentation**: Comprehensive API documentation

### Technical Details
- **Python Support**: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12
- **Dependencies**: pandas, numpy, yfinance, matplotlib, seaborn, scipy
- **Package Structure**: Modular design with clear separation of concerns
- **Testing**: Unit tests with >90% coverage
- **Code Quality**: Black formatting, type hints, docstrings

---

**Note**: This is the initial release of the Financial MCP package on PyPI. The package consolidates and enhances the existing financial analysis tools from the MCP repository into a professional Python package suitable for distribution and use in other projects.

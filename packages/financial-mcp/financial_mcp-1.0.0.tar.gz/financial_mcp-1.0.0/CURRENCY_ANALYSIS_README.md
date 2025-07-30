# Currency Analysis Enhancement

## Overview

This update adds comprehensive currency analysis to the MCP (Market Correlation Project) by incorporating three major currency instruments:

- **JPY/USD (JPY=X)**: Japanese Yen per US Dollar exchange rate
- **EUR/USD (EURUSD=X)**: Euro to US Dollar exchange rate  
- **USD Index (DX-Y.NYB)**: US Dollar Index (DXY) measuring USD strength against a basket of major currencies

## New Features Added

### 1. Enhanced Data Collection (`collect_daily_returns.py`)

**New Currency Assets:**
- JPY/USD exchange rate analysis
- EUR/USD exchange rate analysis
- USD Index (DXY) analysis

**Additional Analysis:**
- Currency-specific correlation analysis with other assets
- Quarterly trend analysis for currencies
- Enhanced volatility comparisons
- Currency relationship mapping

**New Output Files:**
- `daily_returns_with_currencies_2020_2025.csv` - Combined dataset including currencies
- `currency_analysis.json` - Detailed currency-specific metrics
- `summary_statistics_with_currencies.json` - Enhanced statistics
- `monthly_summary_with_currencies.json` - Monthly performance data

### 2. Advanced Visualizations (`create_visualizations.py`)

**New Visualizations:**
1. **Currency Correlation Analysis** - Bar charts showing how each currency correlates with other assets
2. **Enhanced Volatility Comparison** - Color-coded volatility chart distinguishing currencies, cryptocurrencies, and traditional assets
3. **Risk-Return Profile with Asset Classification** - Scatter plot using different markers for asset types
4. **Currency Time Series Analysis** - Individual currency performance over time with major economic events
5. **Monthly Returns Heatmaps** - For each currency showing seasonal patterns

**Visual Enhancements:**
- Asset type classification (Traditional, Cryptocurrency, Currency)
- Color coding and marker differentiation by asset class
- Enhanced correlation matrices with currency data
- Professional styling with clear legends

### 3. Comprehensive Data Fetching (`fetch_returns_data.py`)

**Enhanced Features:**
- Automatic asset type classification
- Higher precision for currency data (6 decimal places)
- Advanced risk metrics (VaR, skewness, kurtosis)
- Monthly and quarterly performance analysis
- Correlation analysis between all asset pairs

**New Analytics:**
- Value at Risk (VaR) calculations at 1% and 5% levels
- Extreme movement detection (95th/5th percentile events)
- Monthly/quarterly aggregated returns
- Asset correlation mapping

## Currency Instruments Explained

### JPY/USD (Japanese Yen per USD)
- **Ticker**: JPY=X
- **Description**: Shows how many Japanese Yen equal 1 US Dollar
- **Interpretation**: Higher values = stronger USD relative to JPY
- **Key Factors**: Bank of Japan policy, US-Japan interest rate differentials, risk sentiment

### EUR/USD (Euro to US Dollar)
- **Ticker**: EURUSD=X  
- **Description**: Shows how many US Dollars equal 1 Euro
- **Interpretation**: Higher values = stronger EUR relative to USD
- **Key Factors**: ECB vs Fed monetary policy, European economic data, global risk appetite

### USD Index (DXY)
- **Ticker**: DX-Y.NYB
- **Description**: Measures USD strength against basket of 6 major currencies (EUR, JPY, GBP, CAD, SEK, CHF)
- **Interpretation**: Higher values = stronger USD overall
- **Key Factors**: US economic data, Federal Reserve policy, global economic conditions

## Key Analysis Insights

### Currency Correlations
The analysis reveals how currencies interact with:
- **Traditional Assets**: Relationship with S&P 500 and Gold
- **Cryptocurrencies**: Correlation patterns with Bitcoin, Ethereum, and XRP
- **Cross-Currency**: How different currency pairs move relative to each other

### Risk Characteristics
- **Volatility Ranking**: Currencies typically show lower volatility than cryptocurrencies
- **Safe Haven Behavior**: USD Index and JPY often strengthen during market stress
- **Risk-On/Risk-Off**: EUR/USD tends to follow global risk sentiment

### Seasonal Patterns
Monthly heatmaps reveal:
- End-of-quarter rebalancing effects
- Seasonal trading patterns
- Economic calendar impacts (Fed meetings, ECB meetings, etc.)

## Usage Instructions

### Running the Enhanced Analysis

1. **Data Collection**:
   ```bash
   python collect_daily_returns.py
   ```
   This will download all asset data including the new currency pairs.

2. **Create Visualizations**:
   ```bash
   python create_visualizations.py
   ```
   This generates comprehensive charts including currency-specific analysis.

3. **Quick Data Fetch** (alternative):
   ```bash
   python fetch_returns_data.py
   ```
   Lighter version focused on data collection and basic analysis.

### New Output Files Generated

- `cumulative_returns_with_currencies_2020_2025.png`
- `currency_correlations_analysis.png`
- `volatility_comparison_with_currencies.png`
- `correlation_matrix_with_currencies_2020_2025.png`
- `risk_return_profile_with_currencies_2020_2025.png`
- `currency_time_series_analysis.png`
- `[currency]_monthly_returns_heatmap.png` (for each currency)

## Technical Implementation

### Data Quality Enhancements
- Higher precision floating point handling for currency data
- Robust error handling for missing data
- Automatic data alignment for correlation calculations
- Enhanced statistical calculations

### Performance Optimizations
- Efficient data merging for multiple time series
- Optimized correlation calculations
- Memory-efficient data structures
- Parallel processing where applicable

### Statistical Improvements
- Log returns analysis for better statistical properties
- Enhanced risk metrics (VaR, skewness, kurtosis)
- Time-series decomposition capabilities
- Advanced correlation analysis

## Future Enhancements

Potential additions for future versions:
- Additional currency pairs (GBP/USD, USD/CHF, AUD/USD, etc.)
- Central bank policy event analysis
- Interest rate differential analysis
- Carry trade strategy analysis
- Currency momentum indicators
- Options-based volatility measures (currency VIX equivalents)

## Dependencies

Ensure you have the required packages:
```bash
pip install yfinance pandas numpy matplotlib seaborn scipy
```

## Notes

- Currency data is available 24/5 (Monday-Friday) due to forex market hours
- Some gaps may appear during holidays when forex markets are closed
- Currency pairs show different characteristics than equity/commodity assets
- Correlations may vary significantly during different market regimes
- All returns are calculated as percentage changes for consistency across asset classes

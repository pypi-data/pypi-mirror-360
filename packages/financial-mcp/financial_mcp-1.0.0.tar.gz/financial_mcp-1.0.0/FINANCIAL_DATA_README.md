# Financial Data Analysis: Daily Returns 2021-2024

This repository contains scripts and data for analyzing daily returns of major financial assets from January 1, 2021, to December 31, 2024.

## Assets Included

- **S&P 500 Index** (^GSPC) - US stock market benchmark
- **Gold Futures** (GC=F) - Precious metals commodity
- **Bitcoin** (BTC-USD) - Leading cryptocurrency
- **Ethereum** (ETH-USD) - Second-largest cryptocurrency
- **XRP** (XRP-USD) - Digital payment cryptocurrency

## Data Source

All data is fetched from Yahoo Finance using the `yfinance` Python library. The data includes:
- Daily open, high, low, close prices
- Trading volume
- Adjusted closing prices
- **Daily returns** (calculated as percentage change in closing prices)

## Files Structure

```
financial_data/
├── SP500_daily_data_2021_2024.csv
├── Gold_daily_data_2021_2024.csv
├── Bitcoin_daily_data_2021_2024.csv
├── Ethereum_daily_data_2021_2024.csv
├── XRP_daily_data_2021_2024.csv
├── combined_daily_returns_2021_2024.csv
└── daily_returns_summary_stats.csv
```

## Installation

1. Clone this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the data fetcher script:
```bash
python fetch_financial_data.py
```

This will:
1. Download historical data for all assets
2. Calculate daily returns for each asset
3. Save individual asset data to separate CSV files
4. Create a combined daily returns file
5. Generate summary statistics
6. Display correlation analysis

## Data Format

### Individual Asset Files
Each CSV contains columns:
- `Date` (index)
- `Open` - Opening price
- `High` - Highest price of the day
- `Low` - Lowest price of the day
- `Close` - Closing price
- `Volume` - Trading volume
- `Daily_Return` - Daily percentage return

### Combined Returns File
- `Date` (index)
- `SP500` - S&P 500 daily returns (%)
- `Gold` - Gold daily returns (%)
- `Bitcoin` - Bitcoin daily returns (%)
- `Ethereum` - Ethereum daily returns (%)
- `XRP` - XRP daily returns (%)

## Analysis Features

The script provides:
- **Summary Statistics**: Mean, standard deviation, min/max returns for each asset
- **Volatility Analysis**: Annualized volatility calculations
- **Correlation Matrix**: Cross-asset correlation analysis
- **Data Quality Checks**: Missing data identification and handling

## Key Metrics Calculated

- **Daily Return**: (Price_today - Price_yesterday) / Price_yesterday × 100
- **Annualized Volatility**: Daily volatility × √252 (trading days per year)
- **Correlation Coefficients**: Pearson correlation between asset returns

## Time Period

- **Start Date**: January 1, 2021
- **End Date**: December 31, 2024
- **Frequency**: Daily (business days only)
- **Total Period**: 4 years

## Use Cases

This dataset is suitable for:
- Portfolio risk analysis
- Asset correlation studies
- Volatility modeling
- Cryptocurrency vs traditional asset comparison
- Financial research and backtesting
- Academic studies in finance

## Data Quality Notes

- Cryptocurrency data is available 7 days a week
- Traditional assets (S&P 500, Gold) follow market trading days
- All returns are calculated using adjusted closing prices
- Missing data points are handled appropriately

## Dependencies

- `yfinance`: Yahoo Finance data fetching
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `matplotlib`: Basic plotting capabilities
- `seaborn`: Statistical visualizations

## License

This project is for educational and research purposes. Please refer to Yahoo Finance's terms of use for data usage rights.

## Disclaimer

This data is provided for research and educational purposes only. It should not be used as the sole basis for investment decisions. Always consult with financial professionals before making investment choices.
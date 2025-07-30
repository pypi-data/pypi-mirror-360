"""
Financial Data Fetcher Module

This module provides functionality to fetch financial data from Yahoo Finance
and calculate daily returns for various assets including stocks, cryptocurrencies,
commodities, and currency pairs.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import json
from datetime import datetime
import os

# Default asset symbols
DEFAULT_ASSETS = {
    'traditional': {
        '^GSPC': 'SP500',
        'GC=F': 'Gold'
    },
    'crypto': {
        'BTC-USD': 'BTC',
        'ETH-USD': 'ETH',
        'XRP-USD': 'XRP'
    },
    'currencies': {
        'JPY=X': 'JPY_USD',
        'EURUSD=X': 'EUR_USD',
        'DX-Y.NYB': 'USD_Index'
    }
}

def fetch_financial_data(
    start_date: str = "2020-01-01",
    end_date: str = "2024-12-31",
    assets: Optional[Dict] = None
) -> Tuple[Dict, Dict]:
    """
    Fetch financial data and calculate daily returns
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        assets: Custom asset dictionary, uses DEFAULT_ASSETS if None
        
    Returns:
        Tuple of (all_data_dict, daily_returns_dict)
    """
    if assets is None:
        # Flatten the DEFAULT_ASSETS dictionary
        assets = {}
        for category in DEFAULT_ASSETS.values():
            assets.update(category)
    
    all_data = {}
    daily_returns = {}
    
    print(f"Fetching data from {start_date} to {end_date}")
    print(f"Assets to fetch: {list(assets.keys())}")
    
    for symbol, name in assets.items():
        try:
            print(f"Fetching {name} ({symbol})...")
            
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                print(f"Warning: No data found for {symbol}")
                continue
            
            # Store raw data
            all_data[name] = data
            
            # Calculate daily returns
            returns = data['Close'].pct_change().dropna() * 100  # Convert to percentage
            daily_returns[name] = returns
            
            print(f"✓ Successfully fetched {name}: {len(data)} days of data")
            
        except Exception as e:
            print(f"✗ Error fetching {symbol}: {e}")
            continue
    
    return all_data, daily_returns

def save_data_to_csv(
    all_data: Dict,
    daily_returns: Dict,
    output_dir: str = "financial_data"
) -> None:
    """
    Save fetched data to CSV files
    
    Args:
        all_data: Dictionary of raw price data
        daily_returns: Dictionary of daily returns data
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"\\nSaving data to {output_dir}/")
    
    # Save individual asset files
    for asset_name in daily_returns.keys():
        if asset_name in all_data:
            # Prepare data for saving
            save_data = all_data[asset_name][['Close']].copy()
            save_data['Daily_Return'] = daily_returns[asset_name]
            save_data = save_data.dropna()
            
            # Save to CSV
            filename = f"{asset_name}_daily_returns_2020_2024.csv"
            filepath = output_path / filename
            save_data.to_csv(filepath)
            print(f"✓ Saved {filename}")
    
    # Save combined daily returns
    if daily_returns:
        combined_returns = pd.DataFrame(daily_returns)
        combined_returns.index.name = 'Date'
        
        # Save combined file
        combined_file = output_path / "combined_daily_returns_2020_2024.csv"
        combined_returns.to_csv(combined_file)
        print(f"✓ Saved combined_daily_returns_2020_2024.csv")
        
        # Also save with different naming convention for compatibility
        alt_combined_file = output_path / "all_assets_daily_returns_with_currencies_2020_2024.csv"
        combined_returns.to_csv(alt_combined_file)
        print(f"✓ Saved all_assets_daily_returns_with_currencies_2020_2024.csv")

def calculate_summary_statistics(daily_returns: Dict) -> Dict:
    """
    Calculate summary statistics for daily returns
    
    Args:
        daily_returns: Dictionary of daily returns data
        
    Returns:
        Dictionary of summary statistics
    """
    summary = {}
    
    for asset_name, returns in daily_returns.items():
        if len(returns) > 0:
            summary[asset_name] = {
                'mean_return': float(returns.mean()),
                'std_return': float(returns.std()),
                'min_return': float(returns.min()),
                'max_return': float(returns.max()),
                'skewness': float(returns.skew()),
                'kurtosis': float(returns.kurtosis()),
                'count': int(len(returns)),
                'sharpe_ratio': float(returns.mean() / returns.std()) if returns.std() > 0 else 0.0
            }
    
    return summary

def save_summary_statistics(
    daily_returns: Dict,
    output_dir: str = "financial_data"
) -> None:
    """
    Calculate and save summary statistics
    
    Args:
        daily_returns: Dictionary of daily returns data
        output_dir: Output directory path
    """
    summary = calculate_summary_statistics(daily_returns)
    
    output_path = Path(output_dir)
    summary_file = output_path / "returns_summary_with_currencies.json"
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✓ Saved returns_summary_with_currencies.json")

def main():
    """
    Main function for standalone execution
    """
    print("Financial Data Fetcher")
    print("=" * 50)
    
    # Fetch data
    all_data, daily_returns = fetch_financial_data()
    
    if not daily_returns:
        print("No data was successfully fetched.")
        return
    
    # Save data
    save_data_to_csv(all_data, daily_returns)
    
    # Save summary statistics
    save_summary_statistics(daily_returns)
    
    print("\\n" + "=" * 50)
    print("Data fetching completed successfully!")
    print("=" * 50)
    print(f"Assets fetched: {len(daily_returns)}")
    print(f"Files saved to: financial_data/")

if __name__ == "__main__":
    main()

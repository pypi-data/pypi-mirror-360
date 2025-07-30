"""
Financial Data Analysis Module

This module provides comprehensive analysis functionality for financial data
including correlation analysis, risk metrics, and statistical analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import json
from scipy import stats

def analyze_returns(daily_returns_df: pd.DataFrame) -> Dict:
    """
    Perform comprehensive analysis on daily returns data
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        
    Returns:
        Dictionary containing analysis results
    """
    analysis_results = {}
    
    for asset in daily_returns_df.columns:
        returns = daily_returns_df[asset].dropna()
        
        if len(returns) == 0:
            continue
            
        # Basic statistics
        mean_return = returns.mean()
        std_return = returns.std()
        min_return = returns.min()
        max_return = returns.max()
        
        # Distribution statistics
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        # Risk metrics
        var_95 = returns.quantile(0.05)  # 5% VaR
        var_99 = returns.quantile(0.01)  # 1% VaR
        
        # Performance metrics
        sharpe_ratio = mean_return / std_return if std_return > 0 else 0
        
        # Cumulative returns
        cumulative_return = ((1 + returns / 100).cumprod() - 1).iloc[-1] * 100
        
        # Maximum drawdown
        cumulative_series = (1 + returns / 100).cumprod()
        rolling_max = cumulative_series.expanding().max()
        drawdown = (cumulative_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        # Volatility (annualized)
        annual_volatility = std_return * np.sqrt(252)  # Assuming 252 trading days
        
        analysis_results[asset] = {
            'mean_return': float(mean_return),
            'std_return': float(std_return),
            'annual_volatility': float(annual_volatility),
            'min_return': float(min_return),
            'max_return': float(max_return),
            'skewness': float(skewness),
            'kurtosis': float(kurtosis),
            'var_95': float(var_95),
            'var_99': float(var_99),
            'sharpe_ratio': float(sharpe_ratio),
            'cumulative_return': float(cumulative_return),
            'max_drawdown': float(max_drawdown),
            'count': int(len(returns))
        }
    
    return analysis_results

def calculate_correlation_matrix(daily_returns_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix for all assets
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        
    Returns:
        Correlation matrix DataFrame
    """
    # Remove columns with all NaN values
    cleaned_df = daily_returns_df.dropna(axis=1, how='all')
    
    # Calculate correlation matrix
    correlation_matrix = cleaned_df.corr()
    
    return correlation_matrix

def calculate_risk_metrics(daily_returns_df: pd.DataFrame) -> Dict:
    """
    Calculate various risk metrics for the portfolio
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        
    Returns:
        Dictionary containing risk metrics
    """
    risk_metrics = {}
    
    # Portfolio metrics (equal-weighted portfolio)
    cleaned_df = daily_returns_df.dropna(axis=1, how='all')
    
    if len(cleaned_df.columns) > 1:
        # Equal-weighted portfolio returns
        portfolio_returns = cleaned_df.mean(axis=1)
        
        # Portfolio statistics
        portfolio_mean = portfolio_returns.mean()
        portfolio_std = portfolio_returns.std()
        portfolio_sharpe = portfolio_mean / portfolio_std if portfolio_std > 0 else 0
        
        # Portfolio VaR
        portfolio_var_95 = portfolio_returns.quantile(0.05)
        portfolio_var_99 = portfolio_returns.quantile(0.01)
        
        risk_metrics['portfolio'] = {
            'mean_return': float(portfolio_mean),
            'volatility': float(portfolio_std),
            'sharpe_ratio': float(portfolio_sharpe),
            'var_95': float(portfolio_var_95),
            'var_99': float(portfolio_var_99)
        }
    
    # Individual asset beta (relative to market proxy - first asset)
    if len(cleaned_df.columns) > 1:
        market_proxy = cleaned_df.iloc[:, 0]  # Use first asset as market proxy
        
        betas = {}
        for asset in cleaned_df.columns[1:]:
            asset_returns = cleaned_df[asset]
            
            # Calculate beta using linear regression
            valid_data = pd.concat([market_proxy, asset_returns], axis=1).dropna()
            if len(valid_data) > 1:
                slope, intercept, r_value, p_value, std_err = stats.linregress(
                    valid_data.iloc[:, 0], valid_data.iloc[:, 1]
                )
                betas[asset] = {
                    'beta': float(slope),
                    'alpha': float(intercept),
                    'r_squared': float(r_value ** 2),
                    'p_value': float(p_value)
                }
        
        risk_metrics['betas'] = betas
    
    return risk_metrics

def save_analysis_results(
    analysis_results: Dict,
    correlation_matrix: pd.DataFrame,
    risk_metrics: Dict,
    output_dir: str = "financial_data"
) -> None:
    """
    Save analysis results to files
    
    Args:
        analysis_results: Analysis results dictionary
        correlation_matrix: Correlation matrix DataFrame
        risk_metrics: Risk metrics dictionary
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print(f"\\nSaving analysis results to {output_dir}/")
    
    # Save analysis results
    analysis_file = output_path / "analysis_results.json"
    with open(analysis_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    print(f"✓ Saved analysis_results.json")
    
    # Save correlation matrix
    correlation_file = output_path / "correlation_matrix.csv"
    correlation_matrix.to_csv(correlation_file)
    print(f"✓ Saved correlation_matrix.csv")
    
    # Alternative naming for compatibility
    alt_correlation_file = output_path / "correlation_matrix_with_currencies.csv"
    correlation_matrix.to_csv(alt_correlation_file)
    print(f"✓ Saved correlation_matrix_with_currencies.csv")
    
    # Save risk metrics
    risk_file = output_path / "risk_metrics.json"
    with open(risk_file, 'w') as f:
        json.dump(risk_metrics, f, indent=2)
    print(f"✓ Saved risk_metrics.json")

def load_data(input_dir: str = "financial_data") -> Optional[pd.DataFrame]:
    """
    Load daily returns data from file
    
    Args:
        input_dir: Input directory path
        
    Returns:
        DataFrame with daily returns data or None if not found
    """
    input_path = Path(input_dir)
    
    # Try different file names
    possible_files = [
        "combined_daily_returns_2020_2024.csv",
        "all_assets_daily_returns_with_currencies_2020_2024.csv",
        "all_assets_daily_returns_2020_2024.csv"
    ]
    
    for filename in possible_files:
        filepath = input_path / filename
        if filepath.exists():
            print(f"Loading data from {filename}")
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    print(f"Error: No data file found in {input_dir}")
    print(f"Expected one of: {possible_files}")
    return None

def main():
    """
    Main function for standalone execution
    """
    print("Financial Data Analysis")
    print("=" * 50)
    
    # Load data
    daily_returns_df = load_data()
    if daily_returns_df is None:
        print("Cannot proceed without data. Please run fetch command first.")
        return
    
    print(f"Loaded data for {len(daily_returns_df.columns)} assets")
    print(f"Date range: {daily_returns_df.index.min()} to {daily_returns_df.index.max()}")
    
    # Perform analysis
    print("\\nPerforming analysis...")
    analysis_results = analyze_returns(daily_returns_df)
    correlation_matrix = calculate_correlation_matrix(daily_returns_df)
    risk_metrics = calculate_risk_metrics(daily_returns_df)
    
    # Save results
    save_analysis_results(analysis_results, correlation_matrix, risk_metrics)
    
    print("\\n" + "=" * 50)
    print("Analysis completed successfully!")
    print("=" * 50)
    print(f"Assets analyzed: {len(analysis_results)}")
    print(f"Results saved to: financial_data/")

if __name__ == "__main__":
    main()

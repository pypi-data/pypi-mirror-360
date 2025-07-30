"""
Financial Data Visualization Module

This module provides comprehensive visualization functionality for financial data
including time series plots, correlation heatmaps, and statistical charts.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict
import warnings

# Set style for better-looking plots
plt.style.use('default')
sns.set_palette("husl")
warnings.filterwarnings('ignore')

def create_cumulative_returns_plot(
    daily_returns_df: pd.DataFrame,
    output_dir: str = "plots",
    filename: str = "cumulative_returns.png"
) -> None:
    """
    Create cumulative returns plot for all assets
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        output_dir: Output directory for plots
        filename: Output filename
    """
    plt.figure(figsize=(14, 8))
    
    # Calculate cumulative returns for each asset
    for asset in daily_returns_df.columns:
        returns = daily_returns_df[asset].dropna()
        if len(returns) > 0:
            cumulative_returns = ((1 + returns / 100).cumprod() - 1) * 100
            plt.plot(cumulative_returns.index, cumulative_returns.values, 
                    label=asset, linewidth=2)
    
    plt.title('Cumulative Returns (2020-2024)', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Cumulative Return (%)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    plt.savefig(output_path / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved {filename}")

def create_correlation_heatmap(
    correlation_matrix: pd.DataFrame,
    output_dir: str = "plots",
    filename: str = "correlation_heatmap.png"
) -> None:
    """
    Create correlation heatmap
    
    Args:
        correlation_matrix: Correlation matrix DataFrame
        output_dir: Output directory for plots
        filename: Output filename
    """
    plt.figure(figsize=(12, 10))
    
    # Create heatmap
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                center=0, square=True, linewidths=0.5, cbar_kws={"shrink": .8})
    
    plt.title('Asset Correlation Matrix', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save plot
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    plt.savefig(output_path / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved {filename}")

def create_volatility_plot(
    daily_returns_df: pd.DataFrame,
    output_dir: str = "plots",
    filename: str = "rolling_volatility.png",
    window: int = 30
) -> None:
    """
    Create rolling volatility plot
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        output_dir: Output directory for plots
        filename: Output filename
        window: Rolling window size
    """
    plt.figure(figsize=(14, 8))
    
    # Calculate rolling volatility for each asset
    for asset in daily_returns_df.columns:
        returns = daily_returns_df[asset].dropna()
        if len(returns) > window:
            rolling_vol = returns.rolling(window=window).std()
            plt.plot(rolling_vol.index, rolling_vol.values, 
                    label=asset, linewidth=2)
    
    plt.title(f'{window}-Day Rolling Volatility', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Volatility (%)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    output_path = Path(output_dir)
    plt.savefig(output_path / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved {filename}")

def create_risk_return_scatter(
    daily_returns_df: pd.DataFrame,
    output_dir: str = "plots",
    filename: str = "risk_return_scatter.png"
) -> None:
    """
    Create risk-return scatter plot
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        output_dir: Output directory for plots
        filename: Output filename
    """
    plt.figure(figsize=(12, 8))
    
    # Calculate mean returns and volatility for each asset
    mean_returns = []
    volatilities = []
    asset_names = []
    
    for asset in daily_returns_df.columns:
        returns = daily_returns_df[asset].dropna()
        if len(returns) > 0:
            mean_returns.append(returns.mean())
            volatilities.append(returns.std())
            asset_names.append(asset)
    
    # Create scatter plot
    scatter = plt.scatter(volatilities, mean_returns, s=100, alpha=0.7)
    
    # Add asset labels
    for i, asset in enumerate(asset_names):
        plt.annotate(asset, (volatilities[i], mean_returns[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=10)
    
    plt.title('Risk-Return Profile', fontsize=16, fontweight='bold')
    plt.xlabel('Risk (Volatility %)', fontsize=12)
    plt.ylabel('Expected Return (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    output_path = Path(output_dir)
    plt.savefig(output_path / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved {filename}")

def create_distribution_plots(
    daily_returns_df: pd.DataFrame,
    output_dir: str = "plots",
    filename: str = "return_distributions.png"
) -> None:
    """
    Create distribution plots for returns
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        output_dir: Output directory for plots
        filename: Output filename
    """
    n_assets = len(daily_returns_df.columns)
    n_cols = 3
    n_rows = (n_assets + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1) if n_assets > 1 else [axes]
    
    for i, asset in enumerate(daily_returns_df.columns):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row][col] if n_rows > 1 else axes[col]
        
        returns = daily_returns_df[asset].dropna()
        if len(returns) > 0:
            # Histogram with KDE
            ax.hist(returns, bins=50, density=True, alpha=0.7, color='skyblue')
            ax.axvline(returns.mean(), color='red', linestyle='--', 
                      label=f'Mean: {returns.mean():.2f}%')
            ax.set_title(f'{asset} Return Distribution')
            ax.set_xlabel('Daily Return (%)')
            ax.set_ylabel('Density')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    # Hide empty subplots
    for i in range(n_assets, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row][col].set_visible(False)
    
    plt.tight_layout()
    
    # Save plot
    output_path = Path(output_dir)
    plt.savefig(output_path / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Saved {filename}")

def create_visualizations(
    daily_returns_df: Optional[pd.DataFrame] = None,
    correlation_matrix: Optional[pd.DataFrame] = None,
    output_dir: str = "plots"
) -> None:
    """
    Create all visualizations
    
    Args:
        daily_returns_df: DataFrame with daily returns data
        correlation_matrix: Correlation matrix DataFrame
        output_dir: Output directory for plots
    """
    print(f"\nCreating visualizations in {output_dir}/")
    
    if daily_returns_df is not None:
        # Time series plots
        create_cumulative_returns_plot(daily_returns_df, output_dir)
        create_volatility_plot(daily_returns_df, output_dir)
        
        # Statistical plots
        create_risk_return_scatter(daily_returns_df, output_dir)
        create_distribution_plots(daily_returns_df, output_dir)
    
    if correlation_matrix is not None:
        # Correlation heatmap
        create_correlation_heatmap(correlation_matrix, output_dir)

def load_data_for_visualization(input_dir: str = "financial_data") -> tuple:
    """
    Load data files for visualization
    
    Args:
        input_dir: Input directory path
        
    Returns:
        Tuple of (daily_returns_df, correlation_matrix)
    """
    input_path = Path(input_dir)
    
    # Load daily returns
    daily_returns_df = None
    possible_files = [
        "combined_daily_returns_2020_2024.csv",
        "all_assets_daily_returns_with_currencies_2020_2024.csv",
        "all_assets_daily_returns_2020_2024.csv"
    ]
    
    for filename in possible_files:
        filepath = input_path / filename
        if filepath.exists():
            print(f"Loading returns data from {filename}")
            daily_returns_df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            break
    
    # Load correlation matrix
    correlation_matrix = None
    corr_files = [
        "correlation_matrix.csv",
        "correlation_matrix_with_currencies.csv"
    ]
    
    for filename in corr_files:
        filepath = input_path / filename
        if filepath.exists():
            print(f"Loading correlation matrix from {filename}")
            correlation_matrix = pd.read_csv(filepath, index_col=0)
            break
    
    return daily_returns_df, correlation_matrix

def main():
    """
    Main function for standalone execution
    """
    print("Financial Data Visualization")
    print("=" * 50)
    
    # Load data
    daily_returns_df, correlation_matrix = load_data_for_visualization()
    
    if daily_returns_df is None and correlation_matrix is None:
        print("Error: No data files found")
        print("Please run fetch and analyze commands first")
        return
    
    # Create visualizations
    create_visualizations(daily_returns_df, correlation_matrix)
    
    print("\n" + "=" * 50)
    print("Visualization completed successfully!")
    print("=" * 50)
    print(f"Plots saved to: plots/")

if __name__ == "__main__":
    main()

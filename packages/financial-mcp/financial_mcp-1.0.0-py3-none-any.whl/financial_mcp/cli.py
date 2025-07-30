#!/usr/bin/env python3
"""
Command Line Interface for Financial MCP
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .fetch_data import main as fetch_main
from .analyze import main as analyze_main
from .visualize import main as visualize_main
from . import __version__, __description__

def create_parser() -> argparse.ArgumentParser:
    """
    Create the main argument parser
    
    Returns:
        argparse.ArgumentParser: Main parser
    """
    parser = argparse.ArgumentParser(
        prog='financial-mcp',
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  financial-mcp fetch --start-date 2023-01-01 --end-date 2023-12-31
  financial-mcp analyze --input-dir ./data
  financial-mcp visualize --output-dir ./plots
  financial-mcp run-all --start-date 2020-01-01

For more information, visit: https://github.com/Tatsuru-Kikuchi/MCP
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # Fetch command
    fetch_parser = subparsers.add_parser(
        'fetch',
        help='Fetch financial data from Yahoo Finance',
        description='Fetch daily price data and calculate returns for financial assets'
    )
    fetch_parser.add_argument(
        '--start-date',
        type=str,
        default='2020-01-01',
        help='Start date in YYYY-MM-DD format (default: 2020-01-01)'
    )
    fetch_parser.add_argument(
        '--end-date',
        type=str,
        default='2024-12-31',
        help='End date in YYYY-MM-DD format (default: 2024-12-31)'
    )
    fetch_parser.add_argument(
        '--output-dir',
        type=str,
        default='financial_data',
        help='Output directory for data files (default: financial_data)'
    )
    fetch_parser.add_argument(
        '--assets',
        type=str,
        nargs='*',
        help='Specific assets to fetch (default: all supported assets)'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze financial data and calculate metrics',
        description='Perform comprehensive analysis on financial returns data'
    )
    analyze_parser.add_argument(
        '--input-dir',
        type=str,
        default='financial_data',
        help='Input directory containing data files (default: financial_data)'
    )
    analyze_parser.add_argument(
        '--output-dir',
        type=str,
        default='financial_data',
        help='Output directory for analysis results (default: financial_data)'
    )
    
    # Visualize command
    visualize_parser = subparsers.add_parser(
        'visualize',
        help='Create visualizations and charts',
        description='Generate charts and plots from financial analysis data'
    )
    visualize_parser.add_argument(
        '--input-dir',
        type=str,
        default='financial_data',
        help='Input directory containing data files (default: financial_data)'
    )
    visualize_parser.add_argument(
        '--output-dir',
        type=str,
        default='plots',
        help='Output directory for plots (default: plots)'
    )
    
    # Run-all command
    runall_parser = subparsers.add_parser(
        'run-all',
        help='Run complete pipeline: fetch, analyze, and visualize',
        description='Execute the complete financial analysis pipeline'
    )
    runall_parser.add_argument(
        '--start-date',
        type=str,
        default='2020-01-01',
        help='Start date in YYYY-MM-DD format (default: 2020-01-01)'
    )
    runall_parser.add_argument(
        '--end-date',
        type=str,
        default='2024-12-31',
        help='End date in YYYY-MM-DD format (default: 2024-12-31)'
    )
    runall_parser.add_argument(
        '--data-dir',
        type=str,
        default='financial_data',
        help='Directory for data files (default: financial_data)'
    )
    runall_parser.add_argument(
        '--plots-dir',
        type=str,
        default='plots',
        help='Directory for plots (default: plots)'
    )
    
    return parser

def run_fetch(args) -> int:
    """
    Run the fetch command
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code
    """
    print(f"Fetching data from {args.start_date} to {args.end_date}")
    print(f"Output directory: {args.output_dir}")
    
    try:
        # Import and modify the fetch module temporarily
        from . import fetch_data
        
        # Store original functions
        original_fetch = fetch_data.fetch_financial_data
        original_save = fetch_data.save_data_to_csv
        
        # Get data
        all_data, daily_returns = original_fetch(
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if not daily_returns:
            print("No data was successfully fetched.")
            return 1
        
        # Save data
        original_save(all_data, daily_returns, args.output_dir)
        
        print("\nFetch completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during fetch: {e}")
        return 1

def run_analyze(args) -> int:
    """
    Run the analyze command
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code
    """
    print(f"Analyzing data from: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    
    try:
        # Check if input directory exists
        input_path = Path(args.input_dir)
        if not input_path.exists():
            print(f"Error: Input directory {args.input_dir} does not exist")
            return 1
        
        # Run analysis
        from . import analyze
        
        # Set the paths and run
        import pandas as pd
        import os
        
        data_file = input_path / 'combined_daily_returns_2020_2024.csv'
        if not data_file.exists():
            print(f"Error: Data file not found: {data_file}")
            print("Please run fetch command first")
            return 1
        
        # Load data
        daily_returns_df = pd.read_csv(data_file, index_col=0, parse_dates=True)
        
        # Perform analysis
        analysis_results = analyze.analyze_returns(daily_returns_df)
        correlation_matrix = analyze.calculate_correlation_matrix(daily_returns_df)
        risk_metrics = analyze.calculate_risk_metrics(daily_returns_df)
        
        # Save results
        analyze.save_analysis_results(
            analysis_results, correlation_matrix, risk_metrics, args.output_dir
        )
        
        print("\nAnalysis completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1

def run_visualize(args) -> int:
    """
    Run the visualize command
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code
    """
    print(f"Creating visualizations from: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    
    try:
        from . import visualize
        import pandas as pd
        from pathlib import Path
        
        input_path = Path(args.input_dir)
        
        # Load data files
        daily_returns_df = None
        correlation_matrix = None
        
        data_file = input_path / 'combined_daily_returns_2020_2024.csv'
        if data_file.exists():
            daily_returns_df = pd.read_csv(data_file, index_col=0, parse_dates=True)
        
        corr_file = input_path / 'correlation_matrix.csv'
        if corr_file.exists():
            correlation_matrix = pd.read_csv(corr_file, index_col=0)
        
        if daily_returns_df is None and correlation_matrix is None:
            print("Error: No data files found in input directory")
            print("Please run fetch and analyze commands first")
            return 1
        
        # Create visualizations
        visualize.create_visualizations(
            daily_returns_df, correlation_matrix, args.output_dir
        )
        
        print("\nVisualization completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during visualization: {e}")
        return 1

def run_all(args) -> int:
    """
    Run the complete pipeline
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: Exit code
    """
    print("Running complete Financial MCP pipeline")
    print("=" * 50)
    
    # Create namespace objects for each step
    class Args:
        pass
    
    # Step 1: Fetch
    print("\nStep 1: Fetching data...")
    fetch_args = Args()
    fetch_args.start_date = args.start_date
    fetch_args.end_date = args.end_date
    fetch_args.output_dir = args.data_dir
    fetch_args.assets = None
    
    if run_fetch(fetch_args) != 0:
        return 1
    
    # Step 2: Analyze
    print("\nStep 2: Analyzing data...")
    analyze_args = Args()
    analyze_args.input_dir = args.data_dir
    analyze_args.output_dir = args.data_dir
    
    if run_analyze(analyze_args) != 0:
        return 1
    
    # Step 3: Visualize
    print("\nStep 3: Creating visualizations...")
    viz_args = Args()
    viz_args.input_dir = args.data_dir
    viz_args.output_dir = args.plots_dir
    
    if run_visualize(viz_args) != 0:
        return 1
    
    print("\n" + "=" * 50)
    print("COMPLETE PIPELINE FINISHED SUCCESSFULLY!")
    print("=" * 50)
    print(f"Data files saved to: {args.data_dir}")
    print(f"Plots saved to: {args.plots_dir}")
    print("\nGenerated files:")
    print("- Combined daily returns data")
    print("- Analysis results and metrics")
    print("- Correlation matrix")
    print("- Risk metrics")
    print("- Comprehensive visualizations")
    
    return 0

def main() -> int:
    """
    Main CLI entry point
    
    Returns:
        int: Exit code
    """
    parser = create_parser()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Route to appropriate function
    if args.command == 'fetch':
        return run_fetch(args)
    elif args.command == 'analyze':
        return run_analyze(args)
    elif args.command == 'visualize':
        return run_visualize(args)
    elif args.command == 'run-all':
        return run_all(args)
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())

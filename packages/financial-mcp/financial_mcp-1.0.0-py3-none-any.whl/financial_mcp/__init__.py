"""
Financial MCP - A comprehensive financial data analysis and visualization package

This package provides tools for fetching, analyzing, and visualizing financial data
including stocks, cryptocurrencies, commodities, and currency pairs.

Features:
- Data fetching from Yahoo Finance
- Comprehensive financial analysis
- Interactive visualizations
- Command-line interface
- Correlation analysis
- Risk metrics calculation

Author: Tatsuru Kikuchi
License: Apache 2.0
"""

__version__ = "1.0.0"
__author__ = "Tatsuru Kikuchi"
__email__ = "tatsuru.kikuchi@example.com"
__description__ = "A comprehensive financial data analysis and visualization package"
__url__ = "https://github.com/Tatsuru-Kikuchi/MCP"

# Import main modules for easy access
try:
    from . import fetch_data
    from . import analyze
    from . import visualize
    from . import cli
except ImportError:
    # Handle cases where dependencies might not be installed
    pass

# Package metadata
__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__description__',
    '__url__',
    'fetch_data',
    'analyze',
    'visualize',
    'cli',
]

# Version info tuple for programmatic access
VERSION_INFO = tuple(map(int, __version__.split('.')))

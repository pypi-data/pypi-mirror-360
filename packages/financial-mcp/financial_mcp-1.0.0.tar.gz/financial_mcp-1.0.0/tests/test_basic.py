"""
Basic tests for financial_mcp package
"""

import unittest
import sys
from pathlib import Path

# Add the package root to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestFinancialMCP(unittest.TestCase):
    """Test basic package functionality"""
    
    def test_package_import(self):
        """Test that the package can be imported"""
        try:
            import financial_mcp
            self.assertTrue(hasattr(financial_mcp, '__version__'))
            self.assertTrue(hasattr(financial_mcp, '__author__'))
        except ImportError as e:
            self.fail(f"Could not import financial_mcp: {e}")
    
    def test_module_imports(self):
        """Test that main modules can be imported"""
        try:
            from financial_mcp import fetch_data
            from financial_mcp import analyze
            from financial_mcp import visualize
            from financial_mcp import cli
        except ImportError as e:
            self.fail(f"Could not import modules: {e}")
    
    def test_version_format(self):
        """Test version format is correct"""
        import financial_mcp
        version = financial_mcp.__version__
        
        # Check version format (should be X.Y.Z)
        parts = version.split('.')
        self.assertEqual(len(parts), 3, "Version should have 3 parts")
        
        for part in parts:
            self.assertTrue(part.isdigit(), f"Version part '{part}' should be numeric")
    
    def test_cli_main_function(self):
        """Test that CLI main function exists and is callable"""
        from financial_mcp.cli import main
        self.assertTrue(callable(main), "CLI main function should be callable")
    
    def test_fetch_data_functions(self):
        """Test that fetch_data module has required functions"""
        from financial_mcp import fetch_data
        
        required_functions = [
            'fetch_financial_data',
            'save_data_to_csv',
            'calculate_summary_statistics'
        ]
        
        for func_name in required_functions:
            self.assertTrue(
                hasattr(fetch_data, func_name),
                f"fetch_data should have {func_name} function"
            )
            self.assertTrue(
                callable(getattr(fetch_data, func_name)),
                f"{func_name} should be callable"
            )
    
    def test_analyze_functions(self):
        """Test that analyze module has required functions"""
        from financial_mcp import analyze
        
        required_functions = [
            'analyze_returns',
            'calculate_correlation_matrix',
            'calculate_risk_metrics'
        ]
        
        for func_name in required_functions:
            self.assertTrue(
                hasattr(analyze, func_name),
                f"analyze should have {func_name} function"
            )
            self.assertTrue(
                callable(getattr(analyze, func_name)),
                f"{func_name} should be callable"
            )
    
    def test_visualize_functions(self):
        """Test that visualize module has required functions"""
        from financial_mcp import visualize
        
        required_functions = [
            'create_cumulative_returns_plot',
            'create_correlation_heatmap',
            'create_visualizations'
        ]
        
        for func_name in required_functions:
            self.assertTrue(
                hasattr(visualize, func_name),
                f"visualize should have {func_name} function"
            )
            self.assertTrue(
                callable(getattr(visualize, func_name)),
                f"{func_name} should be callable"
            )

if __name__ == '__main__':
    unittest.main()

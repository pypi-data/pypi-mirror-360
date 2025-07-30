"""
港股数据MCP工具包
提供港股财务数据和基本面数据的获取和管理功能
"""

__version__ = "0.1.0"
__author__ = "Financial Terminal"
__email__ = "your-email@example.com"
__description__ = "MCP tools for Hong Kong stock data and financial reports"

from .core.mcp_server import HKStockMCPServer
from .tools.financial_reports import FinancialReportsTools
from .tools.yfinance_tools import YFinanceTools
from .database.db_manager import DatabaseManager

__all__ = [
    "HKStockMCPServer",
    "FinancialReportsTools", 
    "YFinanceTools",
    "DatabaseManager"
] 
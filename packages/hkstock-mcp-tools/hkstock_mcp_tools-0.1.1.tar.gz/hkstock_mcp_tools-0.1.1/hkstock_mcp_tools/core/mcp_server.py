"""
港股数据MCP服务器核心实现
提供完整的MCP服务器功能，包括财务报表和yfinance数据获取
"""

import json
import logging
from typing import Optional, Union, List

from mcp.server.fastmcp import FastMCP

from ..database.db_manager import DatabaseManager
from ..tools.financial_reports import FinancialReportsTools
from ..tools.yfinance_tools import YFinanceTools
from ..tools.stock_validator import StockValidator

logger = logging.getLogger(__name__)


class HKStockMCPServer:
    """港股数据MCP服务器"""
    
    def __init__(self, db_path: Optional[str] = None, auto_cleanup: bool = True):
        """
        初始化MCP服务器
        
        Args:
            db_path: 数据库文件路径
            auto_cleanup: 是否启用自动清理过期数据，默认为True
        """
        self.mcp = FastMCP("hkstock_mcp_tools")
        self.db_manager = DatabaseManager(db_path, auto_cleanup)
        self.financial_tools = FinancialReportsTools(self.db_manager)
        self.yfinance_tools = YFinanceTools(self.db_manager)
        
        # 注册所有工具
        self._register_tools()
    
    def _register_tools(self):
        """注册所有MCP工具"""
        
        @self.mcp.tool()
        async def get_hk_balance_sheet(stock: str, indicator: str = "年度", n_periods: int = 1) -> str:
            """
            获取港股资产负债表
            
            Args:
                stock: 港股代码，必须按要求填写，不带后缀的5位数字字符串，如"00700"
                indicator: 报告期类型，可选值："年度"、"中报"、"季报"，默认为"年度"
                n_periods: 获取的期数，默认为1
                
            请求示例:
                {
                    "stock": "00700",
                    "indicator": "年度",
                    "n_periods": 1
                }
            """
            try:
                # 验证股票代码
                validation_result = StockValidator.validate_stock_code(stock)
                if not validation_result["is_valid"]:
                    return json.dumps({
                        "status": "error",
                        "message": f"无效的股票代码: {validation_result['error']}",
                        "data": []
                    }, ensure_ascii=False)
                
                # 获取akshare格式的股票代码
                if validation_result["market"] == "HK":
                    formatted_stock = validation_result["akshare_format"]
                else:
                    formatted_stock = validation_result["formatted_code"]
                
                logger.info(f"原始股票代码: {stock}, 格式化后: {formatted_stock}")
                
                # 获取数据
                result = await self.financial_tools.get_balance_sheet(formatted_stock, indicator, n_periods)
                return json.dumps(result.dict(), ensure_ascii=False)
            except Exception as e:
                logger.error(f"获取资产负债表失败: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"获取资产负债表失败: {str(e)}",
                    "data": []
                }, ensure_ascii=False)

        @self.mcp.tool()
        async def get_hk_income_statement(stock: str, indicator: str = "年度", n_periods: int = 1) -> str:
            """
            获取港股利润表
            
            Args:
                stock: 港股代码，必须按要求填写，不带后缀的5位数字字符串，如"00700"
                indicator: 报告期类型，可选值："年度"、"中报"、"季报"，默认为"年度"
                n_periods: 获取的期数，默认为1
                
            请求示例:
                {
                    "stock": "00700",
                    "indicator": "年度",
                    "n_periods": 1
                }
            """
            try:
                # 验证股票代码
                validation_result = StockValidator.validate_stock_code(stock)
                if not validation_result["is_valid"]:
                    return json.dumps({
                        "status": "error",
                        "message": f"无效的股票代码: {validation_result['error']}",
                        "data": []
                    }, ensure_ascii=False)
                
                # 获取akshare格式的股票代码
                if validation_result["market"] == "HK":
                    formatted_stock = validation_result["akshare_format"]
                else:
                    formatted_stock = validation_result["formatted_code"]
                
                logger.info(f"原始股票代码: {stock}, 格式化后: {formatted_stock}")
                
                # 获取数据
                result = await self.financial_tools.get_income_statement(formatted_stock, indicator, n_periods)
                return json.dumps(result.dict(), ensure_ascii=False)
            except Exception as e:
                logger.error(f"获取利润表失败: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"获取利润表失败: {str(e)}",
                    "data": []
                }, ensure_ascii=False)

        @self.mcp.tool()
        async def get_hk_cash_flow(stock: str, indicator: str = "年度", n_periods: int = 1) -> str:
            """
            获取港股现金流量表
            
            Args:
                stock: 港股代码，必须按要求填写，不带后缀的5位数字字符串，如"00700"
                indicator: 报告期类型，可选值："年度"、"中报"、"季报"，默认为"年度"
                n_periods: 获取的期数，默认为1
                
            请求示例:
                {
                    "stock": "00700",
                    "indicator": "年度",
                    "n_periods": 1
                }
            """
            try:
                # 验证股票代码
                validation_result = StockValidator.validate_stock_code(stock)
                if not validation_result["is_valid"]:
                    return json.dumps({
                        "status": "error",
                        "message": f"无效的股票代码: {validation_result['error']}",
                        "data": []
                    }, ensure_ascii=False)
                
                # 获取akshare格式的股票代码
                if validation_result["market"] == "HK":
                    formatted_stock = validation_result["akshare_format"]
                else:
                    formatted_stock = validation_result["formatted_code"]
                
                logger.info(f"原始股票代码: {stock}, 格式化后: {formatted_stock}")
                
                # 获取数据
                result = await self.financial_tools.get_cash_flow(formatted_stock, indicator, n_periods)
                return json.dumps(result.dict(), ensure_ascii=False)
            except Exception as e:
                logger.error(f"获取现金流量表失败: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"获取现金流量表失败: {str(e)}",
                    "data": []
                }, ensure_ascii=False)

        # @self.mcp.tool()
        async def get_financial_item(
            stock: str, 
            item_names: str, 
            report_type: str = "资产负债表", 
            n_periods: int = 5, 
            indicator: str = "年度"
        ) -> str:
            """
            获取指定财务报表项目的数据
            
            Args:
                stock: 港股代码，必须按要求填写，不带后缀的5位数字字符串，如"00700"
                item_names: 财务项目名称，支持：
                    - 单个项目: "净资产"、"营业收入"、"现金流量净额"
                    - 多个项目: "净资产,营业收入,净利润" (逗号分隔)
                    - 支持模糊匹配，如"收入"可匹配"营业收入"
                report_type: 报表类型，可选值：
                    - "资产负债表" (默认) - 包含资产、负债、所有者权益项目
                    - "利润表" - 包含收入、成本、利润项目
                    - "现金流量表" - 包含经营、投资、筹资现金流项目
                n_periods: 获取的期数，默认为5（获取最近5期数据）
                indicator: 报告期类型，可选值："年度"、"中报"、"季报"，默认为"年度"
                
            请求示例:
                >>> {"stock": "00700", "item_names": "净资产", "report_type": "资产负债表", "n_periods": 5, "indicator": "年度"}  # 腾讯净资产，最近5年
                >>> {"stock": "00700", "item_names": "营业收入,净利润", "report_type": "利润表", "n_periods": 3, "indicator": "年度"}  # 腾讯收入和利润，最近3年
                >>> {"stock": "09988", "item_names": "现金流量净额", "report_type": "现金流量表", "n_periods": 2, "indicator": "中报"}  # 阿里巴巴现金流，最近2期中报
            """
            try:
                # 验证股票代码
                validation_result = StockValidator.validate_stock_code(stock)
                if not validation_result["is_valid"]:
                    return json.dumps({
                        "status": "error",
                        "message": f"无效的股票代码: {validation_result['error']}",
                        "data": []
                    }, ensure_ascii=False)
                
                # 获取akshare格式的股票代码
                if validation_result["market"] == "HK":
                    formatted_stock = validation_result["akshare_format"]
                else:
                    formatted_stock = validation_result["formatted_code"]
                
                logger.info(f"原始股票代码: {stock}, 格式化后: {formatted_stock}")
                
                # 处理项目名称
                items_list = [item.strip() for item in item_names.split(',') if item.strip()]
                
                # 获取数据
                result = await self.financial_tools.get_financial_item(
                    formatted_stock, items_list, report_type, n_periods, indicator
                )
                return json.dumps(result.dict(), ensure_ascii=False)
            except Exception as e:
                logger.error(f"获取财务项目数据失败: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"获取财务项目数据失败: {str(e)}",
                    "data": []
                }, ensure_ascii=False)

        @self.mcp.tool()
        async def get_hk_financial_reports(stock: str, indicator: str = "年度", n_periods: int = 1) -> str:
            """
            一次性获取港股三大财务报表（资产负债表、利润表、现金流量表）
            
            Args:
                stock: 港股代码，必须按要求填写，不带后缀的5位数字字符串，如"00700"
                indicator: 报告期类型，可选值："年度"、"中报"、"季报"，默认为"年度"
                n_periods: 获取的期数，默认为1
                
            请求示例:
                {
                    "stock": "00700",
                    "indicator": "年度",
                    "n_periods": 1
                }
                
            返回数据包含：
                - balance_sheet: 资产负债表数据
                - income_statement: 利润表数据
                - cash_flow: 现金流量表数据
            """
            try:
                # 验证股票代码
                validation_result = StockValidator.validate_stock_code(stock)
                if not validation_result["is_valid"]:
                    return json.dumps({
                        "status": "error",
                        "message": f"无效的股票代码: {validation_result['error']}",
                        "data": {}
                    }, ensure_ascii=False)
                
                # 获取akshare格式的股票代码
                if validation_result["market"] == "HK":
                    formatted_stock = validation_result["akshare_format"]
                else:
                    formatted_stock = validation_result["formatted_code"]
                
                logger.info(f"原始股票代码: {stock}, 格式化后: {formatted_stock}")
                logger.info(f"开始获取三大财务报表，报告期: {indicator}, 期数: {n_periods}")
                
                # 并行获取三大财务报表
                import asyncio
                
                # 创建三个异步任务
                balance_sheet_task = self.financial_tools.get_balance_sheet(formatted_stock, indicator, n_periods)
                income_statement_task = self.financial_tools.get_income_statement(formatted_stock, indicator, n_periods)
                cash_flow_task = self.financial_tools.get_cash_flow(formatted_stock, indicator, n_periods)
                
                # 等待所有任务完成
                balance_sheet_result, income_statement_result, cash_flow_result = await asyncio.gather(
                    balance_sheet_task,
                    income_statement_task,
                    cash_flow_task,
                    return_exceptions=True
                )
                
                # 处理结果
                combined_result = {
                    "status": "success",
                    "message": f"成功获取股票 {stock} 的三大财务报表",
                    "data": {
                        "stock_code": stock,
                        "formatted_stock_code": formatted_stock,
                        "indicator": indicator,
                        "n_periods": n_periods,
                        "balance_sheet": None,
                        "income_statement": None,
                        "cash_flow": None
                    },
                    "errors": []
                }
                
                # 处理资产负债表结果
                if isinstance(balance_sheet_result, Exception):
                    logger.error(f"获取资产负债表失败: {balance_sheet_result}")
                    combined_result["errors"].append(f"资产负债表: {str(balance_sheet_result)}")
                else:
                    combined_result["data"]["balance_sheet"] = balance_sheet_result.dict()
                
                # 处理利润表结果
                if isinstance(income_statement_result, Exception):
                    logger.error(f"获取利润表失败: {income_statement_result}")
                    combined_result["errors"].append(f"利润表: {str(income_statement_result)}")
                else:
                    combined_result["data"]["income_statement"] = income_statement_result.dict()
                
                # 处理现金流量表结果
                if isinstance(cash_flow_result, Exception):
                    logger.error(f"获取现金流量表失败: {cash_flow_result}")
                    combined_result["errors"].append(f"现金流量表: {str(cash_flow_result)}")
                else:
                    combined_result["data"]["cash_flow"] = cash_flow_result.dict()
                
                # 如果所有报表都失败了，返回错误状态
                if (combined_result["data"]["balance_sheet"] is None and 
                    combined_result["data"]["income_statement"] is None and 
                    combined_result["data"]["cash_flow"] is None):
                    combined_result["status"] = "error"
                    combined_result["message"] = "无法获取任何财务报表数据"
                elif combined_result["errors"]:
                    combined_result["status"] = "partial_success"
                    combined_result["message"] = f"部分成功获取财务报表，{len(combined_result['errors'])} 个报表获取失败"
                
                logger.info(f"三大财务报表获取完成，状态: {combined_result['status']}")
                return json.dumps(combined_result, ensure_ascii=False)
                
            except Exception as e:
                logger.error(f"获取三大财务报表失败: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"获取三大财务报表失败: {str(e)}",
                    "data": {}
                }, ensure_ascii=False)

        @self.mcp.tool()
        async def get_company_info(stock: str, force_refresh: bool = False) -> str:
            """
            获取公司基本信息
            
            Args:
                stock: 股票代码，必须根据格式要求填写
                    港股代码:
                    - 4位带后缀: "0700.HK"
                    A股代码:
                    - 6位带后缀: "000001.SZ", "600000.SS"
                    美股代码:
                    - 字母代码: "AAPL", "TSLA"
                force_refresh: 是否强制刷新数据，默认为False（优先使用缓存）
                
            Returns:
                返回公司信息的JSON字符串，包含以下信息：
                - basic_info: 基本信息（名称、简称、行业、国家、网站、员工数等）
                - financial_metrics: 财务指标（市值、PE、PB、ROE等）
                - price_info: 价格信息（当前价格、成交量、52周高低点等）
                - dividend_info: 分红信息（股息率、派息比例等）
                - financial_summary: 财务汇总（营收、现金、债务等）
            """
            try:
                # 验证股票代码
                validation_result = StockValidator.validate_stock_code(stock)
                if not validation_result["is_valid"]:
                    return json.dumps({
                        "status": "error",
                        "message": f"无效的股票代码: {validation_result['error']}",
                        "data": {}
                    }, ensure_ascii=False)
                
                # 获取yfinance格式的股票代码
                if validation_result["market"] == "HK":
                    formatted_stock = validation_result["yfinance_format"]
                else:
                    formatted_stock = validation_result["formatted_code"]
                
                logger.info(f"原始股票代码: {stock}, 格式化后: {formatted_stock}")
                
                # 获取数据 - 直接传入格式化后的股票代码
                result = await self.yfinance_tools.get_company_info(formatted_stock, force_refresh)
                return json.dumps(result.dict(), ensure_ascii=False)
            except Exception as e:
                logger.error(f"获取公司信息失败: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"获取公司信息失败: {str(e)}",
                    "data": {}
                }, ensure_ascii=False)

        @self.mcp.tool()
        async def get_dividend_actions(stock: str, force_refresh: bool = False) -> str:
            """
            获取历史股息分红和拆股行为数据，包括日期、类型、分红金额、拆股比例等
            
            Args:
                stock: 股票代码，必须按要求填写
                    港股代码:
                    - 4位带后缀: "0700.HK"
                    A股代码:
                    - 6位带后缀: "000001.SZ", "600000.SS"
                    美股代码:
                    - 字母代码: "AAPL", "TSLA"
                force_refresh: 是否强制刷新数据，默认为False（优先使用缓存）
                
            请求示例:
                {
                    "stock": "0700.HK",
                    "force_refresh": false
                }
            """
            try:
                # 验证股票代码
                validation_result = StockValidator.validate_stock_code(stock)
                if not validation_result["is_valid"]:
                    return json.dumps({
                        "status": "error",
                        "message": f"无效的股票代码: {validation_result['error']}",
                        "data": []
                    }, ensure_ascii=False)
                
                # 获取yfinance格式的股票代码
                if validation_result["market"] == "HK":
                    formatted_stock = validation_result["yfinance_format"]
                else:
                    formatted_stock = validation_result["formatted_code"]
                
                logger.info(f"原始股票代码: {stock}, 格式化后: {formatted_stock}")
                
                # 获取数据 - 直接传入格式化后的股票代码
                result = await self.yfinance_tools.get_dividend_actions(formatted_stock, force_refresh)
                return json.dumps(result.dict(), ensure_ascii=False)
            except Exception as e:
                logger.error(f"获取分红拆股数据失败: {e}")
                return json.dumps({
                    "status": "error",
                    "message": f"获取分红拆股数据失败: {str(e)}",
                    "data": []
                }, ensure_ascii=False)


    def run(self, transport: str = 'stdio'):
        """
        运行MCP服务器
        
        Args:
            transport: 传输方式，默认为'stdio'
        """
        logger.info("启动港股数据MCP服务器...")
        self.mcp.run(transport=transport)


def main():
    """主函数，用于命令行启动"""
    server = HKStockMCPServer()
    server.run()


if __name__ == "__main__":
    main() 
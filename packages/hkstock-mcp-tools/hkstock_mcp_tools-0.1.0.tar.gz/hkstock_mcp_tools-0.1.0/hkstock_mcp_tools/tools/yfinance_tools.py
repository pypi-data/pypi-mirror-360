"""
YFinance工具类
使用yfinance获取企业信息和分红拆股行为数据
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import yfinance as yf
import pandas as pd

from ..database.db_manager import DatabaseManager
from ..database.models import StockDataResponse

logger = logging.getLogger(__name__)


class YFinanceTools:
    """YFinance工具类"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化YFinance工具
        
        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
    
    def validate_and_format_ticker(self, stock_code: str) -> str:
        """
        验证并格式化股票代码为yfinance需要的格式
        
        Args:
            stock_code: 原始股票代码，支持以下格式：
                港股代码:
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                A股代码:
                - 6位数字: "000001", "600000"
                - 带后缀: "000001.SZ", "600000.SS"
                美股代码:
                - 字母代码: "AAPL", "TSLA"
                
        Returns:
            格式化后的股票代码，yfinance格式：
            - 港股: "0700.HK" (4位数字 + .HK)
            - A股: "000001.SZ", "600000.SS"
            - 美股: "AAPL"
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        Examples:
            >>> validate_and_format_ticker("700")
            "0700.HK"
            >>> validate_and_format_ticker("00700")
            "0700.HK"
            >>> validate_and_format_ticker("000001")
            "000001.SZ"
            >>> validate_and_format_ticker("AAPL")
            "AAPL"
        """
        try:
            # 导入股票验证器
            from .stock_validator import StockValidator
            
            # 验证股票代码
            result = StockValidator.validate_stock_code(stock_code)
            
            if not result["is_valid"]:
                raise ValueError(
                    f"无效的股票代码格式: {stock_code}. "
                    f"支持的格式: "
                    f"港股（纯数字如'700'或带后缀如'700.HK'）, "
                    f"A股（6位数字如'000001'或带后缀如'000001.SZ'）, "
                    f"美股（字母代码如'AAPL'）。"
                    f"错误信息: {result['error']}"
                )
            
            # 根据市场类型返回相应格式
            if result["market"] == "HK":
                return StockValidator.format_for_yfinance(stock_code)
            else:
                return result["formatted_code"]
                
        except ImportError:
            # 如果无法导入验证器，使用原有逻辑作为后备
            if not stock_code:
                raise ValueError("股票代码不能为空")
            
            stock_code = stock_code.strip().upper()
            
            # 港股代码处理
            if stock_code.isdigit():
                # 纯数字，需要判断是港股还是A股
                if len(stock_code) <= 5:
                    # 港股代码，保持4位数格式加上.HK后缀
                    formatted_number = str(int(stock_code)).zfill(4)
                    return f"{formatted_number}.HK"
                elif len(stock_code) == 6:
                    # A股代码，需要判断是上海还是深圳
                    if stock_code.startswith(('60', '68', '11', '50', '51', '52')):
                        return f"{stock_code}.SS"
                    else:
                        return f"{stock_code}.SZ"
            
            # 已经包含后缀的代码
            if '.' in stock_code:
                # 如果是.HK后缀，需要处理数字部分的前导零
                if stock_code.endswith('.HK'):
                    number_part = stock_code[:-3]
                    if number_part.isdigit():
                        # 保持4位数格式
                        formatted_number = str(int(number_part)).zfill(4)
                        return f"{formatted_number}.HK"
                return stock_code
            
            # 美股代码（字母）
            if stock_code.isalpha():
                return stock_code
            
            # 混合代码，默认作为美股处理
            return stock_code

    async def get_company_info(self, stock_code: str, force_refresh: bool = False) -> StockDataResponse:
        """
        获取公司基本信息
        
        Args:
            stock_code: 股票代码，支持多种格式：
                港股代码:
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                A股代码:
                - 6位数字: "000001", "600000"
                - 带后缀: "000001.SZ", "600000.SS"
                美股代码:
                - 字母代码: "AAPL", "TSLA"
                系统会自动格式化为yfinance需要的格式
            force_refresh: 是否强制刷新数据，默认False（优先使用缓存）
            
        Returns:
            StockDataResponse对象，包含公司信息
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        示例数据结构:
        {
            "status": "success",
            "data": {
                "basic_info": {
                    "symbol": "6186.HK",
                    "shortName": "CHINA FEIHE",
                    "longName": "China Feihe Limited",
                    "sector": "Consumer Defensive",
                    "industry": "Packaged Foods",
                    "country": "China",
                    "website": "https://www.feihe.com",
                    "fullTimeEmployees": 9590
                },
                "financial_metrics": {
                    "marketCap": 51683287040,
                    "enterpriseValue": 35275780096,
                    "trailingPE": 13.514286,
                    "forwardPE": 9.27451,
                    "priceToBook": 1.6538463,
                    "debtToEquity": 3.945,
                    "returnOnAssets": 0.08294,
                    "returnOnEquity": 0.13599
                },
                "price_info": {
                    "currentPrice": 4.73,
                    "previousClose": 5.7,
                    "open": 4.85,
                    "dayLow": 4.65,
                    "dayHigh": 4.94,
                    "fiftyTwoWeekLow": 3.39,
                    "fiftyTwoWeekHigh": 7.38,
                    "volume": 211498111,
                    "averageVolume": 32236158
                },
                "dividend_info": {
                    "dividendRate": 0.33,
                    "dividendYield": 5.72,
                    "payoutRatio": 0.72330004,
                    "fiveYearAvgDividendYield": 4.82,
                    "lastDividendValue": 0.1632,
                    "lastDividendDate": "2025-01-31"
                }
            }
        }
        """
        try:
            logger.info(f"开始获取股票 {stock_code} 的公司信息...")
            
            # 验证并格式化股票代码
            ticker_symbol = self.validate_and_format_ticker(stock_code)
            logger.info(f"格式化后的股票代码: {ticker_symbol}")
            
            # 检查数据库中是否有非过期数据
            if not force_refresh:
                logger.info("检查数据库中的缓存数据...")
                cached_info = self.db_manager.get_company_info(ticker_symbol)
                if cached_info:
                    logger.info("从数据库获取到有效的公司信息")
                    return StockDataResponse(
                        status="success",
                        message="从缓存获取数据",
                        data=[self._format_company_info(cached_info['info_json'])]
                    )
            
            # 从yfinance获取数据
            logger.info("从yfinance获取公司信息...")
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                logger.error(f"无法获取股票 {ticker_symbol} 的信息")
                return StockDataResponse(
                    status="error",
                    message=f"无法获取股票 {ticker_symbol} 的信息",
                    data=[]
                )
            
            logger.info(f"成功获取公司信息，股票名称: {info.get('shortName', 'N/A')}")
            
            # 保存到数据库
            save_success = self.db_manager.save_company_info(ticker_symbol, info)
            if save_success:
                logger.info("公司信息已保存到数据库")
            else:
                logger.warning("公司信息保存到数据库失败")
            
            # 格式化返回数据
            formatted_data = self._format_company_info(info)
            
            return StockDataResponse(
                status="success",
                message="",
                data=[formatted_data],
                metadata={
                    "stock_code": stock_code,
                    "ticker_symbol": ticker_symbol,
                    "timestamp": datetime.now().isoformat(),
                    "data_source": "yfinance"
                }
            )
            
        except Exception as e:
            logger.error(f"获取公司信息失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            return StockDataResponse(
                status="error",
                message=f"获取公司信息失败: {str(e)}",
                data=[]
            )

    def _format_company_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """格式化公司信息"""
        return {
            "basic_info": {
                "symbol": info.get("symbol", ""),
                "shortName": info.get("shortName", ""),
                "longName": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "country": info.get("country", ""),
                "website": info.get("website", ""),
                "fullTimeEmployees": info.get("fullTimeEmployees"),
                "longBusinessSummary": info.get("longBusinessSummary", "")
            },
            "financial_metrics": {
                "marketCap": info.get("marketCap"),
                "enterpriseValue": info.get("enterpriseValue"),
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "priceToBook": info.get("priceToBook"),
                "debtToEquity": info.get("debtToEquity"),
                "returnOnAssets": info.get("returnOnAssets"),
                "returnOnEquity": info.get("returnOnEquity"),
                "profitMargins": info.get("profitMargins"),
                "grossMargins": info.get("grossMargins"),
                "operatingMargins": info.get("operatingMargins"),
                "ebitdaMargins": info.get("ebitdaMargins")
            },
            "price_info": {
                "currentPrice": info.get("currentPrice"),
                "previousClose": info.get("previousClose"),
                "open": info.get("open"),
                "dayLow": info.get("dayLow"),
                "dayHigh": info.get("dayHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "volume": info.get("volume"),
                "averageVolume": info.get("averageVolume"),
                "beta": info.get("beta"),
                "currency": info.get("currency", "")
            },
            "dividend_info": {
                "dividendRate": info.get("dividendRate"),
                "dividendYield": info.get("dividendYield"),
                "payoutRatio": info.get("payoutRatio"),
                "fiveYearAvgDividendYield": info.get("fiveYearAvgDividendYield"),
                "lastDividendValue": info.get("lastDividendValue"),
                "lastDividendDate": datetime.fromtimestamp(info.get("lastDividendDate", 0)).strftime('%Y-%m-%d') if info.get("lastDividendDate") else None,
                "exDividendDate": datetime.fromtimestamp(info.get("exDividendDate", 0)).strftime('%Y-%m-%d') if info.get("exDividendDate") else None
            },
            "financial_summary": {
                "totalRevenue": info.get("totalRevenue"),
                "totalCash": info.get("totalCash"),
                "totalDebt": info.get("totalDebt"),
                "totalCashPerShare": info.get("totalCashPerShare"),
                "revenuePerShare": info.get("revenuePerShare"),
                "quickRatio": info.get("quickRatio"),
                "currentRatio": info.get("currentRatio"),
                "earningsGrowth": info.get("earningsGrowth"),
                "revenueGrowth": info.get("revenueGrowth")
            }
        }

    async def get_dividend_actions(self, stock_code: str, force_refresh: bool = False) -> StockDataResponse:
        """
        获取股息分红和拆股行为数据
        
        Args:
            stock_code: 股票代码，支持多种格式：
                港股代码:
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                A股代码:
                - 6位数字: "000001", "600000"
                - 带后缀: "000001.SZ", "600000.SS"
                美股代码:
                - 字母代码: "AAPL", "TSLA"
                系统会自动格式化为yfinance需要的格式
            force_refresh: 是否强制刷新数据，默认False（优先使用缓存）
            
        Returns:
            StockDataResponse对象，包含分红拆股数据
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        示例数据结构:
        {
            "status": "success",
            "data": [
                {
                    "date": "2024-01-31",
                    "type": "dividend",
                    "dividend_amount": 0.1632,
                    "stock_splits": null
                },
                {
                    "date": "2023-08-15",
                    "type": "stock_split",
                    "dividend_amount": null,
                    "stock_splits": "2:1"
                }
            ]
        }
        """
        try:
            logger.info(f"开始获取股票 {stock_code} 的分红拆股数据...")
            
            # 验证并格式化股票代码
            ticker_symbol = self.validate_and_format_ticker(stock_code)
            logger.info(f"格式化后的股票代码: {ticker_symbol}")
            
            # 检查数据库中是否有非过期数据
            if not force_refresh:
                logger.info("检查数据库中的缓存数据...")
                cached_actions = self.db_manager.get_dividend_actions(ticker_symbol)
                if not cached_actions.empty:
                    logger.info(f"从数据库获取到 {len(cached_actions)} 条分红拆股数据")
                    data = []
                    for _, row in cached_actions.iterrows():
                        data.append({
                            "date": row['action_date'].strftime('%Y-%m-%d'),
                            "type": row['action_type'],
                            "dividend_amount": row['dividend_amount'],
                            "stock_splits": row['stock_splits']
                        })
                    
                    return StockDataResponse(
                        status="success",
                        message="从缓存获取数据",
                        data=data
                    )
            
            # 从yfinance获取数据
            logger.info("从yfinance获取分红拆股数据...")
            ticker = yf.Ticker(ticker_symbol)
            actions = ticker.actions
            
            if actions.empty:
                logger.info("没有找到分红拆股数据")
                return StockDataResponse(
                    status="success",
                    message="没有找到分红拆股数据",
                    data=[]
                )
            
            logger.info(f"成功获取 {len(actions)} 条分红拆股数据")
            
            # 保存到数据库
            save_success = self.db_manager.save_dividend_actions(ticker_symbol, actions)
            if save_success:
                logger.info("分红拆股数据已保存到数据库")
            else:
                logger.warning("分红拆股数据保存到数据库失败")
            
            # 格式化返回数据
            data = []
            for date, row in actions.iterrows():
                dividend_amount = self.db_manager.clean_amount(row.get('Dividends', 0))
                stock_splits = str(row.get('Stock Splits', '')) if row.get('Stock Splits') else None
                
                # 添加分红记录
                if dividend_amount and dividend_amount > 0:
                    data.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "type": "dividend",
                        "dividend_amount": dividend_amount,
                        "stock_splits": None
                    })
                
                # 添加拆股记录
                if stock_splits and stock_splits != '0.0':
                    data.append({
                        "date": date.strftime('%Y-%m-%d'),
                        "type": "stock_split",
                        "dividend_amount": None,
                        "stock_splits": stock_splits
                    })
            
            # 按日期降序排序
            data.sort(key=lambda x: x['date'], reverse=True)
            
            return StockDataResponse(
                status="success",
                message="",
                data=data,
                metadata={
                    "stock_code": stock_code,
                    "ticker_symbol": ticker_symbol,
                    "timestamp": datetime.now().isoformat(),
                    "data_source": "yfinance",
                    "total_actions": len(data)
                }
            )
            
        except Exception as e:
            logger.error(f"获取分红拆股数据失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            return StockDataResponse(
                status="error",
                message=f"获取分红拆股数据失败: {str(e)}",
                data=[]
            )

    async def get_stock_summary(self, stock_code: str, force_refresh: bool = False) -> StockDataResponse:
        """
        获取股票综合信息汇总（公司信息 + 分红拆股数据）
        
        Args:
            stock_code: 股票代码，支持多种格式：
                港股代码:
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                A股代码:
                - 6位数字: "000001", "600000"
                - 带后缀: "000001.SZ", "600000.SS"
                美股代码:
                - 字母代码: "AAPL", "TSLA"
                系统会自动格式化为yfinance需要的格式
            force_refresh: 是否强制刷新数据，默认False（优先使用缓存）
            
        Returns:
            StockDataResponse对象，包含综合信息：
            - company_info: 公司基本信息、财务指标、价格信息、分红信息
            - dividend_actions: 历史分红拆股记录
            - actions_summary: 分红拆股统计摘要
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        Examples:
            >>> await get_stock_summary("700")  # 腾讯综合信息
            >>> await get_stock_summary("AAPL", True)  # 苹果综合信息，强制刷新
        """
        try:
            logger.info(f"开始获取股票 {stock_code} 的综合信息...")
            
            # 获取公司信息
            company_info_response = await self.get_company_info(stock_code, force_refresh)
            if company_info_response.status == "error":
                return company_info_response
            
            # 获取分红拆股数据
            actions_response = await self.get_dividend_actions(stock_code, force_refresh)
            
            # 综合返回数据
            summary_data = {
                "company_info": company_info_response.data,
                "dividend_actions": actions_response.data if actions_response.status == "success" else [],
                "actions_summary": {
                    "total_dividends": len([a for a in actions_response.data if a.get('type') == 'dividend']) if actions_response.status == "success" else 0,
                    "total_stock_splits": len([a for a in actions_response.data if a.get('type') == 'stock_split']) if actions_response.status == "success" else 0,
                    "latest_dividend": next((a for a in actions_response.data if a.get('type') == 'dividend'), None) if actions_response.status == "success" else None
                }
            }
            
            return StockDataResponse(
                status="success",
                message="",
                data=summary_data,
                metadata={
                    "stock_code": stock_code,
                    "timestamp": datetime.now().isoformat(),
                    "data_sources": ["yfinance"]
                }
            )
            
        except Exception as e:
            logger.error(f"获取股票综合信息失败: {str(e)}")
            return StockDataResponse(
                status="error",
                message=f"获取股票综合信息失败: {str(e)}",
                data={}
            ) 
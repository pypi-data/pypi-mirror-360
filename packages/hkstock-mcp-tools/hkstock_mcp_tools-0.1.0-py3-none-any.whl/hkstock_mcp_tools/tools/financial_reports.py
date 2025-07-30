"""
财务报表工具类
提供港股三大财务报表的获取和处理功能
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

import akshare as ak
import pandas as pd
import numpy as np

from .stock_validator import StockValidator
from ..database.db_manager import DatabaseManager
from ..database.models import StockDataResponse

logger = logging.getLogger(__name__)


class FinancialReportsTools:
    """港股财务报表工具类"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.validator = StockValidator()
    
    def format_akshare_stock_code(self, stock_code: str) -> str:
        """
        格式化股票代码为akshare需要的5位数格式
        
        Args:
            stock_code: 原始股票代码，支持以下格式：
                - 纯数字: "700", "0700", "00700"
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                - 不支持字母代码或其他格式
            
        Returns:
            格式化后的5位数股票代码，如 "00700"
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        Examples:
            >>> format_akshare_stock_code("700")
            "00700"
            >>> format_akshare_stock_code("0700.HK")
            "00700"
        """
        try:
            # 使用股票验证器进行格式化
            akshare_code = self.validator.format_for_akshare(stock_code)
            return akshare_code
        except ValueError as e:
            # 提供更详细的错误信息
            raise ValueError(
                f"无效的港股代码格式: {stock_code}. "
                f"akshare要求5位数字格式（如 '00700'）。"
                f"支持的输入格式: 纯数字（如 '700', '0700'）或带.HK后缀（如 '700.HK'）。"
                f"原始错误: {str(e)}"
            )
    
    def infer_report_type_from_items(self, item_names: List[str]) -> str:
        """
        根据项目名称推断报表类型
        
        Args:
            item_names: 项目名称列表
            
        Returns:
            推断的报表类型
        """
        balance_sheet_items = ['资产总计', '负债合计', '所有者权益', '净资产', '流动资产', '非流动资产']
        income_statement_items = ['营业收入', '营业成本', '净利润', '利润总额', '营业利润', '毛利润']
        cash_flow_items = ['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', '筹资活动产生的现金流量净额']
        
        # 统计各类型匹配的项目数量
        balance_matches = sum(1 for item in item_names if any(bs_item in item for bs_item in balance_sheet_items))
        income_matches = sum(1 for item in item_names if any(is_item in item for is_item in income_statement_items))
        cash_flow_matches = sum(1 for item in item_names if any(cf_item in item for cf_item in cash_flow_items))
        
        # 返回匹配数量最多的类型
        if balance_matches >= income_matches and balance_matches >= cash_flow_matches:
            return "资产负债表"
        elif income_matches >= cash_flow_matches:
            return "利润表"
        else:
            return "现金流量表"

    async def get_balance_sheet(
        self, 
        stock_code: str, 
        indicator: str = "年度", 
        n_periods: int = 1
    ) -> StockDataResponse:
        """
        获取港股资产负债表
        
        Args:
            stock_code: 港股代码，支持多种格式：
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                - 系统会自动格式化为akshare需要的5位数格式
            indicator: 报告期类型，可选值：
                - "年度" (默认)
                - "中报" 
                - "季报"
            n_periods: 获取的期数，默认为1
            
        Returns:
            StockDataResponse对象，包含资产负债表数据
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        Examples:
            >>> await get_balance_sheet("700")  # 腾讯年度报告
            >>> await get_balance_sheet("0700.HK", "中报", 2)  # 腾讯中报，最近2期
        """
        try:
            logger.info(f"开始获取股票 {stock_code} 的资产负债表数据...")
            logger.info(f"报告期类型: {indicator}, 获取期数: {n_periods}")
            
            # 格式化股票代码
            akshare_code = self.format_akshare_stock_code(stock_code)
            logger.info(f"格式化后的akshare股票代码: {akshare_code}")
            
            # 1. 先从数据库获取
            logger.info("尝试从数据库获取数据...")
            db_data = self.db_manager.get_financial_data(stock_code, "资产负债表", indicator, n_periods)
            
            if not db_data.empty:
                logger.info(f"成功从数据库获取数据，共 {len(db_data)} 条记录")
                data = []
                for _, row in db_data.iterrows():
                    data.append({
                        "report_date": pd.to_datetime(row['report_date']).strftime('%Y-%m-%d'),
                        "item_name": row['item_name'],
                        "amount": self.db_manager.clean_amount(row['amount'])
                    })
                
                return StockDataResponse(
                    status="success",
                    message="",
                    data=data
                )
            
            # 2. 如果数据库没有，从 akshare 获取
            logger.info("数据库中没有数据，尝试从 akshare 获取...")
            df = ak.stock_financial_hk_report_em(stock=akshare_code, symbol="资产负债表", indicator=indicator)
            
            if df.empty:
                logger.info("从 akshare 获取数据失败，返回空数据")
                return StockDataResponse(
                    status="error",
                    message="从 akshare 获取数据失败",
                    data=[]
                )
            
            logger.info(f"成功从 akshare 获取数据，共 {len(df)} 条记录")
            
            # 3. 保存到数据库并返回数据
            logger.info("开始保存数据到数据库...")
            saved_df = self.db_manager.save_financial_data(stock_code, "资产负债表", indicator, df)
            
            if saved_df.empty:
                logger.info("数据保存到数据库失败")
                return StockDataResponse(
                    status="error",
                    message="数据保存到数据库失败",
                    data=[]
                )
                
            data = []
            for _, row in saved_df.iterrows():
                data.append({
                    "report_date": pd.to_datetime(row['report_date']).strftime('%Y-%m-%d'),
                    "item_name": row['item_name'],
                    "amount": self.db_manager.clean_amount(row['amount'])
                })
            
            logger.info("数据保存到数据库成功")
            return StockDataResponse(
                status="success",
                message="",
                data=data
            )
            
        except Exception as e:
            logger.error(f"获取资产负债表数据失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            return StockDataResponse(
                status="error",
                message=f"获取资产负债表数据失败: {str(e)}",
                data=[]
            )

    async def get_income_statement(
        self, 
        stock_code: str, 
        indicator: str = "年度", 
        n_periods: int = 1
    ) -> StockDataResponse:
        """
        获取港股利润表
        
        Args:
            stock_code: 港股代码，支持多种格式：
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                - 系统会自动格式化为akshare需要的5位数格式
            indicator: 报告期类型，可选值：
                - "年度" (默认)
                - "中报"
                - "季报"
            n_periods: 获取的期数，默认为1
            
        Returns:
            StockDataResponse对象，包含利润表数据
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        Examples:
            >>> await get_income_statement("700")  # 腾讯年度利润表
            >>> await get_income_statement("9988.HK", "季报", 4)  # 阿里巴巴季报，最近4期
        """
        try:
            logger.info(f"开始获取股票 {stock_code} 的利润表数据...")
            logger.info(f"报告期类型: {indicator}, 获取期数: {n_periods}")
            
            # 格式化股票代码
            akshare_code = self.format_akshare_stock_code(stock_code)
            logger.info(f"格式化后的akshare股票代码: {akshare_code}")
            
            # 1. 先从数据库获取
            logger.info("尝试从数据库获取数据...")
            db_data = self.db_manager.get_financial_data(stock_code, "利润表", indicator, n_periods)
            
            if not db_data.empty:
                logger.info(f"成功从数据库获取数据，共 {len(db_data)} 条记录")
                data = []
                for _, row in db_data.iterrows():
                    data.append({
                        "report_date": pd.to_datetime(row['report_date']).strftime('%Y-%m-%d'),
                        "item_name": row['item_name'],
                        "amount": self.db_manager.clean_amount(row['amount'])
                    })
                
                return StockDataResponse(
                    status="success",
                    message="",
                    data=data
                )
            
            # 2. 如果数据库没有，从 akshare 获取
            logger.info("数据库中没有数据，尝试从 akshare 获取...")
            df = ak.stock_financial_hk_report_em(stock=akshare_code, symbol="利润表", indicator=indicator)
            
            if df.empty:
                logger.info("从 akshare 获取数据失败，返回空数据")
                return StockDataResponse(
                    status="error",
                    message="从 akshare 获取数据失败",
                    data=[]
                )
            
            logger.info(f"成功从 akshare 获取数据，共 {len(df)} 条记录")
            
            # 3. 保存到数据库并返回数据
            logger.info("开始保存数据到数据库...")
            saved_df = self.db_manager.save_financial_data(stock_code, "利润表", indicator, df)
            
            if saved_df.empty:
                logger.info("数据保存到数据库失败")
                return StockDataResponse(
                    status="error",
                    message="数据保存到数据库失败",
                    data=[]
                )
                
            data = []
            for _, row in saved_df.iterrows():
                data.append({
                    "report_date": pd.to_datetime(row['report_date']).strftime('%Y-%m-%d'),
                    "item_name": row['item_name'],
                    "amount": self.db_manager.clean_amount(row['amount'])
                })
            
            logger.info("数据保存到数据库成功")
            return StockDataResponse(
                status="success",
                message="",
                data=data
            )
            
        except Exception as e:
            logger.error(f"获取利润表数据失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            return StockDataResponse(
                status="error",
                message=f"获取利润表数据失败: {str(e)}",
                data=[]
            )

    async def get_cash_flow(
        self, 
        stock_code: str, 
        indicator: str = "年度", 
        n_periods: int = 1
    ) -> StockDataResponse:
        """
        获取港股现金流量表
        
        Args:
            stock_code: 港股代码，支持多种格式：
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                - 系统会自动格式化为akshare需要的5位数格式
            indicator: 报告期类型，可选值：
                - "年度" (默认)
                - "中报"
                - "季报"
            n_periods: 获取的期数，默认为1
            
        Returns:
            StockDataResponse对象，包含现金流量表数据
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        Examples:
            >>> await get_cash_flow("700")  # 腾讯年度现金流量表
            >>> await get_cash_flow("1", "年度", 3)  # 长和年度现金流量表，最近3期
        """
        try:
            logger.info(f"开始获取股票 {stock_code} 的现金流量表数据...")
            logger.info(f"报告期类型: {indicator}, 获取期数: {n_periods}")
            
            # 格式化股票代码
            akshare_code = self.format_akshare_stock_code(stock_code)
            logger.info(f"格式化后的akshare股票代码: {akshare_code}")
            
            # 1. 先从数据库获取
            logger.info("尝试从数据库获取数据...")
            db_data = self.db_manager.get_financial_data(stock_code, "现金流量表", indicator, n_periods)
            
            if not db_data.empty:
                logger.info(f"成功从数据库获取数据，共 {len(db_data)} 条记录")
                data = []
                for _, row in db_data.iterrows():
                    data.append({
                        "report_date": pd.to_datetime(row['report_date']).strftime('%Y-%m-%d'),
                        "item_name": row['item_name'],
                        "amount": self.db_manager.clean_amount(row['amount'])
                    })
                
                return StockDataResponse(
                    status="success",
                    message="",
                    data=data
                )
            
            # 2. 如果数据库没有，从 akshare 获取
            logger.info("数据库中没有数据，尝试从 akshare 获取...")
            df = ak.stock_financial_hk_report_em(stock=akshare_code, symbol="现金流量表", indicator=indicator)
            
            if df.empty:
                logger.info("从 akshare 获取数据失败，返回空数据")
                return StockDataResponse(
                    status="error",
                    message="从 akshare 获取数据失败",
                    data=[]
                )
            
            logger.info(f"成功从 akshare 获取数据，共 {len(df)} 条记录")
            
            # 3. 保存到数据库并返回数据
            logger.info("开始保存数据到数据库...")
            saved_df = self.db_manager.save_financial_data(stock_code, "现金流量表", indicator, df)
            
            if saved_df.empty:
                logger.info("数据保存到数据库失败")
                return StockDataResponse(
                    status="error",
                    message="数据保存到数据库失败",
                    data=[]
                )
                
            data = []
            for _, row in saved_df.iterrows():
                data.append({
                    "report_date": pd.to_datetime(row['report_date']).strftime('%Y-%m-%d'),
                    "item_name": row['item_name'],
                    "amount": self.db_manager.clean_amount(row['amount'])
                })
            
            logger.info("数据保存到数据库成功")
            return StockDataResponse(
                status="success",
                message="",
                data=data
            )
            
        except Exception as e:
            logger.error(f"获取现金流量表数据失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            return StockDataResponse(
                status="error",
                message=f"获取现金流量表数据失败: {str(e)}",
                data=[]
            )

    async def get_financial_item(
        self, 
        stock_code: str, 
        item_names: Union[str, List[str]], 
        report_type: str = "资产负债表", 
        n_periods: int = 5, 
        indicator: str = "年度"
    ) -> StockDataResponse:
        """
        获取指定财务报表项目的数据
        
        Args:
            stock_code: 港股代码，支持多种格式：
                - 纯数字: "700", "0700", "00700" (腾讯)
                - 带后缀: "700.HK", "0700.HK", "00700.HK"
                - 系统会自动格式化为akshare需要的5位数格式
            item_names: 财务项目名称，支持以下格式：
                - 单个项目: "净资产"、"营业收入"、"现金流量净额"
                - 多个项目: ["净资产", "营业收入", "净利润"]
                - 支持模糊匹配，如"收入"可匹配"营业收入"
            report_type: 报表类型，可选值：
                - "资产负债表" (默认) - 包含资产、负债、所有者权益项目
                - "利润表" - 包含收入、成本、利润项目
                - "现金流量表" - 包含经营、投资、筹资现金流项目
            n_periods: 获取的期数，默认为5（获取最近5期数据）
            indicator: 报告期类型，可选值：
                - "年度" (默认)
                - "中报"
                - "季报"
            
        Returns:
            StockDataResponse对象，包含匹配的财务数据和匹配统计信息
            
        Raises:
            ValueError: 如果股票代码格式无效
            
        Examples:
            >>> await get_financial_item("700", "净资产")  # 腾讯净资产，最近5年
            >>> await get_financial_item("0700.HK", ["营业收入", "净利润"], "利润表", 3)  # 腾讯收入和利润，最近3年
            >>> await get_financial_item("9988", "现金流量净额", "现金流量表", 2, "中报")  # 阿里巴巴现金流，最近2期中报
        """
        try:
            # 将单个字符串转换为列表
            if isinstance(item_names, str):
                item_names = [item_names]
                
            logger.info(f"开始获取股票 {stock_code} 的 {report_type} - {', '.join(item_names)} 数据...")
            logger.info(f"报告期类型: {indicator}, 获取期数: {n_periods}")
            
            # 如果 report_type 未传或为空字符串，根据 item_names 自动判断
            if not report_type or report_type.strip() == "":
                report_type = self.infer_report_type_from_items(item_names)
                logger.info(f"未指定报表类型，系统自动推断为: {report_type}")

            # 根据报表类型调用相应的获取函数
            report_func = {
                "资产负债表": self.get_balance_sheet,
                "利润表": self.get_income_statement,
                "现金流量表": self.get_cash_flow
            }.get(report_type)
            
            if not report_func:
                return StockDataResponse(
                    status="error",
                    message=f"不支持的报表类型: {report_type}",
                    metadata={
                        "stock_code": stock_code,
                        "report_type": report_type,
                        "indicator": indicator,
                        "query_items": item_names,
                        "timestamp": datetime.now().isoformat()
                    },
                    data=[],
                    summary={
                        "total_records": 0,
                        "exact_matches": [],
                        "fuzzy_matches": {},
                        "missing_items": item_names
                    }
                )
            
            # 获取报表数据
            logger.info(f"获取{report_type}数据...")
            result = await report_func(stock_code, indicator, n_periods)
            
            if result.status == "error" or not result.data:
                logger.info(f"获取{report_type}数据失败，返回空数据")
                return StockDataResponse(
                    status="error",
                    message=f"获取{report_type}数据失败: {result.message}",
                    metadata={
                        "stock_code": stock_code,
                        "report_type": report_type,
                        "indicator": indicator,
                        "query_items": item_names,
                        "timestamp": datetime.now().isoformat()
                    },
                    data=[],
                    summary={
                        "total_records": 0,
                        "exact_matches": [],
                        "fuzzy_matches": {},
                        "missing_items": item_names
                    }
                )
            
            logger.info(f"成功获取{report_type}数据，共 {len(result.data)} 条记录")
            
            # 存储所有数据
            all_data = []
            exact_matches = set()
            fuzzy_matches = {}
            missing_items = set(item_names)
            
            # 对每个项目名称进行处理
            for item_name in item_names:
                logger.info(f"提取 {item_name} 数据...")
                has_exact_match = False
                current_fuzzy_matches = set()
                
                for row in result.data:
                    current_item_name = row["item_name"]
                    report_date = row["report_date"]
                    amount = row["amount"]
                    
                    if amount is None:
                        continue
                        
                    # 完全匹配
                    if current_item_name == item_name:
                        has_exact_match = True
                        all_data.append({
                            "report_date": report_date,
                            "item_name": current_item_name,
                            "amount": amount,
                            "match_type": "exact",
                            "query_item": item_name
                        })
                    # 模糊匹配：检查项目名称是否包含搜索词
                    elif item_name in current_item_name:
                        current_fuzzy_matches.add(current_item_name)
                        all_data.append({
                            "report_date": report_date,
                            "item_name": current_item_name,
                            "amount": amount,
                            "match_type": "fuzzy",
                            "query_item": item_name
                        })
                
                # 更新匹配结果
                if has_exact_match:
                    exact_matches.add(item_name)
                    missing_items.remove(item_name)
                elif current_fuzzy_matches:
                    fuzzy_matches[item_name] = sorted(list(current_fuzzy_matches))
                    missing_items.remove(item_name)
            
            # 构建返回结果
            response = StockDataResponse(
                status="success",
                message="部分项目使用了模糊匹配" if fuzzy_matches else "",
                metadata={
                    "stock_code": stock_code,
                    "report_type": report_type,
                    "indicator": indicator,
                    "query_items": item_names,
                    "timestamp": datetime.now().isoformat()
                },
                data=sorted(all_data, key=lambda x: (x["report_date"], x["item_name"]), reverse=True),
                summary={
                    "total_records": len(all_data),
                    "exact_matches": sorted(list(exact_matches)),
                    "fuzzy_matches": fuzzy_matches,
                    "missing_items": sorted(list(missing_items))
                }
            )
            
            return response
                
        except Exception as e:
            logger.error(f"获取数据失败: {str(e)}")
            import traceback
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            return StockDataResponse(
                status="error",
                message=f"获取数据失败: {str(e)}",
                metadata={
                    "stock_code": stock_code,
                    "report_type": report_type,
                    "indicator": indicator,
                    "query_items": item_names,
                    "timestamp": datetime.now().isoformat()
                },
                data=[],
                summary={
                    "total_records": 0,
                    "exact_matches": [],
                    "fuzzy_matches": {},
                    "missing_items": item_names
                }
            ) 
"""
股票代码验证器
提供股票代码的验证和格式化功能
"""

import re
from typing import Dict, Any, Optional, Tuple


class StockValidator:
    """股票代码验证器"""
    
    # 港股代码模式
    HK_PATTERNS = [
        r'^[0-9]{1,5}$',  # 1-5位数字 (akshare格式或原始输入)
        r'^[0-9]{1,5}\.HK$',  # 数字 + .HK (yfinance格式)
        r'^[0-9]{1,5}\.hk$',  # 数字 + .hk
    ]
    
    # A股代码模式
    A_STOCK_PATTERNS = [
        r'^[0-9]{6}$',  # 6位数字
        r'^[0-9]{6}\.SS$',  # 数字 + .SS (上海)
        r'^[0-9]{6}\.SZ$',  # 数字 + .SZ (深圳)
        r'^[0-9]{6}\.ss$',  # 数字 + .ss
        r'^[0-9]{6}\.sz$',  # 数字 + .sz
    ]
    
    # 美股代码模式
    US_STOCK_PATTERNS = [
        r'^[A-Z]{1,5}$',  # 1-5位字母
        r'^[A-Z]{1,5}\.[A-Z]{1,2}$',  # 字母 + 后缀
    ]
    
    @classmethod
    def validate_stock_code(cls, stock_code: str) -> Dict[str, Any]:
        """
        验证股票代码
        
        Args:
            stock_code: 股票代码
            
        Returns:
            验证结果字典
        """
        if not stock_code:
            return {
                "is_valid": False,
                "market": None,
                "formatted_code": None,
                "error": "股票代码不能为空"
            }
        
        stock_code = stock_code.strip().upper()
        
        # 检查港股
        hk_result = cls._validate_hk_stock(stock_code)
        if hk_result["is_valid"]:
            return hk_result
        
        # 检查A股
        a_stock_result = cls._validate_a_stock(stock_code)
        if a_stock_result["is_valid"]:
            return a_stock_result
        
        # 检查美股
        us_stock_result = cls._validate_us_stock(stock_code)
        if us_stock_result["is_valid"]:
            return us_stock_result
        
        return {
            "is_valid": False,
            "market": None,
            "formatted_code": None,
            "error": "无效的股票代码格式"
        }
    
    @classmethod
    def _validate_hk_stock(cls, stock_code: str) -> Dict[str, Any]:
        """验证港股代码"""
        for pattern in cls.HK_PATTERNS:
            if re.match(pattern, stock_code):
                # 提取数字部分
                if '.' in stock_code:
                    number_part = stock_code.split('.')[0]
                else:
                    number_part = stock_code
                
                # 验证数字部分是否为有效的港股代码
                try:
                    stock_num = int(number_part)
                    if stock_num <= 0 or stock_num > 99999:
                        return {"is_valid": False, "market": None, "formatted_code": None, "error": "港股代码数字部分必须在1-99999之间"}
                except ValueError:
                    return {"is_valid": False, "market": None, "formatted_code": None, "error": "港股代码必须为数字"}
                
                # 格式化为不同格式
                # yfinance格式: 标准4位数字 + .HK (去掉前导零后再补齐到4位)
                stock_num_int = int(number_part)
                yfinance_code = f"{stock_num_int:04d}.HK"
                # akshare格式: 5位数字，保持前导零
                akshare_code = f"{stock_num_int:05d}"
                
                return {
                    "is_valid": True,
                    "market": "HK",
                    "formatted_code": yfinance_code,  # 默认返回yfinance格式
                    "yfinance_format": yfinance_code,  # yfinance格式: 4位数字 + .HK
                    "akshare_format": akshare_code,   # akshare格式: 5位数字
                    "original_code": stock_code,
                    "error": None
                }
        
        return {"is_valid": False, "market": None, "formatted_code": None, "error": None}
    
    @classmethod
    def _validate_a_stock(cls, stock_code: str) -> Dict[str, Any]:
        """验证A股代码"""
        for pattern in cls.A_STOCK_PATTERNS:
            if re.match(pattern, stock_code):
                # 提取数字部分
                if '.' in stock_code:
                    number_part = stock_code.split('.')[0]
                    suffix = stock_code.split('.')[1].upper()
                else:
                    number_part = stock_code
                    # 根据代码前缀判断交易所
                    if number_part.startswith(('60', '68', '11', '50', '51', '52')):
                        suffix = 'SS'
                    else:
                        suffix = 'SZ'
                
                formatted_code = f"{number_part}.{suffix}"
                
                return {
                    "is_valid": True,
                    "market": "A",
                    "formatted_code": formatted_code,
                    "original_code": stock_code,
                    "error": None
                }
        
        return {"is_valid": False, "market": None, "formatted_code": None, "error": None}
    
    @classmethod
    def _validate_us_stock(cls, stock_code: str) -> Dict[str, Any]:
        """验证美股代码"""
        for pattern in cls.US_STOCK_PATTERNS:
            if re.match(pattern, stock_code):
                return {
                    "is_valid": True,
                    "market": "US",
                    "formatted_code": stock_code,
                    "original_code": stock_code,
                    "error": None
                }
        
        return {"is_valid": False, "market": None, "formatted_code": None, "error": None}
    
    @classmethod
    def format_stock_code(cls, stock_code: str) -> str:
        """
        格式化股票代码 (默认格式)
        
        Args:
            stock_code: 原始股票代码
            
        Returns:
            格式化后的股票代码
            
        Raises:
            ValueError: 如果股票代码无效
        """
        result = cls.validate_stock_code(stock_code)
        
        if not result["is_valid"]:
            raise ValueError(result["error"])
        
        return result["formatted_code"]
    
    @classmethod
    def format_for_yfinance(cls, stock_code: str) -> str:
        """
        格式化股票代码为yfinance格式
        
        Args:
            stock_code: 原始股票代码
            
        Returns:
            yfinance格式的股票代码
            
        Raises:
            ValueError: 如果股票代码无效
        """
        result = cls.validate_stock_code(stock_code)
        
        if not result["is_valid"]:
            raise ValueError(f"无效的股票代码: {result['error']}")
        
        if result["market"] == "HK":
            return result["yfinance_format"]
        else:
            return result["formatted_code"]
    
    @classmethod
    def format_for_akshare(cls, stock_code: str) -> str:
        """
        格式化股票代码为akshare格式
        
        Args:
            stock_code: 原始股票代码
            
        Returns:
            akshare格式的股票代码
            
        Raises:
            ValueError: 如果股票代码无效
        """
        result = cls.validate_stock_code(stock_code)
        
        if not result["is_valid"]:
            raise ValueError(f"无效的股票代码: {result['error']}")
        
        if result["market"] == "HK":
            return result["akshare_format"]
        else:
            return result["formatted_code"]
    
    @classmethod
    def get_market_info(cls, stock_code: str) -> Dict[str, Any]:
        """
        获取市场信息
        
        Args:
            stock_code: 股票代码
            
        Returns:
            市场信息字典
        """
        result = cls.validate_stock_code(stock_code)
        
        if not result["is_valid"]:
            return result
        
        market_info = {
            "HK": {
                "name": "香港交易所",
                "currency": "HKD",
                "timezone": "Asia/Hong_Kong",
                "trading_hours": "09:30-16:00"
            },
            "A": {
                "name": "中国A股",
                "currency": "CNY",
                "timezone": "Asia/Shanghai",
                "trading_hours": "09:30-15:00"
            },
            "US": {
                "name": "美国股市",
                "currency": "USD",
                "timezone": "America/New_York",
                "trading_hours": "09:30-16:00"
            }
        }
        
        result["market_info"] = market_info.get(result["market"], {})
        return result
    
    @classmethod
    def get_both_formats(cls, stock_code: str) -> Dict[str, Any]:
        """
        获取股票代码的两种格式
        
        Args:
            stock_code: 原始股票代码
            
        Returns:
            包含两种格式的字典
            
        Raises:
            ValueError: 如果股票代码无效
        """
        result = cls.validate_stock_code(stock_code)
        
        if not result["is_valid"]:
            raise ValueError(f"无效的股票代码: {result['error']}")
        
        if result["market"] == "HK":
            return {
                "is_valid": True,
                "market": result["market"],
                "original_code": stock_code,
                "yfinance_format": result["yfinance_format"],
                "akshare_format": result["akshare_format"],
                "formats": {
                    "yfinance": {
                        "code": result["yfinance_format"],
                        "description": "yfinance格式: 4位数字 + .HK后缀"
                    },
                    "akshare": {
                        "code": result["akshare_format"],
                        "description": "akshare格式: 5位数字，无后缀"
                    }
                }
            }
        else:
            return {
                "is_valid": True,
                "market": result["market"],
                "original_code": stock_code,
                "formatted_code": result["formatted_code"],
                "formats": {
                    "default": {
                        "code": result["formatted_code"],
                        "description": f"{result['market']}股市格式"
                    }
                }
            } 
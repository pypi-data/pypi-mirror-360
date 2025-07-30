"""
数据库管理器
提供DuckDB数据库的连接、管理和数据过期机制
"""

import os
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器，负责DuckDB数据库的连接和管理"""
    
    def __init__(self, db_path: Optional[str] = None, auto_cleanup: bool = True):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径，如果为None则使用默认路径
            auto_cleanup: 是否启用自动清理过期数据，默认为True
        """
        if db_path is None:
            # 使用包目录下的数据库文件
            package_dir = Path(__file__).parent.parent
            db_path = package_dir / "data" / "finance_data.duckdb"
            
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.auto_cleanup = auto_cleanup
        self._last_cleanup_time = None
        
        # 确保数据目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._setup_database()
        
        # 初始化时执行一次清理
        if self.auto_cleanup:
            self._auto_cleanup_if_needed()
        
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """获取数据库连接"""
        return duckdb.connect(str(self.db_path))
    
    def _setup_database(self) -> None:
        """设置数据库表结构"""
        conn = self.get_connection()
        
        # 创建财务报表数据表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hk_financial_reports (
                stock_code VARCHAR,
                report_type VARCHAR,
                report_period VARCHAR,
                report_date DATE,
                item_name VARCHAR,
                amount FLOAT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_expired BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (stock_code, report_type, report_period, report_date, item_name)
            )
        """)
        
        # 创建公司信息表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS company_info (
                stock_code VARCHAR PRIMARY KEY,
                company_name VARCHAR,
                sector VARCHAR,
                industry VARCHAR,
                market_cap FLOAT,
                employee_count INTEGER,
                info_json TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_expired BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 创建股息分红表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dividend_actions (
                stock_code VARCHAR,
                action_date DATE,
                action_type VARCHAR,
                dividend_amount FLOAT,
                stock_splits VARCHAR,
                created_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_expired BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (stock_code, action_date, action_type)
            )
        """)
        
        # 创建数据过期配置表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS data_expiry_config (
                data_type VARCHAR PRIMARY KEY,
                expiry_hours INTEGER,
                description VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入默认的数据过期配置
        conn.execute("""
            INSERT OR REPLACE INTO data_expiry_config (data_type, expiry_hours, description)
            VALUES 
                ('financial_reports', 24, '财务报表数据24小时过期'),
                ('company_info', 168, '公司信息数据一周过期'),
                ('dividend_actions', 72, '分红数据3天过期')
        """)
        
        conn.close()
        logger.info("数据库初始化完成")
    
    def clean_amount(self, amount: Any) -> Optional[float]:
        """清理金额数据"""
        if pd.isna(amount) or np.isinf(amount):
            return None
        try:
            return float(amount)
        except (ValueError, TypeError):
            return None
    
    def is_data_expired(self, data_type: str, created_at: datetime) -> bool:
        """检查数据是否过期"""
        conn = self.get_connection()
        
        # 获取过期配置
        result = conn.execute("""
            SELECT expiry_hours FROM data_expiry_config 
            WHERE data_type = ?
        """, [data_type]).fetchone()
        
        if not result:
            # 默认24小时过期
            expiry_hours = 24
        else:
            expiry_hours = result[0]
        
        conn.close()
        
        # 计算是否过期
        expiry_time = created_at + timedelta(hours=expiry_hours)
        return datetime.now() > expiry_time
    
    def mark_expired_data(self, data_type: str) -> int:
        """标记过期数据"""
        conn = self.get_connection()
        
        # 获取过期配置
        result = conn.execute("""
            SELECT expiry_hours FROM data_expiry_config 
            WHERE data_type = ?
        """, [data_type]).fetchone()
        
        if not result:
            expiry_hours = 24
        else:
            expiry_hours = result[0]
        
        # 计算过期时间点
        expiry_cutoff = datetime.now() - timedelta(hours=expiry_hours)
        
        # 根据数据类型标记过期数据
        if data_type == "financial_reports":
            result = conn.execute("""
                UPDATE hk_financial_reports 
                SET is_expired = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE created_at < ? AND is_expired = FALSE
            """, [expiry_cutoff])
        elif data_type == "company_info":
            result = conn.execute("""
                UPDATE company_info 
                SET is_expired = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE created_at < ? AND is_expired = FALSE
            """, [expiry_cutoff])
        elif data_type == "dividend_actions":
            result = conn.execute("""
                UPDATE dividend_actions 
                SET is_expired = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE created_at < ? AND is_expired = FALSE
            """, [expiry_cutoff])
        
        affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
        conn.close()
        
        logger.info(f"标记了 {affected_rows} 条 {data_type} 数据为过期")
        return affected_rows
    
    def cleanup_expired_data(self, data_type: str, keep_days: int = 30) -> int:
        """清理过期数据，保留指定天数"""
        conn = self.get_connection()
        
        # 计算清理时间点
        cleanup_cutoff = datetime.now() - timedelta(days=keep_days)
        
        # 根据数据类型清理数据
        if data_type == "financial_reports":
            result = conn.execute("""
                DELETE FROM hk_financial_reports 
                WHERE is_expired = TRUE AND updated_at < ?
            """, [cleanup_cutoff])
        elif data_type == "company_info":
            result = conn.execute("""
                DELETE FROM company_info 
                WHERE is_expired = TRUE AND updated_at < ?
            """, [cleanup_cutoff])
        elif data_type == "dividend_actions":
            result = conn.execute("""
                DELETE FROM dividend_actions 
                WHERE is_expired = TRUE AND updated_at < ?
            """, [cleanup_cutoff])
        
        affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
        conn.close()
        
        logger.info(f"清理了 {affected_rows} 条 {data_type} 过期数据")
        return affected_rows
    
    def _auto_cleanup_if_needed(self) -> None:
        """自动清理过期数据（如果需要的话）"""
        if not self.auto_cleanup:
            return
            
        # 检查是否需要清理（每天最多清理一次）
        now = datetime.now()
        if (self._last_cleanup_time is None or 
            (now - self._last_cleanup_time).total_seconds() > 86400):  # 24小时
            
            logger.info("开始自动清理过期数据...")
            try:
                # 标记并清理所有类型的过期数据
                total_cleaned = 0
                for data_type in ["financial_reports", "company_info", "dividend_actions"]:
                    self.mark_expired_data(data_type)
                    cleaned = self.cleanup_expired_data(data_type, keep_days=7)  # 保留7天
                    total_cleaned += cleaned
                
                self._last_cleanup_time = now
                logger.info(f"自动清理完成，共清理 {total_cleaned} 条过期数据")
            except Exception as e:
                logger.error(f"自动清理过期数据失败: {e}")
    
    def _trigger_auto_cleanup_on_query(self) -> None:
        """在查询时触发自动清理检查"""
        if self.auto_cleanup:
            self._auto_cleanup_if_needed()
    
    def get_financial_data(
        self, 
        stock_code: str, 
        report_type: str, 
        report_period: str, 
        n_periods: int = 1,
        include_expired: bool = False
    ) -> pd.DataFrame:
        """获取财务数据"""
        conn = self.get_connection()
        
        # 触发自动清理检查
        self._trigger_auto_cleanup_on_query()
        
        # 标记过期数据
        self.mark_expired_data("financial_reports")
        
        # 构建查询条件
        expired_condition = "" if include_expired else "AND is_expired = FALSE"
        
        query = f"""
            WITH distinct_dates AS (
                SELECT DISTINCT report_date
                FROM hk_financial_reports
                WHERE stock_code = ?
                AND report_type = ?
                AND report_period = ?
                {expired_condition}
                ORDER BY report_date DESC
                LIMIT ?
            )
            SELECT DISTINCT r.*
            FROM hk_financial_reports r
            JOIN distinct_dates d ON r.report_date = d.report_date
            WHERE r.stock_code = ?
            AND r.report_type = ?
            AND r.report_period = ?
            {expired_condition}
            ORDER BY r.report_date DESC, r.item_name DESC
        """
        
        result = conn.execute(query, [
            stock_code, report_type, report_period, n_periods,
            stock_code, report_type, report_period
        ]).fetchdf()
        
        conn.close()
        return result
    
    def save_financial_data(
        self, 
        stock_code: str, 
        report_type: str, 
        report_period: str, 
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """保存财务数据到数据库"""
        conn = self.get_connection()
        
        # 准备数据
        data = []
        for _, row in df.iterrows():
            data.append({
                'stock_code': stock_code,
                'report_type': report_type,
                'report_period': report_period,
                'report_date': pd.to_datetime(row['REPORT_DATE']) if 'REPORT_DATE' in row else pd.to_datetime(row['STD_REPORT_DATE']),
                'item_name': row['ITEM_NAME'] if 'ITEM_NAME' in row else row['STD_ITEM_NAME'],
                'amount': self.clean_amount(row['AMOUNT']) if 'AMOUNT' in row else self.clean_amount(row['AMOUNT_CNY']),
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'is_expired': False
            })
        
        # 批量插入数据
        if data:
            logger.info(f"准备插入 {len(data)} 行数据到 hk_financial_reports 表")
            for d in data:
                conn.execute("""
                    INSERT INTO hk_financial_reports 
                    (stock_code, report_type, report_period, report_date, item_name, amount, created_at, updated_at, is_expired)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (stock_code, report_type, report_period, report_date, item_name) 
                    DO UPDATE SET 
                        amount = excluded.amount, 
                        updated_at = excluded.updated_at,
                        is_expired = FALSE
                """, (
                    d['stock_code'], d['report_type'], d['report_period'], 
                    d['report_date'], d['item_name'], d['amount'], 
                    d['created_at'], d['updated_at'], d['is_expired']
                ))
            logger.info(f"成功插入 {len(data)} 行数据到 hk_financial_reports 表")
        
        # 获取插入的数据
        result = self.get_financial_data(stock_code, report_type, report_period, n_periods=10)
        conn.close()
        
        return result
    
    def save_company_info(self, stock_code: str, info_data: Dict[str, Any]) -> bool:
        """保存公司信息"""
        conn = self.get_connection()
        
        # 标记过期数据
        self.mark_expired_data("company_info")
        
        try:
            import json
            conn.execute("""
                INSERT INTO company_info 
                (stock_code, company_name, sector, industry, market_cap, employee_count, info_json, created_at, updated_at, is_expired)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (stock_code) 
                DO UPDATE SET 
                    company_name = excluded.company_name,
                    sector = excluded.sector,
                    industry = excluded.industry,
                    market_cap = excluded.market_cap,
                    employee_count = excluded.employee_count,
                    info_json = excluded.info_json,
                    updated_at = excluded.updated_at,
                    is_expired = FALSE
            """, (
                stock_code,
                info_data.get('longName', ''),
                info_data.get('sector', ''),
                info_data.get('industry', ''),
                self.clean_amount(info_data.get('marketCap')),
                info_data.get('fullTimeEmployees'),
                json.dumps(info_data, ensure_ascii=False),
                datetime.now(),
                datetime.now(),
                False
            ))
            conn.close()
            logger.info(f"成功保存公司信息: {stock_code}")
            return True
        except Exception as e:
            logger.error(f"保存公司信息失败: {e}")
            conn.close()
            return False
    
    def get_company_info(self, stock_code: str, include_expired: bool = False) -> Optional[Dict[str, Any]]:
        """获取公司信息"""
        conn = self.get_connection()
        
        # 触发自动清理检查
        self._trigger_auto_cleanup_on_query()
        
        # 标记过期数据
        self.mark_expired_data("company_info")
        
        expired_condition = "" if include_expired else "AND is_expired = FALSE"
        
        result = conn.execute(f"""
            SELECT * FROM company_info 
            WHERE stock_code = ? {expired_condition}
        """, [stock_code]).fetchone()
        
        conn.close()
        
        if result:
            import json
            return {
                'stock_code': result[0],
                'company_name': result[1],
                'sector': result[2],
                'industry': result[3],
                'market_cap': result[4],
                'employee_count': result[5],
                'info_json': json.loads(result[6]) if result[6] else {},
                'created_at': result[7],
                'updated_at': result[8],
                'is_expired': result[9]
            }
        return None
    
    def save_dividend_actions(self, stock_code: str, actions_df: pd.DataFrame) -> bool:
        """保存分红行为数据"""
        conn = self.get_connection()
        
        # 标记过期数据
        self.mark_expired_data("dividend_actions")
        
        try:
            for _, row in actions_df.iterrows():
                action_date = pd.to_datetime(row.name).date()
                
                # 处理分红和股票拆分
                dividend_amount = self.clean_amount(row.get('Dividends', 0))
                stock_splits = str(row.get('Stock Splits', '')) if row.get('Stock Splits') else None
                
                # 确定行为类型
                if dividend_amount and dividend_amount > 0:
                    action_type = 'dividend'
                elif stock_splits and stock_splits != '0.0':
                    action_type = 'stock_split'
                else:
                    continue
                
                conn.execute("""
                    INSERT INTO dividend_actions 
                    (stock_code, action_date, action_type, dividend_amount, stock_splits, created_at, updated_at, is_expired)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (stock_code, action_date, action_type) 
                    DO UPDATE SET 
                        dividend_amount = excluded.dividend_amount,
                        stock_splits = excluded.stock_splits,
                        updated_at = excluded.updated_at,
                        is_expired = FALSE
                """, (
                    stock_code, action_date, action_type, dividend_amount, stock_splits,
                    datetime.now(), datetime.now(), False
                ))
            
            conn.close()
            logger.info(f"成功保存分红数据: {stock_code}")
            return True
        except Exception as e:
            logger.error(f"保存分红数据失败: {e}")
            conn.close()
            return False
    
    def get_dividend_actions(self, stock_code: str, include_expired: bool = False) -> pd.DataFrame:
        """获取分红行为数据"""
        conn = self.get_connection()
        
        # 触发自动清理检查
        self._trigger_auto_cleanup_on_query()
        
        # 标记过期数据
        self.mark_expired_data("dividend_actions")
        
        expired_condition = "" if include_expired else "AND is_expired = FALSE"
        
        result = conn.execute(f"""
            SELECT * FROM dividend_actions 
            WHERE stock_code = ? {expired_condition}
            ORDER BY action_date DESC
        """, [stock_code]).fetchdf()
        
        conn.close()
        return result 
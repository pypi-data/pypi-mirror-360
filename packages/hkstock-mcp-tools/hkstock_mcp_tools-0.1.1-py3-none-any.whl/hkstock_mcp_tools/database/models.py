"""
数据模型定义
定义财务数据的数据结构和验证规则
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator


class FinancialReportData(BaseModel):
    """财务报表数据模型"""
    stock_code: str = Field(..., description="股票代码")
    report_type: str = Field(..., description="报表类型")
    report_period: str = Field(..., description="报告期")
    report_date: date = Field(..., description="报告日期")
    item_name: str = Field(..., description="项目名称")
    amount: Optional[float] = Field(None, description="金额")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    is_expired: bool = Field(False, description="是否过期")

    @validator('report_type')
    def validate_report_type(cls, v):
        valid_types = ['资产负债表', '利润表', '现金流量表']
        if v not in valid_types:
            raise ValueError(f'报表类型必须是 {valid_types} 中的一种')
        return v

    @validator('report_period')
    def validate_report_period(cls, v):
        valid_periods = ['年度', '半年度', '季度']
        if v not in valid_periods:
            raise ValueError(f'报告期必须是 {valid_periods} 中的一种')
        return v


class CompanyInfo(BaseModel):
    """公司信息模型"""
    stock_code: str = Field(..., description="股票代码")
    company_name: Optional[str] = Field(None, description="公司名称")
    sector: Optional[str] = Field(None, description="行业板块")
    industry: Optional[str] = Field(None, description="具体行业")
    market_cap: Optional[float] = Field(None, description="市值")
    employee_count: Optional[int] = Field(None, description="员工数量")
    info_json: Dict[str, Any] = Field(default_factory=dict, description="完整信息JSON")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    is_expired: bool = Field(False, description="是否过期")


class DividendAction(BaseModel):
    """分红行为模型"""
    stock_code: str = Field(..., description="股票代码")
    action_date: date = Field(..., description="行为日期")
    action_type: str = Field(..., description="行为类型")
    dividend_amount: Optional[float] = Field(None, description="分红金额")
    stock_splits: Optional[str] = Field(None, description="股票拆分")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    is_expired: bool = Field(False, description="是否过期")

    @validator('action_type')
    def validate_action_type(cls, v):
        valid_types = ['dividend', 'stock_split']
        if v not in valid_types:
            raise ValueError(f'行为类型必须是 {valid_types} 中的一种')
        return v


class StockDataResponse(BaseModel):
    """股票数据响应模型"""
    status: str = Field(..., description="状态")
    message: str = Field("", description="消息")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="数据")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    summary: Optional[Dict[str, Any]] = Field(None, description="摘要")


class DataExpiryConfig(BaseModel):
    """数据过期配置模型"""
    data_type: str = Field(..., description="数据类型")
    expiry_hours: int = Field(..., description="过期小时数")
    description: str = Field("", description="描述")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间") 
# HKStock MCP Tools

港股数据MCP工具包，提供港股财务数据和基本面数据的获取和管理功能。

## 功能特性

### 📊 财务报表数据
- **三大财务报表**: 资产负债表、利润表、现金流量表
- **数据来源**: akshare
- **数据缓存**: DuckDB本地缓存，提高查询效率
- **数据过期机制**: 自动管理数据时效性
- **智能匹配**: 支持财务指标的精确匹配和模糊匹配

### 🏢 企业基本面数据
- **公司信息**: 使用yfinance获取企业基本信息
- **分红拆股**: 历史分红和拆股记录
- **估值指标**: PE、PB、ROE等财务指标
- **价格数据**: 实时价格、成交量、52周高低点

### 🔧 技术特性
- **MCP协议**: 标准的Model Context Protocol接口
- **数据持久化**: DuckDB高性能本地数据库
- **数据过期管理**: 自动标记和清理过期数据
- **股票代码验证**: 支持港股、A股、美股代码格式
- **异步处理**: 高效的异步数据获取

## 安装

### 从PyPI安装（推荐）
```bash
pip install hkstock-mcp-tools
```

### 从源码安装
```bash
git clone https://github.com/your-username/hkstock-mcp-tools.git
cd hkstock-mcp-tools
pip install -e .
```

## 快速开始

### 1. 命令行启动MCP服务器
```bash
# 基本启动
hkstock-mcp --transport stdio

# 指定数据库路径
hkstock-mcp --transport stdio --db-path /path/to/custom.db

# 调试模式
hkstock-mcp --transport stdio --log-level DEBUG
```

### 2. Python代码中使用
```python
from hkstock_mcp_tools import HKStockMCPServer

# 创建服务器实例
server = HKStockMCPServer()

# 运行服务器
server.run(transport='stdio')
```

## MCP工具说明

### 财务报表工具

#### 1. get_hk_balance_sheet
获取港股资产负债表数据

**参数**:
- `stock`: 股票代码（如"0700"、"00700"）
- `indicator`: 报告期类型（"年度"、"半年度"、"季度"），默认"年度"
- `n_periods`: 获取期数，默认1

**示例**:
```json
{
  "status": "success",
  "data": [
    {
      "report_date": "2023-12-31",
      "item_name": "总资产",
      "amount": 1234567890.0
    }
  ]
}
```

#### 2. get_hk_income_statement
获取港股利润表数据

**参数**: 同资产负债表

#### 3. get_hk_cash_flow
获取港股现金流量表数据

**参数**: 同资产负债表

#### 4. get_financial_item
获取指定财务项目的历史数据

**参数**:
- `stock`: 股票代码
- `item_names`: 项目名称，多个用逗号分隔（如"净资产,营业收入"）
- `report_type`: 报表类型（"资产负债表"、"利润表"、"现金流量表"）
- `n_periods`: 获取期数，默认5
- `indicator`: 报告期类型，默认"年度"

**示例**:
```json
{
  "status": "success",
  "metadata": {
    "stock_code": "0700",
    "report_type": "利润表",
    "query_items": ["营业收入", "净利润"]
  },
  "data": [
    {
      "report_date": "2023-12-31",
      "item_name": "营业收入",
      "amount": 609896000000.0,
      "match_type": "exact",
      "query_item": "营业收入"
    }
  ],
  "summary": {
    "total_records": 10,
    "exact_matches": ["营业收入"],
    "fuzzy_matches": {},
    "missing_items": []
  }
}
```

### 企业基本面工具

#### 1. get_company_info
获取公司基本信息

**参数**:
- `stock`: 股票代码（支持港股、A股、美股）
- `force_refresh`: 是否强制刷新，默认False

**示例**:
```json
{
  "status": "success",
  "data": {
    "basic_info": {
      "symbol": "0700.HK",
      "shortName": "TENCENT",
      "longName": "Tencent Holdings Limited",
      "sector": "Communication Services",
      "industry": "Internet Content & Information",
      "country": "China",
      "website": "https://www.tencent.com",
      "fullTimeEmployees": 116213
    },
    "financial_metrics": {
      "marketCap": 3200000000000,
      "trailingPE": 25.5,
      "forwardPE": 22.1,
      "priceToBook": 3.2,
      "returnOnAssets": 0.095,
      "returnOnEquity": 0.16
    },
    "price_info": {
      "currentPrice": 320.5,
      "previousClose": 318.2,
      "fiftyTwoWeekLow": 245.0,
      "fiftyTwoWeekHigh": 398.8,
      "volume": 12500000
    },
    "dividend_info": {
      "dividendRate": 2.4,
      "dividendYield": 0.75,
      "payoutRatio": 0.3
    }
  }
}
```

#### 2. get_dividend_actions
获取分红拆股历史数据

**参数**:
- `stock`: 股票代码
- `force_refresh`: 是否强制刷新，默认False

**示例**:
```json
{
  "status": "success",
  "data": [
    {
      "date": "2024-05-15",
      "type": "dividend",
      "dividend_amount": 0.6,
      "stock_splits": null
    },
    {
      "date": "2020-05-11",
      "type": "stock_split",
      "dividend_amount": null,
      "stock_splits": "5:1"
    }
  ]
}
```

#### 3. get_stock_summary
获取股票综合信息汇总

**参数**:
- `stock`: 股票代码
- `force_refresh`: 是否强制刷新，默认False

### 辅助工具

#### 1. validate_stock_code
验证股票代码格式

**参数**:
- `stock`: 股票代码

**示例**:
```json
{
  "is_valid": true,
  "market": "HK",
  "formatted_code": "00700.HK",
  "original_code": "0700",
  "market_info": {
    "name": "香港交易所",
    "currency": "HKD",
    "timezone": "Asia/Hong_Kong",
    "trading_hours": "09:30-16:00"
  }
}
```

#### 2. cleanup_expired_data
清理过期数据

**参数**:
- `data_type`: 数据类型（"financial_reports"、"company_info"、"dividend_actions"、"all"）
- `keep_days`: 保留天数，默认30

## 支持的股票代码格式

### 港股
- `0700`、`00700` → `00700.HK`
- `700` → `00700.HK`

### A股
- `000001` → `000001.SZ`（深圳）
- `600000` → `600000.SS`（上海）

### 美股
- `AAPL` → `AAPL`
- `MSFT` → `MSFT`

## 数据过期和清理机制

### 数据过期时间
- **财务报表数据**: 24小时过期
- **公司信息数据**: 7天过期
- **分红行为数据**: 3天过期

### 自动清理机制
- **自动清理**: 系统每天自动清理过期数据（保留7天）
- **触发时机**: 
  - 服务器启动时
  - 每次查询数据时检查（每天最多清理一次）
- **清理策略**: 只删除已标记为过期且超过保留期的数据

### 手动清理
可通过 `cleanup_expired_data` 工具手动清理过期数据或自定义保留天数。

### 配置选项
```python
# 启用自动清理（默认）
server = HKStockMCPServer(auto_cleanup=True)

# 禁用自动清理
server = HKStockMCPServer(auto_cleanup=False)
```

## 开发指南

### 项目结构
```
hkstock_mcp_tools/
├── __init__.py              # 包初始化
├── cli.py                   # 命令行接口
├── core/                    # 核心模块
│   ├── __init__.py
│   └── mcp_server.py        # MCP服务器实现
├── database/                # 数据库模块
│   ├── __init__.py
│   ├── db_manager.py        # 数据库管理器
│   └── models.py            # 数据模型
├── tools/                   # 工具模块
│   ├── __init__.py
│   ├── financial_reports.py # 财务报表工具
│   ├── yfinance_tools.py    # YFinance工具
│   └── stock_validator.py   # 股票代码验证器
└── utils/                   # 工具函数
    └── __init__.py
```

### 运行测试
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行覆盖率测试
pytest --cov=hkstock_mcp_tools
```

### 代码格式化
```bash
# 格式化代码
black hkstock_mcp_tools/
isort hkstock_mcp_tools/

# 类型检查
mypy hkstock_mcp_tools/
```

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 更新日志

### v0.1.0
- 初始版本发布
- 支持港股三大财务报表数据获取
- 支持YFinance企业信息和分红数据
- 实现数据过期机制
- 提供MCP标准接口

## 支持

如有问题，请提交Issue或联系开发者。 
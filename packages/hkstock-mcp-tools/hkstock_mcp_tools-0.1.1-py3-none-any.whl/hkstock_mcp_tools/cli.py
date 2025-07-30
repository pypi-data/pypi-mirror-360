"""
命令行接口
提供命令行启动MCP服务器的入口点
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from .core.mcp_server import HKStockMCPServer


def setup_logging(level: str = "INFO"):
    """设置日志配置"""
    log_level = getattr(logging, level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ]
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="港股数据MCP服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s --transport stdio
  %(prog)s --transport stdio --db-path /path/to/custom.db
  %(prog)s --transport stdio --log-level DEBUG
        """,
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="传输方式 (默认: stdio)",
    )
    
    parser.add_argument(
        "--db-path",
        type=str,
        help="数据库文件路径 (默认: 包目录下的data/finance_data.duckdb)",
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别 (默认: INFO)",
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    
    # 创建并运行服务器
    try:
        server = HKStockMCPServer(db_path=args.db_path)
        server.run(transport=args.transport)
    except KeyboardInterrupt:
        print("\n服务器已停止", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 
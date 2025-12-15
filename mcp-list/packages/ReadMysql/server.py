import asyncio
import json
import sys
import os
from typing import Any
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import logging

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    # 设置标准输出和错误输出为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 新的导入 - 使用重构后的模块
from config.settings import get_settings, Settings
from core.connection_pool import ConnectionPool
from core.exceptions import MySQLError, ConfigurationError
from database.operations import DatabaseOperations
from core.query_logger import get_logger

# MCP 扩展功能
from mcp_extensions.resources import register_resources
from mcp_extensions.prompts import register_prompts
from mcp_extensions.export_tools import register_export_tools
from mcp_extensions.performance_tools import register_performance_tools
from mcp_extensions.documentation_tools import register_documentation_tools

# 配置日志输出到文件，避免干扰 MCP stdio 通信
log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'mcp_server.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        # 仅在非 MCP 模式下输出到 stderr
        logging.StreamHandler(sys.stderr) if os.environ.get('DEBUG_MODE') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)
query_logger = get_logger()

# 全局变量
_db_ops: DatabaseOperations = None
_settings: Settings = None


def initialize_infrastructure() -> DatabaseOperations:
    """
    初始化基础设施（配置、连接池、数据库操作）

    Returns:
        DatabaseOperations 实例

    Raises:
        ConfigurationError: 配置初始化失败
    """
    global _db_ops, _settings

    if _db_ops is not None:
        logger.info("数据库操作已初始化，跳过重复初始化")
        return _db_ops

    try:
        logger.info("=" * 60)
        logger.info("开始初始化 MySQL Reader MCP 服务器...")
        logger.info("=" * 60)

        # 1. 加载配置
        logger.info("步骤 1/3: 加载配置...")
        _settings = get_settings()
        logger.info(f"✓ 配置加载成功 (环境: {_settings.environment})")

        # 2. 初始化连接池
        logger.info("步骤 2/3: 初始化连接池...")
        pool = ConnectionPool()
        pool.initialize(_settings)
        logger.info("✓ 连接池初始化成功")

        # 3. 创建数据库操作实例
        logger.info("步骤 3/3: 创建数据库操作实例...")
        _db_ops = DatabaseOperations(pool)
        logger.info("✓ 数据库操作实例创建成功")

        logger.info("=" * 60)
        logger.info("✓ MySQL Reader MCP 服务器初始化完成")
        logger.info("=" * 60)

        return _db_ops

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"✗ 服务器初始化失败: {str(e)}")
        logger.error("=" * 60)
        raise ConfigurationError(
            f"服务器初始化失败: {str(e)}",
            original_error=e
        ) from e


# 创建 MCP 服务器实例
server = Server("mysql-reader")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    定义可用的 MCP 工具列表
    """
    return [
        Tool(
            name="list_databases",
            description="获取 MySQL 服务器上的所有数据库列表",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_tables",
            description="获取指定数据库中的所有表列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "数据库名称"
                    }
                },
                "required": ["database"]
            }
        ),
        Tool(
            name="describe_table",
            description="获取指定表的结构信息（字段名、类型、键等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "数据库名称"
                    },
                    "table": {
                        "type": "string",
                        "description": "表名称"
                    }
                },
                "required": ["database", "table"]
            }
        ),
        Tool(
            name="query_database",
            description="在指定数据库上执行 SELECT 查询（只读操作）",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "数据库名称"
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT 查询语句"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "限制返回的行数（可选，默认 1000）",
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "required": ["database", "query"]
            }
        ),
        Tool(
            name="get_table_info",
            description="获取表的完整信息，包括结构、行数和创建语句",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "数据库名称"
                    },
                    "table": {
                        "type": "string",
                        "description": "表名称"
                    }
                },
                "required": ["database", "table"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """
    处理工具调用请求
    """
    # 确保基础设施已初始化
    db_ops = _db_ops or initialize_infrastructure()

    try:
        if name == "list_databases":
            # 获取数据库列表
            databases = await asyncio.to_thread(db_ops.list_databases)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "databases": databases,
                        "count": len(databases)
                    }, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "list_tables":
            # 获取表列表
            database = arguments.get("database")
            if not database:
                raise ValueError("缺少必需参数: database")

            tables = await asyncio.to_thread(db_ops.list_tables, database)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "database": database,
                        "tables": tables,
                        "count": len(tables)
                    }, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "describe_table":
            # 获取表结构
            database = arguments.get("database")
            table = arguments.get("table")

            if not database or not table:
                raise ValueError("缺少必需参数: database 和 table")

            structure = await asyncio.to_thread(db_ops.describe_table, database, table)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "database": database,
                        "table": table,
                        "structure": structure
                    }, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "query_database":
            # 执行查询
            database = arguments.get("database")
            query = arguments.get("query")
            limit = arguments.get("limit")

            if not database or not query:
                raise ValueError("缺少必需参数: database 和 query")

            result = await asyncio.to_thread(
                db_ops.execute_query,
                database,
                query,
                None,
                limit,
                "query_database"  # 传递工具名称
            )

            # 记录工具调用日志
            query_logger.log_tool_call(
                tool_name="query_database",
                params={"database": database, "query": query[:100], "limit": limit},
                success=result.get("success", False),
                result_summary=f"返回 {result.get('row_count', 0)} 行数据",
                error=result.get("error")
            )

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        elif name == "get_table_info":
            # 获取表详细信息
            database = arguments.get("database")
            table = arguments.get("table")

            if not database or not table:
                raise ValueError("缺少必需参数: database 和 table")

            info = await asyncio.to_thread(db_ops.get_table_info, database, table)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(info, ensure_ascii=False, indent=2)
                )
            ]

        else:
            raise ValueError(f"未知的工具: {name}")

    except Exception as e:
        logger.error(f"工具调用失败 [{name}]: {str(e)}")
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e)
                }, ensure_ascii=False, indent=2)
            )
        ]


async def main():
    """
    主函数：启动 MCP 服务器
    """
    from mcp.server.stdio import stdio_server

    try:
        # 在启动服务器前初始化基础设施
        db_ops = initialize_infrastructure()

        # 注册 MCP Resources 和 Prompts
        logger.info("注册 MCP Resources...")
        register_resources(server, db_ops)
        logger.info("✓ Resources 注册成功")

        logger.info("注册 MCP Prompts...")
        register_prompts(server, db_ops)
        logger.info("✓ Prompts 注册成功")

        # TODO: 这些扩展工具使用了不兼容的 @server.tool() API
        # 需要重构为使用 @server.list_tools() 和 @server.call_tool()
        # logger.info("注册 MCP Export Tools...")
        # register_export_tools(server, db_ops)
        # logger.info("✓ Export Tools 注册成功")

        # logger.info("注册 MCP Performance Tools...")
        # register_performance_tools(server, db_ops)
        # logger.info("✓ Performance Tools 注册成功")

        # logger.info("注册 MCP Documentation Tools...")
        # register_documentation_tools(server, db_ops)
        # logger.info("✓ Documentation Tools 注册成功")

        async with stdio_server() as (read_stream, write_stream):
            logger.info("MySQL Reader MCP 服务器已启动，等待客户端连接...")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    except ConfigurationError as e:
        logger.error(f"配置错误，服务器无法启动: {str(e)}")
        logger.error("请检查配置文件或环境变量设置")
        sys.exit(1)

    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

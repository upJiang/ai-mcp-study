"""MCP Resources 实现 - 提供数据库资源访问"""

import asyncio
import json
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Resource, ResourceTemplate

logger = logging.getLogger(__name__)


def register_resources(server: Server, db_ops: Any) -> None:
    """
    注册 MCP Resources

    Args:
        server: MCP Server 实例
        db_ops: DatabaseOperations 实例
    """

    @server.list_resources()
    async def list_resources() -> list[Resource | ResourceTemplate]:
        """列出所有可用的资源"""
        return [
            # 静态资源：数据库列表
            Resource(
                uri="mysql://databases",
                name="数据库列表",
                description="获取所有可访问的 MySQL 数据库列表",
                mimeType="application/json"
            ),

            # 动态资源模板：特定数据库的表列表
            ResourceTemplate(
                uriTemplate="mysql://databases/{database}/tables",
                name="数据库表列表",
                description="获取指定数据库中的所有表",
                mimeType="application/json"
            ),

            # 动态资源模板：特定表的结构信息
            ResourceTemplate(
                uriTemplate="mysql://databases/{database}/tables/{table}",
                name="表结构信息",
                description="获取指定表的完整结构信息",
                mimeType="application/json"
            ),
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """
        读取资源内容

        Args:
            uri: 资源 URI

        Returns:
            资源内容（JSON 字符串）
        """
        try:
            # 解析 URI
            if uri == "mysql://databases":
                # 获取所有数据库列表
                databases = await asyncio.to_thread(db_ops.list_databases)

                result = {
                    "uri": uri,
                    "type": "database_list",
                    "count": len(databases),
                    "databases": databases
                }
                return json.dumps(result, ensure_ascii=False, indent=2)

            elif uri.startswith("mysql://databases/") and uri.endswith("/tables"):
                # 获取特定数据库的表列表
                # URI 格式: mysql://databases/{database}/tables
                parts = uri.split("/")
                if len(parts) >= 4:
                    database = parts[3]

                    tables = await asyncio.to_thread(db_ops.list_tables, database)

                    result = {
                        "uri": uri,
                        "type": "table_list",
                        "database": database,
                        "count": len(tables),
                        "tables": tables
                    }
                    return json.dumps(result, ensure_ascii=False, indent=2)

            elif uri.startswith("mysql://databases/") and "/tables/" in uri:
                # 获取特定表的结构信息
                # URI 格式: mysql://databases/{database}/tables/{table}
                parts = uri.split("/")
                if len(parts) >= 6:
                    database = parts[3]
                    table = parts[5]

                    info = await asyncio.to_thread(db_ops.get_table_info, database, table)

                    result = {
                        "uri": uri,
                        "type": "table_info",
                        "database": info["database"],
                        "table": info["table"],
                        "row_count": info["row_count"],
                        "fields": info["structure"],
                        "field_count": len(info["structure"]),
                        "create_statement": info.get("create_statement")
                    }
                    return json.dumps(result, ensure_ascii=False, indent=2)

            # 未知资源
            return json.dumps({
                "error": f"未知的资源 URI: {uri}",
                "uri": uri
            }, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"读取资源失败 [{uri}]: {str(e)}")
            return json.dumps({
                "error": str(e),
                "uri": uri
            }, ensure_ascii=False, indent=2)

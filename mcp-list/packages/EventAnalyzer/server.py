#!/usr/bin/env python3
"""EventAnalyzer MCP Server
埋点分析 MCP 服务

提供 5 个 Tools:
1. query_event_fields - 查询事件字段定义
2. analyze_tracking_data - 分析埋点数据
3. explain_field - 解释字段含义
4. find_field_in_code - 在代码中搜索字段
5. compare_events - 比较事件差异
"""

import asyncio
import json
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 导入业务模块
from src.api_client import EventAPIClient
from src.event_analyzer import EventAnalyzer
from src.field_explainer import FieldExplainer
from src.code_searcher import CodeSearcher
from src.utils.base64_decoder import Base64Decoder

# 创建 MCP Server 实例
server = Server("eventanalyzer")

# 初始化业务模块
api_client = EventAPIClient()
event_analyzer = EventAnalyzer()
field_explainer = FieldExplainer()
code_searcher = CodeSearcher()
base64_decoder = Base64Decoder()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """注册 MCP Tools"""
    return [
        Tool(
            name="query_event_fields",
            description="查询埋点事件的所有字段定义，返回字段类型、说明、枚举值等信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "event": {
                        "type": "string",
                        "description": "事件名称，如 LlwResExposure、LlwResDownBtnClick"
                    },
                    "show_details": {
                        "type": "boolean",
                        "description": "是否显示详细信息（默认 true）",
                        "default": True
                    }
                },
                "required": ["event"]
            }
        ),
        Tool(
            name="analyze_tracking_data",
            description="分析埋点数据，检测字段类型错误、缺失字段、枚举值错误等问题",
            inputSchema={
                "type": "object",
                "properties": {
                    "event": {
                        "type": "string",
                        "description": "事件名称（可选，从数据中自动提取）"
                    },
                    "data": {
                        "type": "string",
                        "description": "Base64 编码的埋点数据或 JSON 字符串"
                    },
                    "check_required": {
                        "type": "boolean",
                        "description": "是否检查必填字段（默认 false）",
                        "default": False
                    }
                },
                "required": ["data"]
            }
        ),
        Tool(
            name="explain_field",
            description="解释埋点字段的含义、类型和枚举值",
            inputSchema={
                "type": "object",
                "properties": {
                    "event": {
                        "type": "string",
                        "description": "事件名称"
                    },
                    "field_name": {
                        "type": "string",
                        "description": "字段名称"
                    },
                    "show_enum": {
                        "type": "boolean",
                        "description": "是否显示枚举值（默认 true）",
                        "default": True
                    }
                },
                "required": ["event", "field_name"]
            }
        ),
        Tool(
            name="find_field_in_code",
            description="在指定项目中搜索字段的实现位置",
            inputSchema={
                "type": "object",
                "properties": {
                    "field_name": {
                        "type": "string",
                        "description": "字段名称"
                    },
                    "project_path": {
                        "type": "string",
                        "description": "项目根目录的绝对路径"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "最大结果数（默认 50）",
                        "default": 50
                    }
                },
                "required": ["field_name", "project_path"]
            }
        ),
        Tool(
            name="compare_events",
            description="比较两个埋点事件的字段差异",
            inputSchema={
                "type": "object",
                "properties": {
                    "event1": {
                        "type": "string",
                        "description": "第一个事件名称"
                    },
                    "event2": {
                        "type": "string",
                        "description": "第二个事件名称"
                    }
                },
                "required": ["event1", "event2"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理 Tool 调用"""

    try:
        if name == "query_event_fields":
            # 查询事件字段定义
            event = arguments["event"]
            show_details = arguments.get("show_details", True)

            fields = api_client.get_event_fields(event)

            # 解析枚举值
            if show_details:
                for field_name, field_def in fields.items():
                    if field_def.get("trans"):
                        field_def["enum_values"] = api_client.parse_field_trans(field_def["trans"])

            result = {
                "event": event,
                "total_fields": len(fields),
                "fields": fields
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "analyze_tracking_data":
            # 分析埋点数据
            data = arguments["data"]
            event_name = arguments.get("event")
            check_required = arguments.get("check_required", False)

            # 解码数据
            event_data = base64_decoder.decode_flexible(data)

            # 如果没有指定事件名称，从数据中提取
            if not event_name:
                event_name = event_data.get("event")

            if not event_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "无法确定事件名称，请指定 event 参数或确保数据中包含 event 字段"
                    }, ensure_ascii=False)
                )]

            # 获取字段定义
            field_definitions = api_client.get_event_fields(event_name)

            # 分析数据
            result = event_analyzer.analyze(event_data, field_definitions, check_required)

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "explain_field":
            # 解释字段含义
            event = arguments["event"]
            field_name = arguments["field_name"]
            show_enum = arguments.get("show_enum", True)

            field_info = api_client.get_field_info(event, field_name)

            if not field_info:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"字段 {field_name} 在事件 {event} 中不存在"
                    }, ensure_ascii=False)
                )]

            result = field_explainer.explain_field(field_name, field_info, show_enum)

            # 查找相关字段
            all_fields = api_client.get_event_fields(event)
            related_fields = field_explainer.search_related_fields(field_name, all_fields)
            result["related_fields"] = related_fields

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "find_field_in_code":
            # 在代码中搜索字段
            field_name = arguments["field_name"]
            project_path = arguments["project_path"]
            max_results = arguments.get("max_results", 50)

            result = code_searcher.find_field(field_name, project_path, max_results)

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "compare_events":
            # 比较事件差异
            event1 = arguments["event1"]
            event2 = arguments["event2"]

            fields1 = api_client.get_event_fields(event1)
            fields2 = api_client.get_event_fields(event2)

            result = event_analyzer.compare_events(fields1, fields2)
            result["event1"] = event1
            result["event2"] = event2

            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, ensure_ascii=False, indent=2)
        )]


async def main():
    """启动 MCP Server"""
    import os

    # 检查运行模式
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if transport == "http":
        # HTTP/SSE 模式（用于远程访问）
        import uvicorn
        from mcp.server.sse import SseServerTransport
        from starlette.requests import Request
        from starlette.responses import Response

        # 创建 SSE transport（使用相对路径，避免 nginx 代理时的路径问题）
        sse = SseServerTransport("messages")

        # 纯 ASGI 应用，避免 Mount 的 307 重定向问题
        async def app(scope, receive, send):
            if scope["type"] == "http":
                path = scope["path"]
                method = scope["method"]

                # SSE 连接端点
                if path == "/sse" and method == "GET":
                    async with sse.connect_sse(scope, receive, send) as streams:
                        await server.run(
                            streams[0],
                            streams[1],
                            server.create_initialization_options()
                        )
                # POST 消息端点
                elif path == "/messages" and method == "POST":
                    await sse.handle_post_message(scope, receive, send)
                # 404
                else:
                    await send({
                        "type": "http.response.start",
                        "status": 404,
                        "headers": [[b"content-type", b"text/plain"]],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b"Not Found",
                    })

        # 启动 HTTP 服务器
        port = int(os.getenv("MCP_PORT", "8000"))
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
    else:
        # stdio 模式（用于本地）
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )


if __name__ == "__main__":
    asyncio.run(main())

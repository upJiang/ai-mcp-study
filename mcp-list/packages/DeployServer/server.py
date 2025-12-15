#!/usr/bin/env python3
"""
MCP Deploy Server - 测试环境批量发版服务器

提供以下工具：
1. list_projects - 获取可发版的项目列表
2. deploy_project - 发版单个项目
3. batch_deploy - 批量发版（串行执行）
4. deploy_all - 发版所有项目
"""

import asyncio
import json
import sys
import io
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 注意：不要在 MCP 服务器中重新包装 stdout/stderr
# MCP 使用 stdio 进行二进制 JSON-RPC 通信，重新包装会破坏通信
# 如果需要处理编码问题，应该在数据层面处理

import deploy_api
from deploy_api import DeployAPIError


# 创建 MCP 服务器实例
app = Server("deploy-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    注册 MCP 工具列表
    """
    return [
        Tool(
            name="list_projects",
            description="获取可发版的项目列表（从 OA API 动态获取）",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="deploy_project",
            description="发版单个项目，拉取最新代码并复制配置",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目名称（如：3d, user, www 等）"
                    }
                },
                "required": ["project_name"]
            }
        ),
        Tool(
            name="batch_deploy",
            description="批量发版多个项目（串行执行）",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "项目名称列表（如：[\"3d\", \"user\", \"www\"]）"
                    }
                },
                "required": ["project_names"]
            }
        ),
        Tool(
            name="deploy_all",
            description="发版所有项目（可选排除指定项目）",
            inputSchema={
                "type": "object",
                "properties": {
                    "exclude": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "要排除的项目名称列表（可选）"
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    处理工具调用
    """
    try:
        if name == "list_projects":
            result = await handle_list_projects()
        elif name == "deploy_project":
            result = await handle_deploy_project(arguments)
        elif name == "batch_deploy":
            result = await handle_batch_deploy(arguments)
        elif name == "deploy_all":
            result = await handle_deploy_all(arguments)
        else:
            raise ValueError(f"未知的工具: {name}")

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e)
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]


async def handle_list_projects() -> dict:
    """
    处理获取项目列表（已过滤不需要发版的项目）
    """
    try:
        result = await asyncio.to_thread(deploy_api.get_project_list)

        # 格式化输出
        output = {
            "status": "success",
            "total": result["total"],
            "filtered_count": result.get("filtered_count", 0),
            "projects": result["projects"]
        }

        return output

    except DeployAPIError as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def handle_deploy_project(arguments: dict) -> dict:
    """
    处理单个项目发版
    """
    project_name = arguments.get("project_name")

    if not project_name:
        return {
            "status": "error",
            "error": "缺少 project_name 参数"
        }

    try:
        result = await asyncio.to_thread(deploy_api.deploy_project, project_name)
        return result

    except DeployAPIError as e:
        return {
            "status": "error",
            "project": project_name,
            "error": str(e)
        }


async def handle_batch_deploy(arguments: dict) -> dict:
    """
    处理批量发版
    """
    project_names = arguments.get("project_names", [])

    if not project_names:
        return {
            "status": "error",
            "error": "缺少 project_names 参数或列表为空"
        }

    try:
        results = await asyncio.to_thread(deploy_api.batch_deploy, project_names)

        # 统计成功和失败的数量
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = len(results) - success_count

        return {
            "status": "completed",
            "total": len(results),
            "success": success_count,
            "failed": error_count,
            "results": results
        }

    except DeployAPIError as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def handle_deploy_all(arguments: dict) -> dict:
    """
    处理发版所有项目
    """
    exclude = arguments.get("exclude", [])

    try:
        results = await asyncio.to_thread(deploy_api.deploy_all, exclude)

        # 统计成功和失败的数量
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = len(results) - success_count

        return {
            "status": "completed",
            "total": len(results),
            "success": success_count,
            "failed": error_count,
            "excluded": exclude,
            "results": results
        }

    except DeployAPIError as e:
        return {
            "status": "error",
            "error": str(e)
        }


async def main():
    """
    主入口函数
    """
    import sys
    # 添加调试日志到 stderr（不影响 MCP 的 stdout 通信）
    print("[DeployServer] Starting...", file=sys.stderr, flush=True)

    try:
        async with stdio_server() as (read_stream, write_stream):
            print("[DeployServer] stdio_server initialized", file=sys.stderr, flush=True)
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
            print("[DeployServer] app.run completed", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[DeployServer] Error: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(main())

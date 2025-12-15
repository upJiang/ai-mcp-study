#!/usr/bin/env python3
"""
MCP OpenAPI Generator Server - PHP 项目 OpenAPI 文档生成器

支持的框架：
- Laravel
- ThinkPHP 5.0
- ThinkPHP 5.1

提供以下工具：
1. generate_openapi_for_controller - 为指定控制器生成 OpenAPI 文档
2. generate_openapi_for_methods - 为指定方法生成 OpenAPI 文档
3. save_openapi_doc - 保存生成的 OpenAPI 文档
"""

import asyncio
import json
import sys
import os
from typing import Any, Union
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 导入本地模块
from src.scanners import FrameworkDetector, FrameworkType, LaravelScanner, ThinkPHPScanner
from src.core import CodeAnalyzer, OpenAPIBuilder


def get_scanner(project_path: str) -> tuple[Union[LaravelScanner, ThinkPHPScanner], FrameworkType]:
    """
    根据项目类型获取对应的扫描器

    Args:
        project_path: 项目路径

    Returns:
        tuple: (扫描器实例, 框架类型)
    """
    detector = FrameworkDetector(project_path)
    framework_type = detector.detect()

    if framework_type == FrameworkType.LARAVEL:
        return LaravelScanner(project_path), framework_type
    elif framework_type == FrameworkType.THINKPHP:
        return ThinkPHPScanner(project_path, framework_type), framework_type
    else:
        # 默认尝试 Laravel
        return LaravelScanner(project_path), FrameworkType.UNKNOWN


def get_default_output_dir(project_path: str) -> str:
    """
    根据框架类型获取默认输出目录

    Args:
        project_path: 项目路径

    Returns:
        str: 默认输出目录的完整路径
    """
    detector = FrameworkDetector(project_path)
    relative_dir = detector.get_default_output_dir()
    return f"{project_path}/{relative_dir}"


# 创建 MCP 服务器实例
server = Server("openapi-generator")


def get_project_path(arguments: dict) -> str:
    """
    获取项目路径，如果未提供则使用当前工作目录
    """
    project_path = arguments.get("project_path")
    if not project_path:
        # 使用当前工作目录
        project_path = os.getcwd()
    return project_path


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    注册 MCP 工具列表
    """
    return [
        Tool(
            name="generate_openapi_for_controller",
            description="为指定控制器生成完整的 OpenAPI 文档。支持 Laravel 和 ThinkPHP 框架，自动检测框架类型。当用户提到'生成接口文档'、'生成API文档'、'生成OpenAPI文档'并指定了控制器时，应该调用此工具。自动分析控制器代码、Request/Validate验证类、Service服务类、Model模型等相关依赖。",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目根目录路径（可选，默认使用当前工作目录）。支持 Laravel 和 ThinkPHP 项目"
                    },
                    "controller_name": {
                        "type": "string",
                        "description": "控制器名称（如 'UserController' 或 'User'），从用户 @ 指定的文件路径中提取"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录（可选，Laravel 默认 storage/api-docs，ThinkPHP 默认 api-docs）"
                    },
                    "use_schemas": {
                        "type": "boolean",
                        "description": "是否生成 components.schemas 并使用 $ref 引用（可选，默认 false）。设为 false 时直接在 responses 中内联定义 schema，设为 true 时生成可复用的 Schema 定义。如果用户没有明确要求生成 Schemas，应该询问用户是否需要。"
                    }
                },
                "required": ["controller_name"]
            }
        ),
        Tool(
            name="generate_openapi_for_methods",
            description="为控制器的指定方法生成 OpenAPI 文档。当用户只需要生成控制器中某几个方法的文档时使用。",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目根目录路径（可选，默认使用当前工作目录）"
                    },
                    "controller_name": {
                        "type": "string",
                        "description": "控制器名称"
                    },
                    "method_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "方法名称列表（如 ['index', 'store']）"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录（可选）"
                    },
                    "use_schemas": {
                        "type": "boolean",
                        "description": "是否生成 components.schemas 并使用 $ref 引用（可选，默认 false）"
                    }
                },
                "required": ["controller_name", "method_names"]
            }
        ),
        Tool(
            name="save_openapi_doc",
            description="保存生成的 OpenAPI 文档到文件。在分析完控制器代码生成文档后，必须调用此工具保存。",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Laravel 项目根目录路径（可选，默认使用当前工作目录）"
                    },
                    "controller_name": {
                        "type": "string",
                        "description": "控制器名称（如 'UserController'）"
                    },
                    "controller_path": {
                        "type": "string",
                        "description": "控制器相对路径（如 'Admin/MenuController'），用于生成带目录前缀的文件名如 Admin_Menu.json"
                    },
                    "openapi_doc": {
                        "type": "object",
                        "description": "生成的 OpenAPI 文档对象，包含 paths 和 components"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录（可选，默认为 storage/api-docs）"
                    }
                },
                "required": ["controller_name", "openapi_doc"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    处理工具调用
    """
    try:
        if name == "generate_openapi_for_controller":
            result = await handle_generate_openapi_for_controller(arguments)
        elif name == "generate_openapi_for_methods":
            result = await handle_generate_openapi_for_methods(arguments)
        elif name == "save_openapi_doc":
            result = await handle_save_openapi_doc(arguments)
        else:
            raise ValueError(f"未知的工具: {name}")

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e)
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]


async def handle_generate_openapi_for_controller(arguments: dict) -> dict:
    """
    处理为控制器生成 OpenAPI 文档
    """
    project_path = get_project_path(arguments)
    controller_name = arguments.get("controller_name")
    output_dir = arguments.get("output_dir")
    use_schemas = arguments.get("use_schemas", False)  # 默认不生成 Schemas

    if not controller_name:
        return {
            "status": "error",
            "error": "缺少必需参数: controller_name"
        }

    # 自动检测框架类型并获取对应扫描器
    scanner, framework_type = get_scanner(project_path)
    framework_name = {
        FrameworkType.LARAVEL: "Laravel",
        FrameworkType.THINKPHP: "ThinkPHP",
        FrameworkType.UNKNOWN: "Unknown"
    }.get(framework_type, "Unknown")

    # 设置输出目录（根据框架类型使用不同的默认目录）
    if not output_dir:
        output_dir = get_default_output_dir(project_path)

    # 验证项目
    if not scanner.validate_project():
        return {
            "status": "error",
            "error": f"不是有效的 PHP 项目: {project_path}（检测到框架: {framework_name}）"
        }

    # 获取控制器文件路径
    controller_file = scanner.get_controller_file(controller_name)
    if not controller_file:
        return {
            "status": "error",
            "error": f"无法找到控制器: {controller_name}"
        }

    # 读取控制器代码
    controller_code = scanner.read_controller_code(controller_name)
    if not controller_code:
        return {
            "status": "error",
            "error": f"无法读取控制器代码: {controller_name}"
        }

    # 计算控制器相对路径（用于生成文件名）
    # 例如：app/Http/Controllers/Admin/MenuController.php -> Admin/MenuController
    try:
        relative_path = controller_file.relative_to(scanner.project_path)
        # 去掉 app/Http/Controllers/ 或 modules/*/Http/Controllers/ 前缀
        path_str = str(relative_path).replace("\\", "/")
        # 移除常见前缀
        for prefix in ["app/Http/Controllers/", "modules/"]:
            if path_str.startswith(prefix):
                path_str = path_str[len(prefix):]
                break
        # 如果还有 /Http/Controllers/，也移除
        if "/Http/Controllers/" in path_str:
            path_str = path_str.split("/Http/Controllers/", 1)[-1]
        controller_path = path_str
    except ValueError:
        controller_path = controller_name

    # 查找路由
    routes = scanner.find_routes_for_controller(controller_name)

    # 查找相关类
    related_classes = scanner.find_related_classes(controller_code)

    # 构建分析提示词
    analyzer = CodeAnalyzer()
    analysis_prompt = analyzer.build_controller_analysis_prompt(
        controller_name,
        controller_code,
        routes,
        related_classes,
        framework=framework_name,
        use_schemas=use_schemas
    )

    # 根据是否使用 Schemas 调整指令
    if use_schemas:
        doc_format = """{
    "paths": {
      "/api/path": {
        "get": { ... },
        "post": { ... }
      }
    },
    "components": {
      "schemas": { ... }
    }
  }"""
    else:
        doc_format = """{
    "paths": {
      "/api/path": {
        "get": {
          "responses": {
            "200": {
              "content": {
                "application/json": {
                  "schema": { "type": "object", "properties": {...} }
                }
              }
            }
          }
        }
      }
    }
  }

注意：不需要生成 components.schemas，直接在 responses 中内联定义 schema。"""

    # 返回分析提示词，让 Claude 在当前会话中分析
    return {
        "status": "analysis_request",
        "message": f"正在准备分析 {controller_name}（{framework_name} 项目）...",
        "framework": framework_name,
        "controller_name": controller_name,
        "controller_path": controller_path,
        "project_path": project_path,
        "output_dir": output_dir,
        "use_schemas": use_schemas,
        "analysis_prompt": analysis_prompt,
        "routes_found": len(routes),
        "related_classes_found": len(related_classes),
        "instruction": f"""请基于上述分析提示词，生成符合 OpenAPI 3.0 规范的文档。

框架类型：{framework_name}
是否生成 Schemas：{"是" if use_schemas else "否（直接内联定义）"}

分析完成后，你必须调用 save_openapi_doc 工具来保存文档，参数如下：
- controller_name: "{controller_name}"
- controller_path: "{controller_path}"
- openapi_doc: 生成的 OpenAPI 文档对象，格式为：
  {doc_format}

注意：必须调用 save_openapi_doc 工具才能将文档保存到文件！"""
    }


async def handle_generate_openapi_for_methods(arguments: dict) -> dict:
    """
    处理为指定方法生成 OpenAPI 文档
    """
    project_path = get_project_path(arguments)
    controller_name = arguments.get("controller_name")
    method_names = arguments.get("method_names")
    output_dir = arguments.get("output_dir")
    use_schemas = arguments.get("use_schemas", False)  # 默认不生成 Schemas

    if not controller_name or not method_names:
        return {
            "status": "error",
            "error": "缺少必需参数: controller_name 或 method_names"
        }

    # 自动检测框架类型并获取对应扫描器
    scanner, framework_type = get_scanner(project_path)
    framework_name = {
        FrameworkType.LARAVEL: "Laravel",
        FrameworkType.THINKPHP: "ThinkPHP",
        FrameworkType.UNKNOWN: "Unknown"
    }.get(framework_type, "Unknown")

    # 设置输出目录（根据框架类型使用不同的默认目录）
    if not output_dir:
        output_dir = get_default_output_dir(project_path)

    # 验证项目
    if not scanner.validate_project():
        return {
            "status": "error",
            "error": f"不是有效的 PHP 项目: {project_path}（检测到框架: {framework_name}）"
        }

    # 获取控制器文件路径
    controller_file = scanner.get_controller_file(controller_name)
    if not controller_file:
        return {
            "status": "error",
            "error": f"无法找到控制器: {controller_name}"
        }

    # 读取控制器代码
    controller_code = scanner.read_controller_code(controller_name)
    if not controller_code:
        return {
            "status": "error",
            "error": f"无法读取控制器代码: {controller_name}"
        }

    # 计算控制器相对路径（用于生成文件名）
    try:
        relative_path = controller_file.relative_to(scanner.project_path)
        path_str = str(relative_path).replace("\\", "/")
        for prefix in ["app/Http/Controllers/", "modules/"]:
            if path_str.startswith(prefix):
                path_str = path_str[len(prefix):]
                break
        if "/Http/Controllers/" in path_str:
            path_str = path_str.split("/Http/Controllers/", 1)[-1]
        controller_path = path_str
    except ValueError:
        controller_path = controller_name

    # 查找路由
    all_routes = scanner.find_routes_for_controller(controller_name)

    # 只保留指定方法的路由
    routes = [r for r in all_routes if r.action in method_names]

    # 查找相关类
    related_classes = scanner.find_related_classes(controller_code)

    # 为每个方法构建分析提示词
    analysis_prompts = {}
    for method_name in method_names:
        # 找到对应的路由
        method_route = next((r for r in routes if r.action == method_name), None)

        # 构建提示词
        analyzer = CodeAnalyzer()
        prompt = analyzer.build_analysis_prompt(
            controller_code,
            method_name,
            method_route,
            related_classes,
            framework=framework_name,
            use_schemas=use_schemas
        )
        analysis_prompts[method_name] = prompt

    return {
        "status": "analysis_request",
        "message": f"正在准备分析 {controller_name} 的 {len(method_names)} 个方法（{framework_name} 项目）...",
        "framework": framework_name,
        "controller_name": controller_name,
        "controller_path": controller_path,
        "method_names": method_names,
        "project_path": project_path,
        "output_dir": output_dir,
        "use_schemas": use_schemas,
        "analysis_prompts": analysis_prompts,
        "instruction": f"""请逐个分析每个方法，生成符合 OpenAPI 3.0 规范的文档。

框架类型：{framework_name}
是否生成 Schemas：{"是" if use_schemas else "否（直接内联定义）"}

分析完成后，你必须调用 save_openapi_doc 工具来保存文档，参数如下：
- controller_name: "{controller_name}"
- controller_path: "{controller_path}"
- openapi_doc: 生成的 OpenAPI 文档对象

{"" if use_schemas else "注意：不需要生成 components.schemas，直接在 responses 中内联定义 schema。"}
必须调用 save_openapi_doc 工具才能将文档保存到文件！"""
    }


async def handle_save_openapi_doc(arguments: dict) -> dict:
    """
    保存生成的 OpenAPI 文档到文件

    文件名格式：{目录1}_{目录2}_{控制器名}.json
    例如：
    - Admin/MenuController -> Admin_Menu.json
    - Api/V1/UserController -> Api_V1_User.json
    - UserController -> User.json
    """
    project_path = get_project_path(arguments)
    controller_name = arguments.get("controller_name")
    controller_path = arguments.get("controller_path")  # 可选的控制器路径
    openapi_doc = arguments.get("openapi_doc")
    output_dir = arguments.get("output_dir")

    if not controller_name:
        return {
            "status": "error",
            "error": "缺少必需参数: controller_name"
        }

    if not openapi_doc:
        return {
            "status": "error",
            "error": "缺少必需参数: openapi_doc"
        }

    # 设置输出目录（根据框架类型使用不同的默认目录）
    if not output_dir:
        output_dir = get_default_output_dir(project_path)

    try:
        # 确保输出目录存在
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        # 优先使用 controller_path，否则使用 controller_name
        if controller_path:
            # 处理路径：Admin/MenuController -> Admin_Menu
            # 1. 替换路径分隔符为下划线
            # 2. 去掉 Controller 后缀
            # 3. 去掉 .php 扩展名（如果有）
            path_str = controller_path.replace("\\", "/")  # 统一使用 /
            path_str = path_str.replace(".php", "")  # 去掉 .php
            path_str = path_str.replace("Controller", "")  # 去掉 Controller
            # 替换 / 为 _
            file_base_name = path_str.replace("/", "_")
            # 清理可能的多余下划线
            file_base_name = "_".join(filter(None, file_base_name.split("_")))
        else:
            # 只有控制器名，去掉 Controller 后缀
            file_base_name = controller_name.replace("Controller", "")

        file_name = f"{file_base_name}.json"
        file_path = output_path / file_name

        # 用于显示的标题
        display_name = file_base_name.replace("_", " ")

        # 构建完整的 OpenAPI 文档
        builder = OpenAPIBuilder(
            title=f"{display_name} API",
            version="1.0.0",
            description=f"Auto-generated API documentation for {controller_name}"
        )

        # 如果传入的是完整文档，直接使用
        if "openapi" in openapi_doc:
            builder.document = openapi_doc
        else:
            # 如果只传入了 paths 和 components，合并到 builder
            if "paths" in openapi_doc:
                for path, methods in openapi_doc["paths"].items():
                    for method, operation in methods.items():
                        builder.add_path(path, method, operation)

            if "components" in openapi_doc and "schemas" in openapi_doc["components"]:
                for name, schema in openapi_doc["components"]["schemas"].items():
                    builder.add_schema(name, schema)

        # 保存文件
        builder.save_to_file(str(file_path))

        # 统计信息
        paths_count = len(builder.document.get("paths", {}))
        endpoints_count = sum(
            len(methods) for methods in builder.document.get("paths", {}).values()
        )

        return {
            "status": "success",
            "message": f"OpenAPI 文档已保存",
            "controller_name": controller_name,
            "file_path": str(file_path),
            "paths_count": paths_count,
            "endpoints_count": endpoints_count
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"保存文档失败: {str(e)}"
        }


async def main():
    """
    主入口函数
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

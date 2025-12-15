"""代码分析器 - 构建分析提示词，通过 Claude 分析代码

支持的框架：
- Laravel
- ThinkPHP
"""

from typing import Dict, Optional, Union


class CodeAnalyzer:
    """代码分析器"""

    @staticmethod
    def build_analysis_prompt(
        controller_code: str,
        method_name: str,
        route_info: Optional[object],
        related_classes: Dict[str, str],
        framework: str = "Laravel",
        use_schemas: bool = False
    ) -> str:
        """
        构建分析提示词

        Args:
            controller_code: 控制器源代码
            method_name: 方法名称
            route_info: 路由信息
            related_classes: 相关类代码（Model, Request/Validate, Resource, Service）
            framework: 框架类型（Laravel, ThinkPHP）
            use_schemas: 是否使用 $ref 引用 Schemas（默认 False，直接内联定义）

        Returns:
            str: 分析提示词
        """
        # 根据框架类型调整提示词
        if "ThinkPHP" in framework:
            framework_hint = f"ThinkPHP ({framework})"
            validation_hint = "validate (验证器)"
        else:
            framework_hint = "Laravel"
            validation_hint = "FormRequest (表单请求验证)"

        prompt_parts = [
            f"请分析以下 {framework_hint} 控制器方法，并提取接口信息：\n",
            "\n## 控制器代码",
            "```php",
            controller_code,
            "```\n",
            f"## 方法名称",
            f"{method_name}\n"
        ]

        # 添加路由信息
        if route_info:
            prompt_parts.extend([
                "## 路由信息",
                f"- 路径: {route_info.path}",
                f"- HTTP 方法: {route_info.method}",
                f"- 中间件: {', '.join(route_info.middleware) if route_info.middleware else '无'}\n"
            ])

        # 添加相关类代码
        if related_classes:
            prompt_parts.append("## 相关类代码")
            for class_name, class_code in related_classes.items():
                prompt_parts.extend([
                    f"\n### {class_name}",
                    "```php",
                    class_code,
                    "```"
                ])

        # 添加分析要求
        prompt_parts.extend([
            "\n---\n",
            "请以 JSON 格式返回以下信息：\n",
            "```json",
            "{",
            '  "summary": "接口简短描述（1句话）",',
            '  "description": "接口详细描述",',
            '  "parameters": [',
            "    {",
            '      "name": "参数名",',
            '      "in": "query|path|header|cookie",',
            '      "required": true|false,',
            '      "schema": {"type": "string|integer|boolean|array|object", ...},',
            '      "description": "参数描述"',
            "    }",
            "  ],",
            '  "requestBody": {',
            '    "required": true|false,',
            '    "content": {',
            '      "application/json": {',
            '        "schema": {',
            '          "type": "object",',
            '          "properties": {},',
            '          "required": []',
            "        }",
            "      }",
            "    }",
            "  },",
            '  "responses": {',
            '    "200": {',
            '      "description": "成功响应描述",',
            '      "content": {',
            '        "application/json": {',
            '          "schema": {',
            '            "type": "object",',
            '            "properties": {}',
            "          }",
            "        }",
            "      }",
            "    },",
            '    "400": {',
            '      "description": "验证失败",',
            '      "content": {',
            '        "application/json": {',
            '          "schema": {',
            '            "type": "object",',
            '            "properties": {',
            '              "message": {"type": "string"},',
            '              "errors": {"type": "object"}',
            "            }",
            "          }",
            "        }",
            "      }",
            "    }",
            "  }",
            "}",
            "```\n",
            "**分析要点**：",
            "1. 从代码逻辑推断参数类型和是否必需",
            "2. 分析返回值的数据结构",
            f"3. 如果有 {validation_hint}，从验证规则推断参数和 requestBody",
        ])

        # 根据框架添加特定的分析要点
        if "ThinkPHP" in framework:
            prompt_parts.extend([
                "4. 如果使用 model() 助手函数，分析 Model 的字段结构",
                "5. 生成符合 OpenAPI 3.0 规范的 Schema",
                "6. 考虑 ThinkPHP 的响应格式（json(), success(), error()）",
                "7. 路径参数从路由 path 中提取（如 :id 或 <id>）",
                "8. 查询参数从 $request->param() 或 input() 中提取",
            ])
        else:
            prompt_parts.extend([
                "4. 如果有 Resource，从 toArray() 方法推断响应结构",
                "5. 生成符合 OpenAPI 3.0 规范的 Schema",
                "6. 考虑常见的 Laravel 响应格式（JSON、分页、错误响应）",
                "7. 路径参数应该从路由 path 中提取（如 {id}）",
                "8. 查询参数应该从 Request 的 validate() 或 $request->input() 中提取",
            ])

        prompt_parts.append("\n请直接返回 JSON，不要添加额外的说明文字。")

        return "\n".join(prompt_parts)

    @staticmethod
    def build_controller_analysis_prompt(
        controller_name: str,
        controller_code: str,
        routes: list,
        related_classes: Dict[str, str],
        framework: str = "Laravel",
        use_schemas: bool = False
    ) -> str:
        """
        构建整个控制器的分析提示词

        Args:
            controller_name: 控制器名称
            controller_code: 控制器源代码
            routes: 路由列表
            related_classes: 相关类代码
            framework: 框架类型
            use_schemas: 是否使用 $ref 引用 Schemas（默认 False，直接内联定义）

        Returns:
            str: 分析提示词
        """
        # 根据框架类型调整提示词
        if "ThinkPHP" in framework:
            framework_hint = f"ThinkPHP"
            validation_hint = "如果有 validate 验证器，从验证规则推断参数"
        else:
            framework_hint = "Laravel"
            validation_hint = "如果有 FormRequest，从验证规则推断参数和 requestBody"

        prompt_parts = [
            f"请分析以下 {framework_hint} 控制器 `{controller_name}` 的所有方法，并为每个方法生成 OpenAPI 接口定义：\n",
            "\n## 控制器代码",
            "```php",
            controller_code,
            "```\n",
            "## 路由信息",
        ]

        # 添加所有路由信息
        if routes:
            for route in routes:
                prompt_parts.append(
                    f"- {route.method} {route.path} → {route.action}()"
                )
        else:
            prompt_parts.append("- 未找到路由定义，请从控制器方法推断")

        # 添加相关类代码
        if related_classes:
            prompt_parts.append("\n## 相关类代码")
            for class_name, class_code in related_classes.items():
                # 截取代码，避免过长
                truncated_code = class_code[:2000] + "\n// ... (代码已截断)" if len(class_code) > 2000 else class_code
                prompt_parts.extend([
                    f"\n### {class_name}",
                    "```php",
                    truncated_code,
                    "```"
                ])

        # 添加分析要求
        prompt_parts.extend([
            "\n---\n",
            "请以 JSON 格式返回一个对象，key 为方法名，value 为该方法的 OpenAPI 定义：\n",
        ])

        # 根据是否使用 Schemas 调整输出格式说明
        if use_schemas:
            prompt_parts.extend([
                "```json",
                "{",
                '  "paths": {',
                '    "methodName": {',
                '      "summary": "接口简短描述",',
                '      "description": "接口详细描述",',
                '      "operationId": "controllerName.methodName",',
                '      "tags": ["TagName"],',
                '      "parameters": [...],',
                '      "requestBody": {...},',
                '      "responses": {',
                '        "200": {',
                '          "description": "成功响应",',
                '          "content": {',
                '            "application/json": {',
                '              "schema": { "$ref": "#/components/schemas/SchemaName" }',
                '            }',
                '          }',
                '        }',
                '      }',
                "    }",
                "  },",
                '  "components": {',
                '    "schemas": {',
                '      "SchemaName": {',
                '        "type": "object",',
                '        "properties": {...}',
                '      }',
                '    }',
                '  }',
                "}",
                "```\n",
            ])
        else:
            prompt_parts.extend([
                "```json",
                "{",
                '  "methodName": {',
                '    "summary": "接口简短描述",',
                '    "description": "接口详细描述",',
                '    "operationId": "controllerName.methodName",',
                '    "tags": ["TagName"],',
                '    "parameters": [...],',
                '    "requestBody": {',
                '      "required": true,',
                '      "content": {',
                '        "application/json": {',
                '          "schema": {',
                '            "type": "object",',
                '            "properties": {',
                '              "field1": { "type": "string", "description": "字段描述" }',
                '            },',
                '            "required": ["field1"]',
                '          }',
                '        }',
                '      }',
                '    },',
                '    "responses": {',
                '      "200": {',
                '        "description": "成功响应",',
                '        "content": {',
                '          "application/json": {',
                '            "schema": {',
                '              "type": "object",',
                '              "properties": {',
                '                "code": { "type": "integer", "example": 0 },',
                '                "message": { "type": "string", "example": "success" },',
                '                "data": { "type": "object", "properties": {...} }',
                '              }',
                '            }',
                '          }',
                '        }',
                '      }',
                '    }',
                "  }",
                "}",
                "```\n",
            ])

        prompt_parts.extend([
            "**分析要点**：",
            "1. 从代码逻辑推断参数类型和是否必需",
            "2. 分析返回值的数据结构",
            f"3. {validation_hint}",
        ])

        # 根据框架添加特定的分析要点
        if "ThinkPHP" in framework:
            prompt_parts.extend([
                "4. 如果使用 model() 助手函数，分析 Model 的字段结构",
                "5. 考虑 ThinkPHP 的响应格式（json(), success(), error()）",
                "6. 路径参数从路由 path 中提取（如 :id 或 <id>）",
                "7. 查询参数从 $request->param() 或 input() 中提取",
            ])
        else:
            prompt_parts.extend([
                "4. 如果有 Resource，从 toArray() 方法推断响应结构",
                "5. 考虑常见的 Laravel 响应格式（JSON、分页、错误响应）",
                "6. 路径参数应该从路由 path 中提取（如 {id}）",
                "7. 查询参数应该从 Request 的 validate() 或 $request->input() 中提取",
            ])

        # 根据是否使用 Schemas 添加额外说明
        if use_schemas:
            prompt_parts.extend([
                "\n**Schema 规范**：",
                "- 将可复用的数据结构定义在 components.schemas 中",
                "- 在 responses 中使用 $ref 引用 Schema",
                "- Schema 名称使用 PascalCase（如 UserInfo, OrderDetail）",
            ])
        else:
            prompt_parts.extend([
                "\n**重要**：",
                "- 不要生成 components.schemas，直接在 responses 中内联定义 schema",
                "- 所有响应结构直接写在 responses.200.content.application/json.schema 中",
                "- requestBody 的 schema 也直接内联定义",
            ])

        prompt_parts.append("\n请直接返回 JSON，不要添加额外的说明文字。")

        return "\n".join(prompt_parts)

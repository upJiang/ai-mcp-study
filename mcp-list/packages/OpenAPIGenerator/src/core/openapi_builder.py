"""OpenAPI 文档构建器 - 构建符合 OpenAPI 3.0 规范的文档"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class OpenAPIBuilder:
    """OpenAPI 文档构建器"""

    def __init__(
        self,
        title: str = "Laravel API Documentation",
        version: str = "1.0.0",
        description: str = "Auto-generated API documentation",
        server_url: str = "http://localhost",
        server_description: str = "本地开发环境"
    ):
        """
        初始化 Builder

        Args:
            title: API 标题
            version: API 版本
            description: API 描述
            server_url: 服务器 URL
            server_description: 服务器描述
        """
        self.document = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
                "description": description
            },
            "servers": [
                {
                    "url": server_url,
                    "description": server_description
                }
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }

    def add_path(
        self,
        path: str,
        method: str,
        operation: Dict[str, Any],
        test_result: Optional[Dict] = None
    ):
        """
        添加一个 API 端点

        Args:
            path: 路径（如 "/api/users"）
            method: HTTP 方法（如 "get", "post"）
            operation: 操作定义（OpenAPI Operation Object）
            test_result: 可选的测试结果
        """
        # 确保路径存在
        if path not in self.document["paths"]:
            self.document["paths"][path] = {}

        # 转换为小写
        method = method.lower()

        # 如果有测试结果，添加示例
        if test_result and "responses" in operation:
            for status_code, response in operation["responses"].items():
                if status_code == str(test_result.get("status_code", 200)):
                    if "content" in response and "application/json" in response["content"]:
                        # 添加真实响应示例
                        response["content"]["application/json"]["example"] = test_result.get("body")
                        # 标注已测试
                        if "description" in response:
                            response["description"] += " (✓ 已测试验证)"

        # 添加操作
        self.document["paths"][path][method] = operation

    def add_schema(self, name: str, schema: Dict[str, Any]):
        """
        添加一个 Schema 组件

        Args:
            name: Schema 名称
            schema: Schema 定义
        """
        self.document["components"]["schemas"][name] = schema

    def merge_with(self, other_doc: Dict[str, Any]):
        """
        合并另一个 OpenAPI 文档

        Args:
            other_doc: 另一个 OpenAPI 文档
        """
        # 合并 paths
        if "paths" in other_doc:
            for path, methods in other_doc["paths"].items():
                if path not in self.document["paths"]:
                    self.document["paths"][path] = {}
                self.document["paths"][path].update(methods)

        # 合并 schemas
        if "components" in other_doc and "schemas" in other_doc["components"]:
            self.document["components"]["schemas"].update(
                other_doc["components"]["schemas"]
            )

    def build(self) -> Dict[str, Any]:
        """
        构建完整的 OpenAPI 文档

        Returns:
            Dict[str, Any]: OpenAPI 文档
        """
        return self.document

    def save_to_file(self, file_path: str, indent: int = 2):
        """
        保存为 JSON 文件

        Args:
            file_path: 文件路径
            indent: JSON 缩进空格数
        """
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.document, f, ensure_ascii=False, indent=indent)

    @staticmethod
    def load_from_file(file_path: str) -> "OpenAPIBuilder":
        """
        从文件加载 OpenAPI 文档

        Args:
            file_path: 文件路径

        Returns:
            OpenAPIBuilder: 新的 Builder 实例
        """
        with open(file_path, "r", encoding="utf-8") as f:
            doc = json.load(f)

        # 创建新的 Builder
        builder = OpenAPIBuilder()
        builder.document = doc
        return builder

    @staticmethod
    def merge_documents(input_dir: str, output_file: str) -> Dict[str, Any]:
        """
        合并目录中的所有 OpenAPI 文档

        Args:
            input_dir: 输入目录
            output_file: 输出文件路径

        Returns:
            Dict[str, Any]: 合并后的文档
        """
        input_path = Path(input_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"目录不存在: {input_dir}")

        # 创建主文档
        main_builder = OpenAPIBuilder()

        # 合并所有 .openapi.json 文件
        json_files = list(input_path.glob("*.openapi.json"))

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    doc = json.load(f)
                    main_builder.merge_with(doc)
            except Exception as e:
                print(f"警告：无法加载文件 {json_file}: {e}")

        # 保存合并后的文档
        main_builder.save_to_file(output_file)

        return {
            "success": True,
            "input_files": len(json_files),
            "output_file": output_file,
            "total_paths": len(main_builder.document["paths"])
        }

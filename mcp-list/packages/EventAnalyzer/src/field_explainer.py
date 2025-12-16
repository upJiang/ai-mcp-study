"""Field Explainer
解释字段含义和枚举值
"""

import json
from typing import Dict, Any, Optional


class FieldExplainer:
    """字段解释器"""

    def explain_field(
        self,
        field_name: str,
        field_definition: Dict[str, Any],
        show_enum: bool = True
    ) -> Dict[str, Any]:
        """
        解释字段含义

        Args:
            field_name: 字段名称
            field_definition: 字段定义
            show_enum: 是否显示枚举值

        Returns:
            字段解释信息
        """
        result = {
            "field": field_name,
            "type": field_definition.get("type", "UNKNOWN"),
            "tips": field_definition.get("tips", ""),
            "description": field_definition.get("desc", "")
        }

        # 解析枚举值
        if show_enum and field_definition.get("trans"):
            try:
                enum_values = json.loads(field_definition["trans"])
                result["enum_values"] = enum_values
                result["enum_count"] = len(enum_values)
            except json.JSONDecodeError:
                result["enum_values"] = {}

        return result

    def format_field_info(self, field_info: Dict[str, Any]) -> str:
        """
        格式化字段信息为易读的文本

        Args:
            field_info: 字段信息

        Returns:
            格式化后的文本
        """
        lines = []
        lines.append(f"字段名: {field_info['field']}")
        lines.append(f"类型: {field_info['type']}")
        lines.append(f"说明: {field_info['tips']}")

        if field_info.get("description"):
            lines.append(f"描述: {field_info['description']}")

        if field_info.get("enum_values"):
            lines.append("\\n枚举值:")
            for key, value in field_info["enum_values"].items():
                lines.append(f"  {key}: {value}")

        return "\\n".join(lines)

    def search_related_fields(
        self,
        field_name: str,
        all_fields: Dict[str, Dict]
    ) -> list[str]:
        """
        搜索相关字段（基于命名模式）

        Args:
            field_name: 字段名称
            all_fields: 所有字段定义

        Returns:
            相关字段名称列表
        """
        related = []

        # 提取字段名的主要部分
        parts = field_name.split("_")

        for other_field in all_fields.keys():
            if other_field == field_name:
                continue

            # 检查是否包含相同的词根
            other_parts = other_field.split("_")
            common_parts = set(parts) & set(other_parts)

            if len(common_parts) > 0:
                related.append(other_field)

        return related[:10]  # 最多返回 10 个相关字段

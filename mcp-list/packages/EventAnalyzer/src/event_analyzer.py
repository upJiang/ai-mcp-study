"""Event Analyzer
分析埋点数据，检测字段问题
"""

from typing import Dict, Any, List
from src.utils.type_checker import TypeChecker, TypeName


class EventAnalyzer:
    """埋点事件分析器"""

    def __init__(self):
        self.type_checker = TypeChecker()

    def analyze(
        self,
        event_data: Dict[str, Any],
        field_definitions: Dict[str, Dict],
        check_required: bool = False
    ) -> Dict[str, Any]:
        """
        分析埋点数据，检测问题

        Args:
            event_data: 埋点数据
            field_definitions: 字段定义（从 API 获取）
            check_required: 是否检查必填字段

        Returns:
            分析结果
        """
        issues = []
        properties = event_data.get("properties", {})

        # 1. 检查类型匹配
        for field_name, value in properties.items():
            if field_name in field_definitions:
                expected_type = field_definitions[field_name]["type"]
                actual_type = self.type_checker.infer_type(value)

                if not self.type_checker.type_matches(expected_type, actual_type):
                    issues.append({
                        "type": "type_mismatch",
                        "field": field_name,
                        "expected": expected_type,
                        "actual": actual_type,
                        "value": value,
                        "severity": "error",
                        "message": f"字段 {field_name} 类型错误: 期望 {expected_type}, 实际 {actual_type}"
                    })

        # 2. 检查字段是否在定义中（可能是拼写错误或废弃字段）
        for field_name in properties.keys():
            if field_name not in field_definitions:
                # 跳过系统字段（以 $ 开头）
                if not field_name.startswith("$"):
                    issues.append({
                        "type": "unknown_field",
                        "field": field_name,
                        "severity": "warning",
                        "message": f"字段 {field_name} 不在字段定义中，可能是拼写错误或废弃字段"
                    })

        # 3. 检查枚举值（如果有 trans 定义）
        for field_name, value in properties.items():
            if field_name in field_definitions:
                field_def = field_definitions[field_name]
                if field_def.get("trans"):
                    try:
                        import json
                        enum_values = json.loads(field_def["trans"])
                        str_value = str(value)
                        if str_value not in enum_values:
                            issues.append({
                                "type": "invalid_enum",
                                "field": field_name,
                                "value": value,
                                "valid_values": list(enum_values.keys()),
                                "severity": "warning",
                                "message": f"字段 {field_name} 的值 {value} 不在枚举值范围内"
                            })
                    except Exception:
                        pass

        # 统计信息
        total_fields = len(field_definitions)
        present_fields = len([f for f in properties.keys() if f in field_definitions])

        # 确定状态
        error_count = len([i for i in issues if i.get("severity") == "error"])
        warning_count = len([i for i in issues if i.get("severity") == "warning"])

        if error_count > 0:
            status = "error"
        elif warning_count > 0:
            status = "warning"
        else:
            status = "ok"

        return {
            "event": event_data.get("event", "Unknown"),
            "status": status,
            "summary": f"检测到 {error_count} 个错误, {warning_count} 个警告",
            "issues": issues,
            "fields_present": present_fields,
            "fields_total": total_fields,
            "coverage": f"{present_fields}/{total_fields} ({present_fields*100//total_fields if total_fields > 0 else 0}%)"
        }

    def get_missing_fields(
        self,
        event_data: Dict[str, Any],
        field_definitions: Dict[str, Dict]
    ) -> List[str]:
        """
        获取缺失的字段列表

        Args:
            event_data: 埋点数据
            field_definitions: 字段定义

        Returns:
            缺失的字段名称列表
        """
        properties = event_data.get("properties", {})
        all_fields = set(field_definitions.keys())
        present_fields = set(properties.keys())

        # 排除系统字段（以 $ 开头）
        present_fields = {f for f in present_fields if not f.startswith("$")}

        return sorted(list(all_fields - present_fields))

    def compare_events(
        self,
        event1_fields: Dict[str, Dict],
        event2_fields: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        比较两个事件的字段差异

        Args:
            event1_fields: 事件1的字段定义
            event2_fields: 事件2的字段定义

        Returns:
            差异分析结果
        """
        fields1 = set(event1_fields.keys())
        fields2 = set(event2_fields.keys())

        common = fields1 & fields2
        only_in_event1 = fields1 - fields2
        only_in_event2 = fields2 - fields1

        return {
            "common_fields": sorted(list(common)),
            "event1_only": sorted(list(only_in_event1)),
            "event2_only": sorted(list(only_in_event2)),
            "total_common": len(common),
            "total_diff": len(only_in_event1) + len(only_in_event2)
        }

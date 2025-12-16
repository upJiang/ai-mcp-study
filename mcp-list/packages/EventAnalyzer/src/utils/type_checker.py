"""类型检查器
用于推断和校验埋点字段的类型
"""

from typing import Any, Literal


TypeName = Literal["NUMBER", "STRING", "BOOL", "LIST", "OBJECT", "NULL", "UNKNOWN"]


class TypeChecker:
    """类型检查和推断工具"""

    @staticmethod
    def infer_type(value: Any) -> TypeName:
        """
        推断值的类型

        Args:
            value: 待推断的值

        Returns:
            类型名称（NUMBER/STRING/BOOL/LIST/OBJECT/NULL/UNKNOWN）
        """
        if value is None:
            return "NULL"

        if isinstance(value, bool):
            return "BOOL"

        if isinstance(value, (int, float)):
            return "NUMBER"

        if isinstance(value, str):
            return "STRING"

        if isinstance(value, list):
            return "LIST"

        if isinstance(value, dict):
            return "OBJECT"

        return "UNKNOWN"

    @staticmethod
    def type_matches(expected: TypeName, actual: TypeName) -> bool:
        """
        检查类型是否匹配

        Args:
            expected: 期望的类型
            actual: 实际的类型

        Returns:
            是否匹配
        """
        # 完全匹配
        if expected == actual:
            return True

        # NULL 可以匹配任何类型（可选字段）
        if actual == "NULL":
            return True

        # BOOL 在某些情况下可以视为 NUMBER (0/1)
        if expected == "NUMBER" and actual == "BOOL":
            return True

        # NUMBER 在某些情况下可以转换为 STRING
        if expected == "STRING" and actual == "NUMBER":
            return True

        return False

    @staticmethod
    def validate_value(value: Any, expected_type: TypeName) -> tuple[bool, str]:
        """
        验证值是否符合期望的类型

        Args:
            value: 待验证的值
            expected_type: 期望的类型

        Returns:
            (是否有效, 错误信息)
        """
        actual_type = TypeChecker.infer_type(value)

        if TypeChecker.type_matches(expected_type, actual_type):
            return True, ""

        error_msg = f"类型不匹配: 期望 {expected_type}, 实际 {actual_type}"
        return False, error_msg

    @staticmethod
    def is_number_like(value: Any) -> bool:
        """检查值是否可以被视为数字"""
        if isinstance(value, (int, float)):
            return True

        if isinstance(value, bool):
            return True

        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False

        return False

    @staticmethod
    def is_bool_like(value: Any) -> bool:
        """检查值是否可以被视为布尔值"""
        if isinstance(value, bool):
            return True

        if isinstance(value, (int, float)):
            return value in (0, 1)

        if isinstance(value, str):
            return value.lower() in ("true", "false", "0", "1")

        return False

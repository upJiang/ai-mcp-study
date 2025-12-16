"""API Client
调用埋点接口获取事件字段定义
"""

import json
import requests
from typing import Dict, Any, Optional
from functools import lru_cache


class EventAPIClient:
    """埋点事件 API 客户端"""

    BASE_URL = "https://tptest-3d66.top/trans/api/event"

    def __init__(self, timeout: int = 10):
        """
        初始化 API 客户端

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()

    @lru_cache(maxsize=128)
    def get_event_fields(self, event_name: str) -> Dict[str, Any]:
        """
        获取事件的所有字段定义（带缓存）

        Args:
            event_name: 事件名称（如 LlwResExposure）

        Returns:
            字段定义字典
            格式: {
                "field_name": {
                    "type": "NUMBER/STRING/BOOL/LIST",
                    "tips": "字段说明",
                    "desc": "详细描述",
                    "trans": "枚举值映射 JSON 字符串"
                }
            }

        Raises:
            Exception: 请求失败时抛出异常
        """
        try:
            response = self.session.get(
                self.BASE_URL,
                params={"event": event_name},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"获取事件字段定义失败: {str(e)}")

    def parse_field_trans(self, trans_str: str) -> Dict[str, str]:
        """
        解析 trans 字段的枚举值映射

        Args:
            trans_str: trans 字段的 JSON 字符串

        Returns:
            枚举值映射字典
        """
        if not trans_str:
            return {}

        try:
            return json.loads(trans_str)
        except json.JSONDecodeError:
            return {}

    def get_field_info(self, event_name: str, field_name: str) -> Optional[Dict[str, Any]]:
        """
        获取单个字段的信息

        Args:
            event_name: 事件名称
            field_name: 字段名称

        Returns:
            字段信息，如果字段不存在返回 None
        """
        fields = self.get_event_fields(event_name)
        field_info = fields.get(field_name)

        if field_info and field_info.get("trans"):
            # 解析枚举值
            field_info["enum_values"] = self.parse_field_trans(field_info["trans"])

        return field_info

    def get_all_field_names(self, event_name: str) -> list[str]:
        """
        获取事件的所有字段名称列表

        Args:
            event_name: 事件名称

        Returns:
            字段名称列表
        """
        fields = self.get_event_fields(event_name)
        return list(fields.keys())

    def clear_cache(self):
        """清空缓存"""
        self.get_event_fields.cache_clear()

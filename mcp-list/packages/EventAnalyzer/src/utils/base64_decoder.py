"""Base64 解码工具
处理 URL 编码 + Base64 双重编码的埋点数据
"""

import base64
import json
import urllib.parse
from typing import Dict, Any, Union


class Base64Decoder:
    """Base64 解码器，支持 URL 编码 + Base64 双重编码"""

    @staticmethod
    def decode(encoded_data: str) -> Dict[str, Any]:
        """
        解码埋点数据

        Args:
            encoded_data: URL 编码 + Base64 编码的字符串

        Returns:
            解码后的 JSON 对象

        Raises:
            ValueError: 解码失败时抛出异常
        """
        try:
            # Step 1: URL 解码
            url_decoded = urllib.parse.unquote(encoded_data)

            # Step 2: Base64 解码
            base64_decoded = base64.b64decode(url_decoded).decode('utf-8')

            # Step 3: JSON 解析
            json_data = json.loads(base64_decoded)

            return json_data

        except Exception as e:
            raise ValueError(f"解码失败: {str(e)}")

    @staticmethod
    def is_valid_base64(s: str) -> bool:
        """
        检查字符串是否为有效的 Base64 编码

        Args:
            s: 待检查的字符串

        Returns:
            是否为有效的 Base64 编码
        """
        try:
            # URL 解码后尝试 Base64 解码
            url_decoded = urllib.parse.unquote(s)
            base64.b64decode(url_decoded)
            return True
        except Exception:
            return False

    @staticmethod
    def decode_flexible(data: Union[str, Dict]) -> Dict[str, Any]:
        """
        灵活解码，支持多种输入格式

        Args:
            data: Base64 字符串、JSON 字符串或字典对象

        Returns:
            解码后的 JSON 对象
        """
        # 如果已经是字典，直接返回
        if isinstance(data, dict):
            return data

        # 如果是字符串
        if isinstance(data, str):
            # 尝试直接解析为 JSON
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                pass

            # 尝试 Base64 解码
            try:
                return Base64Decoder.decode(data)
            except ValueError:
                pass

        raise ValueError(f"无法解析数据: {type(data)}")

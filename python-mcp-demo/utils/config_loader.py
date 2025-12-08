import json
import os
from pathlib import Path
from typing import List
from .api_client import ApiKeyInfo


def load_api_keys(config_path: str = None) -> List[ApiKeyInfo]:
    """加载API Key配置"""
    try:
        # 确定配置文件路径
        if config_path:
            final_path = config_path
        elif os.getenv('KEYS_CONFIG_PATH'):
            final_path = os.getenv('KEYS_CONFIG_PATH')
        else:
            final_path = str(Path(__file__).parent.parent.parent / 'ccReport' / 'config' / 'keys.json')
        
        absolute_path = Path(final_path).resolve()
        
        if not absolute_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {absolute_path}")
        
        # 读取配置文件
        with open(absolute_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 支持两种格式：api_keys 或 apiKeys
        api_keys_data = config.get('api_keys') or config.get('apiKeys')
        
        if not api_keys_data or not isinstance(api_keys_data, list):
            raise ValueError('配置文件格式错误：缺少 apiKeys 或 api_keys 数组')
        
        # 转换为ApiKeyInfo对象
        api_keys = [
            ApiKeyInfo(
                name=key['name'],
                account=key['account'],
                apiKey=key['apiKey']
            )
            for key in api_keys_data
        ]
        
        return api_keys
    except Exception as e:
        raise Exception(f"加载API Key配置失败: {str(e)}")


"""MCP 协议扩展模块 - Resources、Prompts 和 Tools"""

from .schemas import TableStructure, TableInfo, DatabaseInfo
from .resources import register_resources
from .prompts import register_prompts
from .export_tools import register_export_tools
from .performance_tools import register_performance_tools
from .documentation_tools import register_documentation_tools

__all__ = [
    'TableStructure',
    'TableInfo',
    'DatabaseInfo',
    'register_resources',
    'register_prompts',
    'register_export_tools',
    'register_performance_tools',
    'register_documentation_tools'
]

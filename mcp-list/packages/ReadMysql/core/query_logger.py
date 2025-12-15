#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查询日志记录模块"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class QueryLogger:
    """查询日志记录器"""

    def __init__(self, log_dir: str = "log"):
        """
        初始化日志记录器

        Args:
            log_dir: 日志目录路径
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # 创建日志器
        self.logger = logging.getLogger("QueryLogger")
        self.logger.setLevel(logging.INFO)

        # 防止重复添加 handler
        if not self.logger.handlers:
            self._setup_logger()

    def _setup_logger(self):
        """设置日志处理器"""
        # 创建按日期分割的文件处理器
        log_file = self.log_dir / f"query_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def log_query(
        self,
        database: str,
        query: str,
        success: bool,
        row_count: int = 0,
        execution_time: float = 0.0,
        error: Optional[str] = None,
        tool_name: Optional[str] = None,
        extra_info: Optional[Dict[str, Any]] = None
    ):
        """
        记录查询日志

        Args:
            database: 数据库名称
            query: SQL 查询语句
            success: 查询是否成功
            row_count: 返回的行数（可视为 token 使用量）
            execution_time: 查询执行时间（秒）
            error: 错误信息（如果有）
            tool_name: MCP 工具名称
            extra_info: 额外信息
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "database": database,
            "query": query.strip()[:500],  # 限制查询语句长度
            "success": success,
            "row_count": row_count,
            "execution_time": round(execution_time, 4),
            "tool_name": tool_name,
        }

        if error:
            log_data["error"] = str(error)

        if extra_info:
            log_data.update(extra_info)

        # 记录日志
        log_message = json.dumps(log_data, ensure_ascii=False)

        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)

    def log_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        success: bool,
        result_summary: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        记录 MCP 工具调用日志

        Args:
            tool_name: 工具名称
            params: 工具参数
            success: 是否成功
            result_summary: 结果摘要
            error: 错误信息
        """
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "params": params,
            "success": success,
        }

        if result_summary:
            log_data["result_summary"] = result_summary

        if error:
            log_data["error"] = str(error)

        log_message = json.dumps(log_data, ensure_ascii=False)

        if success:
            self.logger.info(log_message)
        else:
            self.logger.error(log_message)

    def get_statistics(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取查询统计信息

        Args:
            date: 日期（格式：YYYYMMDD），默认为今天

        Returns:
            统计信息字典
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')

        log_file = self.log_dir / f"query_{date}.log"

        if not log_file.exists():
            return {
                "date": date,
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "total_rows": 0,
                "total_time": 0.0,
            }

        stats = {
            "date": date,
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_rows": 0,
            "total_time": 0.0,
            "databases": {},
            "tools": {},
        }

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # 提取 JSON 部分
                    if ' - QueryLogger - ' in line:
                        json_part = line.split(' - ', 3)[-1]
                        data = json.loads(json_part)

                        stats["total_queries"] += 1

                        if data.get("success"):
                            stats["successful_queries"] += 1
                        else:
                            stats["failed_queries"] += 1

                        if "row_count" in data:
                            stats["total_rows"] += data["row_count"]

                        if "execution_time" in data:
                            stats["total_time"] += data["execution_time"]

                        # 按数据库统计
                        if "database" in data:
                            db = data["database"]
                            if db not in stats["databases"]:
                                stats["databases"][db] = 0
                            stats["databases"][db] += 1

                        # 按工具统计
                        if "tool_name" in data:
                            tool = data["tool_name"]
                            if tool not in stats["tools"]:
                                stats["tools"][tool] = 0
                            stats["tools"][tool] += 1

                except (json.JSONDecodeError, IndexError):
                    continue

        stats["total_time"] = round(stats["total_time"], 4)

        return stats


# 全局日志记录器实例
_logger_instance = None


def get_logger() -> QueryLogger:
    """获取全局日志记录器实例"""
    global _logger_instance

    if _logger_instance is None:
        # 获取 ReadMysql 项目根目录（core 的父目录）
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "log"
        _logger_instance = QueryLogger(str(log_dir))

    return _logger_instance

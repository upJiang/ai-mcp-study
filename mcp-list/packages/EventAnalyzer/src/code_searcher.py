"""Code Searcher
在项目代码中搜索字段实现
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any


class CodeSearcher:
    """代码搜索器"""

    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = ('.js', '.ts', '.vue', '.jsx', '.tsx', '.py', '.java', '.php')

    # 排除的目录
    EXCLUDED_DIRS = {
        'node_modules', '.git', 'dist', 'build', '__pycache__',
        'venv', 'vendor', '.next', '.nuxt', 'coverage'
    }

    def find_field(
        self,
        field_name: str,
        project_path: str,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        在项目中搜索字段实现

        Args:
            field_name: 字段名称
            project_path: 项目路径
            max_results: 最大结果数

        Returns:
            搜索结果
        """
        if not os.path.exists(project_path):
            return {
                "field": field_name,
                "error": f"项目路径不存在: {project_path}",
                "found_locations": [],
                "total_matches": 0
            }

        matches = []

        # 搜索模式
        patterns = self._build_search_patterns(field_name)

        # 遍历项目文件
        for file_path in self._iter_project_files(project_path):
            if len(matches) >= max_results:
                break

            file_matches = self._search_in_file(file_path, patterns, field_name)
            matches.extend(file_matches)

        return {
            "field": field_name,
            "found_locations": matches[:max_results],
            "total_matches": len(matches),
            "truncated": len(matches) > max_results
        }

    def _build_search_patterns(self, field_name: str) -> List[re.Pattern]:
        """
        构建搜索模式

        Args:
            field_name: 字段名称

        Returns:
            正则表达式模式列表
        """
        patterns = [
            # 字符串字面量: "field_name" 或 'field_name'
            re.compile(rf'["\']({field_name})["\']'),

            # 对象属性: field_name: value
            re.compile(rf'\b({field_name})\s*:'),

            # 对象属性赋值: obj.field_name = value
            re.compile(rf'\.({field_name})\s*='),

            # 变量名: const/let/var field_name
            re.compile(rf'\b(?:const|let|var)\s+({field_name})\b'),

            # 解构赋值: { field_name }
            re.compile(rf'\{{\s*({field_name})\s*\}}'),
        ]

        return patterns

    def _iter_project_files(self, project_path: str):
        """
        迭代项目中的所有支持的文件

        Args:
            project_path: 项目路径

        Yields:
            文件路径
        """
        for root, dirs, files in os.walk(project_path):
            # 排除指定目录
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]

            for file in files:
                if file.endswith(self.SUPPORTED_EXTENSIONS):
                    yield os.path.join(root, file)

    def _search_in_file(
        self,
        file_path: str,
        patterns: List[re.Pattern],
        field_name: str
    ) -> List[Dict[str, Any]]:
        """
        在单个文件中搜索

        Args:
            file_path: 文件路径
            patterns: 搜索模式列表
            field_name: 字段名称

        Returns:
            匹配结果列表
        """
        matches = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    if pattern.search(line):
                        # 获取上下文（前后各1行）
                        context_lines = []
                        for i in range(max(0, line_num - 2), min(len(lines), line_num + 1)):
                            context_lines.append(lines[i].rstrip())

                        matches.append({
                            "file": file_path,
                            "line": line_num,
                            "code": line.strip(),
                            "context": "\\n".join(context_lines)
                        })
                        break  # 每行只记录一次

        except Exception as e:
            # 忽略读取错误
            pass

        return matches

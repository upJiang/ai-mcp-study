"""框架检测器 - 自动识别 Laravel 或 ThinkPHP 框架"""

import json
from pathlib import Path
from typing import Optional
from enum import Enum


class FrameworkType(Enum):
    """框架类型枚举"""
    LARAVEL = "laravel"
    THINKPHP = "thinkphp"
    UNKNOWN = "unknown"


class FrameworkDetector:
    """框架检测器"""

    def __init__(self, project_path: str):
        """
        初始化检测器

        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)

    def detect(self) -> FrameworkType:
        """
        检测项目使用的框架类型

        Returns:
            FrameworkType: 框架类型
        """
        # 检查 composer.json
        composer_file = self.project_path / "composer.json"
        if not composer_file.exists():
            return FrameworkType.UNKNOWN

        try:
            with open(composer_file, "r", encoding="utf-8") as f:
                composer_data = json.load(f)
        except Exception:
            return FrameworkType.UNKNOWN

        require = composer_data.get("require", {})

        # 检测 Laravel
        if "laravel/framework" in require:
            return FrameworkType.LARAVEL

        # 检测 ThinkPHP - 只要包含 topthink 相关依赖就判定为 ThinkPHP
        for package in require.keys():
            if "topthink" in package.lower():
                return FrameworkType.THINKPHP

        # 通过目录结构检测
        return self._detect_by_structure()

    def _detect_by_structure(self) -> FrameworkType:
        """
        通过目录结构检测框架类型

        Returns:
            FrameworkType: 框架类型
        """
        # Laravel 特征文件
        laravel_markers = [
            self.project_path / "artisan",
            self.project_path / "app" / "Http" / "Controllers",
            self.project_path / "routes" / "web.php",
        ]
        if all(marker.exists() for marker in laravel_markers):
            return FrameworkType.LARAVEL

        # ThinkPHP 特征：有 application 目录或 thinkphp 目录
        application_dir = self.project_path / "application"
        thinkphp_dir = self.project_path / "thinkphp"
        vendor_topthink = self.project_path / "vendor" / "topthink"

        if application_dir.exists() or thinkphp_dir.exists() or vendor_topthink.exists():
            return FrameworkType.THINKPHP

        return FrameworkType.UNKNOWN

    def get_framework_info(self) -> dict:
        """
        获取框架详细信息

        Returns:
            dict: 框架信息
        """
        framework_type = self.detect()

        info = {
            "type": framework_type.value,
            "name": self._get_framework_name(framework_type),
            "project_path": str(self.project_path),
        }

        # 添加控制器目录信息
        info["controller_dirs"] = self._get_controller_dirs(framework_type)
        info["route_dirs"] = self._get_route_dirs(framework_type)

        return info

    def _get_framework_name(self, framework_type: FrameworkType) -> str:
        """获取框架显示名称"""
        names = {
            FrameworkType.LARAVEL: "Laravel",
            FrameworkType.THINKPHP: "ThinkPHP",
            FrameworkType.UNKNOWN: "Unknown",
        }
        return names.get(framework_type, "Unknown")

    def _get_controller_dirs(self, framework_type: FrameworkType) -> list:
        """获取控制器目录列表"""
        if framework_type == FrameworkType.LARAVEL:
            return ["app/Http/Controllers"]
        elif framework_type == FrameworkType.THINKPHP:
            # ThinkPHP 控制器可能在多个位置
            return [
                "application/*/controller",
                "application/controller",
                "app/*/controller",
                "app/controller",
            ]
        return []

    def _get_route_dirs(self, framework_type: FrameworkType) -> list:
        """
        获取路由目录/文件列表

        ThinkPHP 路由有两种方式：
        1. 模块+控制器+方法 (默认方式，无需路由文件)
        2. application/route.php 或 route/ 目录
        """
        if framework_type == FrameworkType.LARAVEL:
            return ["routes"]
        elif framework_type == FrameworkType.THINKPHP:
            return [
                "application/route.php",
                "application/*/route.php",
                "route",
            ]
        return []

    def get_default_output_dir(self) -> str:
        """
        获取默认的 API 文档输出目录

        Returns:
            str: 输出目录路径（相对于项目根目录）
                - Laravel: storage/api-docs
                - ThinkPHP: api-docs
        """
        framework_type = self.detect()

        if framework_type == FrameworkType.LARAVEL:
            return "storage/api-docs"
        elif framework_type == FrameworkType.THINKPHP:
            return "api-docs"
        else:
            # 默认使用 api-docs
            return "api-docs"

"""ThinkPHP 项目扫描器 - 扫描和解析 ThinkPHP 项目结构"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ControllerInfo:
    """控制器信息"""
    name: str
    path: str
    methods: List[str]
    namespace: Optional[str] = None
    module: Optional[str] = None  # ThinkPHP 模块名


@dataclass
class RouteInfo:
    """路由信息"""
    path: str
    method: str  # GET, POST, PUT, DELETE, etc.
    controller: str
    action: str
    middleware: List[str] = None
    name: Optional[str] = None


class ThinkPHPScanner:
    """ThinkPHP 项目扫描器"""

    def __init__(self, project_path: str, version=None):
        """
        初始化扫描器

        Args:
            project_path: ThinkPHP 项目根目录路径
            version: 保留参数，不再使用（为兼容性保留）
        """
        self.project_path = Path(project_path)

        # 自动检测目录结构，优先使用 application 目录
        self.app_dir = self.project_path / "application"
        if not self.app_dir.exists():
            self.app_dir = self.project_path / "app"

        # 路由文件可能在 application/route.php 或 route/ 目录
        self.route_file = self.app_dir / "route.php"
        self.route_dir = self.project_path / "route"

        self.controller_dirs = self._get_controller_dirs()
        self.routes_dirs = self._get_routes_dirs()

    def _get_controller_dirs(self) -> List[Path]:
        """
        获取所有控制器目录

        Returns:
            List[Path]: 控制器目录列表
        """
        controller_dirs = []

        if not self.app_dir.exists():
            return controller_dirs

        # 扫描模块目录下的 controller 目录
        for item in self.app_dir.iterdir():
            if item.is_dir():
                # 模块/controller 结构
                controller_path = item / "controller"
                if controller_path.exists():
                    controller_dirs.append(controller_path)

        # 也检查 app_dir/controller（单模块结构）
        single_controller = self.app_dir / "controller"
        if single_controller.exists():
            controller_dirs.append(single_controller)

        return controller_dirs

    def _get_routes_dirs(self) -> List[Path]:
        """
        获取所有路由目录/文件

        ThinkPHP 路由可能在以下位置：
        1. application/route.php（应用级路由）
        2. route/ 目录
        3. application/模块/route.php（模块级路由）

        Returns:
            List[Path]: 路由目录或文件列表
        """
        routes_paths = []

        # 检查 application/route.php
        if hasattr(self, 'route_file') and self.route_file.exists():
            routes_paths.append(self.route_file)

        # 检查 route/ 目录
        if hasattr(self, 'route_dir') and self.route_dir.exists():
            routes_paths.append(self.route_dir)

        # 检查模块级路由
        if self.app_dir.exists():
            for module_dir in self.app_dir.iterdir():
                if module_dir.is_dir():
                    # 模块下的 route.php 文件
                    module_route_file = module_dir / "route.php"
                    if module_route_file.exists():
                        routes_paths.append(module_route_file)
                    # 模块下的 route 目录
                    module_route_dir = module_dir / "route"
                    if module_route_dir.exists():
                        routes_paths.append(module_route_dir)

        return routes_paths

    def validate_project(self) -> bool:
        """
        验证是否为有效的 ThinkPHP 项目

        Returns:
            bool: 是否为有效的 ThinkPHP 项目
        """
        # 检查 composer.json
        composer_file = self.project_path / "composer.json"
        if not composer_file.exists():
            return False

        # 检查应用目录
        if not self.app_dir.exists():
            return False

        # 检查是否有控制器目录
        return len(self.controller_dirs) > 0

    def scan_controllers(self) -> List[ControllerInfo]:
        """
        扫描所有控制器

        Returns:
            List[ControllerInfo]: 控制器信息列表
        """
        controllers = []

        for controllers_dir in self.controller_dirs:
            if not controllers_dir.exists():
                continue

            # 获取模块名（从路径推断）
            module_name = self._get_module_name(controllers_dir)

            # 递归扫描目录下所有 PHP 文件
            for php_file in controllers_dir.rglob("*.php"):
                controller_info = self._parse_controller_file(php_file, module_name)
                if controller_info:
                    controllers.append(controller_info)

        return controllers

    def _get_module_name(self, controller_dir: Path) -> Optional[str]:
        """
        从控制器目录路径获取模块名

        Args:
            controller_dir: 控制器目录

        Returns:
            Optional[str]: 模块名
        """
        try:
            relative = controller_dir.relative_to(self.app_dir)
            parts = relative.parts
            if len(parts) >= 2 and parts[-1] == "controller":
                return parts[0]
        except ValueError:
            pass
        return None

    def get_controller_file(self, controller_name: str) -> Optional[Path]:
        """
        获取控制器文件路径

        Args:
            controller_name: 控制器名称（如 "User" 或 "UserController"）

        Returns:
            Optional[Path]: 控制器文件路径，如果不存在则返回 None
        """
        # 规范化控制器名称
        if not controller_name.endswith(".php"):
            # ThinkPHP 控制器通常不带 Controller 后缀
            name = controller_name.replace("Controller", "")
            controller_name = f"{name}.php"

        # 在所有控制器目录中查找
        for controllers_dir in self.controller_dirs:
            if not controllers_dir.exists():
                continue
            for php_file in controllers_dir.rglob(controller_name):
                return php_file

        # 也尝试查找带 Controller 后缀的文件
        controller_name_with_suffix = controller_name.replace(".php", "Controller.php")
        for controllers_dir in self.controller_dirs:
            if not controllers_dir.exists():
                continue
            for php_file in controllers_dir.rglob(controller_name_with_suffix):
                return php_file

        return None

    def read_controller_code(self, controller_name: str) -> Optional[str]:
        """
        读取控制器源代码

        Args:
            controller_name: 控制器名称

        Returns:
            Optional[str]: 控制器源代码，如果不存在则返回 None
        """
        controller_file = self.get_controller_file(controller_name)
        if not controller_file:
            return None

        try:
            with open(controller_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def find_routes_for_controller(self, controller_name: str) -> List[RouteInfo]:
        """
        从路由文件中找到控制器的路由定义

        Args:
            controller_name: 控制器名称

        Returns:
            List[RouteInfo]: 路由信息列表
        """
        routes = []

        for route_path in self.routes_dirs:
            if route_path.is_file():
                # 单个路由文件
                file_routes = self._parse_routes_file(route_path, controller_name)
                routes.extend(file_routes)
            elif route_path.is_dir():
                # 路由目录，扫描所有 PHP 文件
                for route_file in route_path.rglob("*.php"):
                    file_routes = self._parse_routes_file(route_file, controller_name)
                    routes.extend(file_routes)

        return routes

    def find_related_classes(self, controller_code: str) -> Dict[str, str]:
        """
        找到控制器中使用的相关类的代码

        支持的类类型：
        - model (模型)
        - validate (验证器)
        - service (服务类)
        - logic (逻辑类)

        Args:
            controller_code: 控制器源代码

        Returns:
            Dict[str, str]: 类名 -> 类代码的映射
        """
        related_classes = {}

        # 提取所有 use 语句
        # 匹配 app\* 或 think\* 命名空间的类
        use_pattern = r'use\s+(app(?:\\[\w]+)+);'
        uses = re.findall(use_pattern, controller_code, re.IGNORECASE)

        for use_class in uses:
            # 跳过控制器基类
            if use_class.lower().endswith("\\controller"):
                continue

            # 转换命名空间为文件路径
            class_file = self._namespace_to_file_path(use_class)

            if class_file and class_file.exists():
                try:
                    with open(class_file, "r", encoding="utf-8") as f:
                        class_code = f.read()
                        class_name = use_class.split("\\")[-1]
                        if class_name in related_classes:
                            key = use_class.replace("\\", "_")
                        else:
                            key = class_name
                        related_classes[key] = class_code
                except Exception:
                    continue

        # ThinkPHP 特有：查找 model() 和 validate() 方法调用
        self._find_helper_calls(controller_code, related_classes)

        return related_classes

    def _find_helper_calls(self, controller_code: str, related_classes: Dict[str, str]):
        """
        查找 ThinkPHP 助手函数调用的类

        例如：model('User'), validate('User')

        Args:
            controller_code: 控制器源代码
            related_classes: 相关类字典（会被修改）
        """
        # 匹配 model('ClassName') 或 model('module/ClassName')
        model_pattern = r"model\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
        model_matches = re.findall(model_pattern, controller_code)

        for model_name in model_matches:
            model_file = self._find_model_file(model_name)
            if model_file and model_file.exists():
                try:
                    with open(model_file, "r", encoding="utf-8") as f:
                        class_code = f.read()
                        class_name = model_name.split("/")[-1]
                        related_classes[f"Model_{class_name}"] = class_code
                except Exception:
                    continue

        # 匹配 validate('ClassName')
        validate_pattern = r"validate\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
        validate_matches = re.findall(validate_pattern, controller_code)

        for validate_name in validate_matches:
            validate_file = self._find_validate_file(validate_name)
            if validate_file and validate_file.exists():
                try:
                    with open(validate_file, "r", encoding="utf-8") as f:
                        class_code = f.read()
                        class_name = validate_name.split("/")[-1]
                        related_classes[f"Validate_{class_name}"] = class_code
                except Exception:
                    continue

    def _find_model_file(self, model_name: str) -> Optional[Path]:
        """
        查找模型文件

        Args:
            model_name: 模型名称（如 'User' 或 'admin/User'）

        Returns:
            Optional[Path]: 模型文件路径
        """
        parts = model_name.split("/")
        if len(parts) == 1:
            # 单模块或公共模型
            file_name = f"{parts[0]}.php"
            # 在所有模块的 model 目录中查找
            for module_dir in self.app_dir.iterdir():
                if module_dir.is_dir():
                    model_file = module_dir / "model" / file_name
                    if model_file.exists():
                        return model_file
            # 公共 model 目录
            common_model = self.app_dir / "model" / file_name
            if common_model.exists():
                return common_model
        else:
            # 指定模块
            module, name = parts[0], parts[1]
            model_file = self.app_dir / module / "model" / f"{name}.php"
            if model_file.exists():
                return model_file

        return None

    def _find_validate_file(self, validate_name: str) -> Optional[Path]:
        """
        查找验证器文件

        Args:
            validate_name: 验证器名称

        Returns:
            Optional[Path]: 验证器文件路径
        """
        parts = validate_name.split("/")
        if len(parts) == 1:
            file_name = f"{parts[0]}.php"
            for module_dir in self.app_dir.iterdir():
                if module_dir.is_dir():
                    validate_file = module_dir / "validate" / file_name
                    if validate_file.exists():
                        return validate_file
            common_validate = self.app_dir / "validate" / file_name
            if common_validate.exists():
                return common_validate
        else:
            module, name = parts[0], parts[1]
            validate_file = self.app_dir / module / "validate" / f"{name}.php"
            if validate_file.exists():
                return validate_file

        return None

    def _namespace_to_file_path(self, namespace: str) -> Optional[Path]:
        """
        将命名空间转换为文件路径

        Args:
            namespace: PHP 命名空间

        Returns:
            Optional[Path]: 文件路径
        """
        # app\module\controller\User -> app/module/controller/User.php
        if namespace.lower().startswith("app\\"):
            relative_path = namespace.replace("\\", "/") + ".php"
            return self.project_path / relative_path

        return None

    def _parse_controller_file(self, file_path: Path, module_name: Optional[str] = None) -> Optional[ControllerInfo]:
        """
        解析控制器文件

        Args:
            file_path: 控制器文件路径
            module_name: 模块名

        Returns:
            Optional[ControllerInfo]: 控制器信息
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取类名
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?'
            class_match = re.search(class_pattern, content)
            if not class_match:
                return None

            class_name = class_match.group(1)

            # 跳过基类
            if class_name.lower() == "controller":
                return None

            # 提取命名空间
            namespace_pattern = r'namespace\s+([\w\\]+);'
            namespace_match = re.search(namespace_pattern, content)
            namespace = namespace_match.group(1) if namespace_match else None

            # 提取公共方法
            method_pattern = r'public\s+function\s+(\w+)\s*\('
            methods = re.findall(method_pattern, content)

            # 过滤掉构造函数和魔术方法
            methods = [m for m in methods if not m.startswith("_")]

            if not methods:
                return None

            relative_path = file_path.relative_to(self.project_path)

            return ControllerInfo(
                name=class_name,
                path=str(relative_path),
                methods=methods,
                namespace=namespace,
                module=module_name
            )

        except Exception:
            return None

    def _parse_routes_file(self, file_path: Path, controller_name: str) -> List[RouteInfo]:
        """
        解析路由文件

        Args:
            file_path: 路由文件路径
            controller_name: 控制器名称

        Returns:
            List[RouteInfo]: 路由信息列表
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return []

        routes = []
        controller_base_name = controller_name.replace("Controller", "")

        # ThinkPHP 5.x 路由格式

        # 格式1: Route::get('path', 'module/controller/action')
        pattern1 = r"Route::(get|post|put|delete|patch|any)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)"
        for match in re.finditer(pattern1, content, re.IGNORECASE):
            method = match.group(1).upper()
            path = match.group(2)
            target = match.group(3)

            # 解析 target: module/controller/action 或 controller/action
            parts = target.split("/")
            if len(parts) >= 2:
                controller = parts[-2]
                action = parts[-1]

                if self._controller_matches(controller, controller_name, controller_base_name):
                    routes.append(RouteInfo(
                        path=f"/{path}" if not path.startswith("/") else path,
                        method=method if method != "ANY" else "GET",
                        controller=controller,
                        action=action,
                        middleware=[]
                    ))

        # 格式2: Route::rule('path', 'controller/action', 'GET|POST')
        pattern2 = r"Route::rule\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*(?:,\s*['\"]([^'\"]+)['\"])?\s*\)"
        for match in re.finditer(pattern2, content, re.IGNORECASE):
            path = match.group(1)
            target = match.group(2)
            methods_str = match.group(3) or "GET"

            parts = target.split("/")
            if len(parts) >= 2:
                controller = parts[-2]
                action = parts[-1]

                if self._controller_matches(controller, controller_name, controller_base_name):
                    for method in methods_str.split("|"):
                        routes.append(RouteInfo(
                            path=f"/{path}" if not path.startswith("/") else path,
                            method=method.strip().upper(),
                            controller=controller,
                            action=action,
                            middleware=[]
                        ))

        # 格式3: 'path' => 'controller/action' (数组配置)
        pattern3 = r"['\"]([^'\"]+)['\"]\s*=>\s*['\"]([^'\"]+)['\"]\s*(?:,\s*['\"]([^'\"]+)['\"])?"
        for match in re.finditer(pattern3, content):
            path = match.group(1)
            target = match.group(2)

            # 跳过非路由配置
            if "/" not in target or "=>" in path:
                continue

            parts = target.split("/")
            if len(parts) >= 2:
                controller = parts[-2]
                action = parts[-1]

                if self._controller_matches(controller, controller_name, controller_base_name):
                    routes.append(RouteInfo(
                        path=f"/{path}" if not path.startswith("/") else path,
                        method="GET",  # 默认 GET
                        controller=controller,
                        action=action,
                        middleware=[]
                    ))

        return routes

    def _controller_matches(self, found_controller: str, controller_name: str, controller_base_name: str) -> bool:
        """
        检查找到的控制器是否匹配目标控制器

        Args:
            found_controller: 路由文件中找到的控制器名称
            controller_name: 目标控制器名称
            controller_base_name: 目标控制器基础名称

        Returns:
            bool: 是否匹配
        """
        found_lower = found_controller.lower()
        target_lower = controller_name.lower()
        base_lower = controller_base_name.lower()

        # 精确匹配
        if found_lower == target_lower or found_lower == base_lower:
            return True

        # ThinkPHP 路由中通常使用小写
        if found_lower == target_lower.replace("controller", ""):
            return True

        return False

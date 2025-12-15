"""Laravel 项目扫描器 - 扫描和解析 Laravel 项目结构"""

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


@dataclass
class RouteInfo:
    """路由信息"""
    path: str
    method: str  # GET, POST, PUT, DELETE, etc.
    controller: str
    action: str
    middleware: List[str] = None
    name: Optional[str] = None


class LaravelScanner:
    """Laravel 项目扫描器"""

    def __init__(self, project_path: str):
        """
        初始化扫描器

        Args:
            project_path: Laravel 项目根目录路径
        """
        self.project_path = Path(project_path)

        # 检测项目类型并设置控制器目录和路由目录
        self.modules_dir = self.project_path / "modules"
        self.is_modular = self.modules_dir.exists()

        if self.is_modular:
            # 子模块结构：扫描 modules/{ModuleName}/Http/Controllers（排除 Common）
            self.controller_dirs = self._get_module_controller_dirs()
            # 子模块结构：扫描 modules/{ModuleName}/Routes
            self.routes_dirs = self._get_module_routes_dirs()
        else:
            # 标准结构：扫描 app/Http/Controllers
            self.controller_dirs = [self.project_path / "app" / "Http" / "Controllers"]
            # 标准结构：扫描 routes 目录
            self.routes_dirs = [self.project_path / "routes"]

        # 兼容旧代码：保留 controllers_dir 和 routes_dir 属性
        self.controllers_dir = self.controller_dirs[0] if self.controller_dirs else None
        self.routes_dir = self.routes_dirs[0] if self.routes_dirs else None

    def _get_module_controller_dirs(self) -> List[Path]:
        """
        获取所有模块的控制器目录（排除 Common 模块）

        Returns:
            List[Path]: 控制器目录列表
        """
        controller_dirs = []

        if not self.modules_dir.exists():
            return controller_dirs

        for module_dir in self.modules_dir.iterdir():
            # 跳过 Common 目录和非目录文件
            if not module_dir.is_dir() or module_dir.name == "Common":
                continue

            controllers_path = module_dir / "Http" / "Controllers"
            if controllers_path.exists():
                controller_dirs.append(controllers_path)

        return controller_dirs

    def _get_module_routes_dirs(self) -> List[Path]:
        """
        获取所有模块的路由目录

        Returns:
            List[Path]: 路由目录列表
        """
        routes_dirs = []

        # 先添加根目录的 routes（如果存在）
        root_routes = self.project_path / "routes"
        if root_routes.exists():
            routes_dirs.append(root_routes)

        if not self.modules_dir.exists():
            return routes_dirs

        for module_dir in self.modules_dir.iterdir():
            # 跳过非目录文件
            if not module_dir.is_dir():
                continue

            # 检查 Routes 目录（大写 R）
            routes_path = module_dir / "Routes"
            if routes_path.exists():
                routes_dirs.append(routes_path)

            # 也检查 routes 目录（小写 r）
            routes_path_lower = module_dir / "routes"
            if routes_path_lower.exists() and routes_path_lower != routes_path:
                routes_dirs.append(routes_path_lower)

        return routes_dirs

    def validate_project(self) -> bool:
        """
        验证是否为有效的 Laravel 项目

        Returns:
            bool: 是否为有效的 Laravel 项目
        """
        # 检查关键文件是否存在
        artisan_file = self.project_path / "artisan"
        composer_file = self.project_path / "composer.json"

        if not artisan_file.exists() or not composer_file.exists():
            return False

        # 检查 app 目录或 modules 目录（支持子模块结构）
        app_dir = self.project_path / "app"
        modules_dir = self.project_path / "modules"

        if not app_dir.exists() and not modules_dir.exists():
            return False

        return True

    def scan_controllers(self) -> List[ControllerInfo]:
        """
        扫描所有控制器

        Returns:
            List[ControllerInfo]: 控制器信息列表
        """
        controllers = []

        # 扫描所有控制器目录
        for controllers_dir in self.controller_dirs:
            if not controllers_dir.exists():
                continue

            # 递归扫描目录下所有 PHP 文件
            for php_file in controllers_dir.rglob("*.php"):
                controller_info = self._parse_controller_file(php_file)
                if controller_info:
                    controllers.append(controller_info)

        return controllers

    def get_controller_file(self, controller_name: str) -> Optional[Path]:
        """
        获取控制器文件路径

        Args:
            controller_name: 控制器名称（如 "UserController"）

        Returns:
            Optional[Path]: 控制器文件路径，如果不存在则返回 None
        """
        # 确保控制器名称以 .php 结尾
        if not controller_name.endswith(".php"):
            controller_name += ".php"

        # 在所有控制器目录中查找
        for controllers_dir in self.controller_dirs:
            if not controllers_dir.exists():
                continue
            for php_file in controllers_dir.rglob(controller_name):
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

        扫描策略：
        1. 遍历所有路由目录（routes/ 和 modules/*/Routes/）
        2. 递归扫描目录下所有 .php 文件
        3. 在每个文件中查找匹配的路由定义

        Args:
            controller_name: 控制器名称

        Returns:
            List[RouteInfo]: 路由信息列表
        """
        routes = []

        # 遍历所有路由目录
        for routes_dir in self.routes_dirs:
            if not routes_dir.exists():
                continue

            # 递归扫描目录下所有 PHP 文件
            for route_file in routes_dir.rglob("*.php"):
                file_routes = self._parse_routes_file(route_file, controller_name)
                routes.extend(file_routes)

        return routes

    def find_related_classes(self, controller_code: str) -> Dict[str, str]:
        """
        找到控制器中使用的相关类的代码

        支持的类类型：
        - Models (模型)
        - Http\Requests (表单请求验证)
        - Http\Resources (API 资源)
        - Services (服务类)
        - Repositories (仓库类)
        - Helpers / Utils (工具类)
        - 子模块中的类 (Modules\*\*)

        Args:
            controller_code: 控制器源代码

        Returns:
            Dict[str, str]: 类名 -> 类代码的映射
        """
        related_classes = {}

        # 提取所有 use 语句
        # 匹配 App\* 和 Modules\* 命名空间的类
        use_pattern_full = r'use\s+((?:App|Modules)(?:\\[\w]+)+);'
        uses = re.findall(use_pattern_full, controller_code)

        for use_class in uses:
            # 跳过控制器基类
            if use_class.endswith("\\Controller"):
                continue

            # 转换命名空间为文件路径
            class_file = self._namespace_to_file_path(use_class)

            if class_file and class_file.exists():
                try:
                    with open(class_file, "r", encoding="utf-8") as f:
                        class_code = f.read()
                        # 使用 "命名空间::类名" 作为键，避免同名类冲突
                        class_name = use_class.split("\\")[-1]
                        # 如果类名已存在，使用完整命名空间
                        if class_name in related_classes:
                            key = use_class.replace("\\", "_")
                        else:
                            key = class_name
                        related_classes[key] = class_code
                except Exception:
                    continue

        return related_classes

    def _namespace_to_file_path(self, namespace: str) -> Optional[Path]:
        """
        将命名空间转换为文件路径

        支持的命名空间：
        - App\* -> app/*
        - Modules\ModuleName\* -> modules/ModuleName/*

        Args:
            namespace: PHP 命名空间

        Returns:
            Optional[Path]: 文件路径，如果无法解析则返回 None
        """
        # App 命名空间
        if namespace.startswith("App\\"):
            relative_path = namespace.replace("App\\", "app/").replace("\\", "/") + ".php"
            return self.project_path / relative_path

        # Modules 命名空间
        if namespace.startswith("Modules\\"):
            relative_path = namespace.replace("Modules\\", "modules/").replace("\\", "/") + ".php"
            return self.project_path / relative_path

        return None

    def _parse_controller_file(self, file_path: Path) -> Optional[ControllerInfo]:
        """
        解析控制器文件

        Args:
            file_path: 控制器文件路径

        Returns:
            Optional[ControllerInfo]: 控制器信息，解析失败返回 None
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取类名 - 支持继承任意基类或不继承
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?'
            class_match = re.search(class_pattern, content)
            if not class_match:
                return None

            class_name = class_match.group(1)

            # 跳过基类 Controller
            if class_name == "Controller":
                return None

            # 提取命名空间
            namespace_pattern = r'namespace\s+([\w\\]+);'
            namespace_match = re.search(namespace_pattern, content)
            namespace = namespace_match.group(1) if namespace_match else None

            # 提取公共方法
            method_pattern = r'public\s+function\s+(\w+)\s*\('
            methods = re.findall(method_pattern, content)

            # 过滤掉构造函数和魔术方法
            methods = [m for m in methods if not m.startswith("__")]

            # 如果没有公共方法，可能不是控制器
            if not methods:
                return None

            relative_path = file_path.relative_to(self.project_path)

            return ControllerInfo(
                name=class_name,
                path=str(relative_path),
                methods=methods,
                namespace=namespace
            )

        except Exception:
            return None

    def _parse_routes_file(self, file_path: Path, controller_name: str) -> List[RouteInfo]:
        """
        解析路由文件，查找指定控制器的路由

        支持的路由格式：
        1. Route::get('/path', [Controller::class, 'method'])
        2. Route::get('/path', 'Controller@method')
        3. Route::resource('path', Controller::class)
        4. Route::apiResource('path', Controller::class)
        5. Route::match(['get', 'post'], '/path', [...])
        6. Route::any('/path', [...])
        7. 支持路由组中的前缀

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

        # 去掉控制器名称中的 "Controller" 后缀，用于更灵活的匹配
        controller_base_name = controller_name.replace("Controller", "")

        # 模式1: Route::get('/path', [Controller::class, 'method'])
        # 支持多行和各种空白字符
        pattern1 = r"Route::(get|post|put|delete|patch|options)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*\[\s*([^\]]+?)::class\s*,\s*['\"](\w+)['\"]\s*\]"

        for match in re.finditer(pattern1, content, re.IGNORECASE | re.DOTALL):
            method = match.group(1).upper()
            path = match.group(2)
            controller = match.group(3).strip().split("\\")[-1]
            action = match.group(4)

            if self._controller_matches(controller, controller_name, controller_base_name):
                routes.append(RouteInfo(
                    path=path,
                    method=method,
                    controller=controller,
                    action=action,
                    middleware=[]
                ))

        # 模式2: Route::get('/path', 'Controller@method') - 旧式字符串格式
        pattern2 = r"Route::(get|post|put|delete|patch|options)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"@]+)@(\w+)['\"]\s*\)"

        for match in re.finditer(pattern2, content, re.IGNORECASE):
            method = match.group(1).upper()
            path = match.group(2)
            controller = match.group(3).strip().split("\\")[-1]
            action = match.group(4)

            if self._controller_matches(controller, controller_name, controller_base_name):
                routes.append(RouteInfo(
                    path=path,
                    method=method,
                    controller=controller,
                    action=action,
                    middleware=[]
                ))

        # 模式3: Route::resource / Route::apiResource
        resource_pattern = r"Route::(resource|apiResource)\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*([^\),]+?)::class"

        for match in re.finditer(resource_pattern, content, re.IGNORECASE):
            resource_type = match.group(1).lower()
            resource_path = match.group(2)
            controller = match.group(3).strip().split("\\")[-1]

            if self._controller_matches(controller, controller_name, controller_base_name):
                # Resource 路由生成标准的 RESTful 路由
                if resource_type == "apiresource":
                    # apiResource 不包含 create 和 edit
                    resource_routes = [
                        ("GET", f"/{resource_path}", "index"),
                        ("POST", f"/{resource_path}", "store"),
                        ("GET", f"/{resource_path}/{{id}}", "show"),
                        ("PUT", f"/{resource_path}/{{id}}", "update"),
                        ("DELETE", f"/{resource_path}/{{id}}", "destroy"),
                    ]
                else:
                    # resource 包含所有 7 个方法
                    resource_routes = [
                        ("GET", f"/{resource_path}", "index"),
                        ("GET", f"/{resource_path}/create", "create"),
                        ("POST", f"/{resource_path}", "store"),
                        ("GET", f"/{resource_path}/{{id}}", "show"),
                        ("GET", f"/{resource_path}/{{id}}/edit", "edit"),
                        ("PUT", f"/{resource_path}/{{id}}", "update"),
                        ("DELETE", f"/{resource_path}/{{id}}", "destroy"),
                    ]

                for method, path, action in resource_routes:
                    routes.append(RouteInfo(
                        path=path,
                        method=method,
                        controller=controller,
                        action=action,
                        middleware=[]
                    ))

        # 模式4: Route::match(['get', 'post'], '/path', [...])
        match_pattern = r"Route::match\s*\(\s*\[([^\]]+)\]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*\[\s*([^\]]+?)::class\s*,\s*['\"](\w+)['\"]\s*\]"

        for match in re.finditer(match_pattern, content, re.IGNORECASE | re.DOTALL):
            methods_str = match.group(1)
            path = match.group(2)
            controller = match.group(3).strip().split("\\")[-1]
            action = match.group(4)

            if self._controller_matches(controller, controller_name, controller_base_name):
                # 解析方法列表
                methods = re.findall(r"['\"](\w+)['\"]", methods_str)
                for method in methods:
                    routes.append(RouteInfo(
                        path=path,
                        method=method.upper(),
                        controller=controller,
                        action=action,
                        middleware=[]
                    ))

        # 模式5: Route::any('/path', [...])
        any_pattern = r"Route::any\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*\[\s*([^\]]+?)::class\s*,\s*['\"](\w+)['\"]\s*\]"

        for match in re.finditer(any_pattern, content, re.IGNORECASE | re.DOTALL):
            path = match.group(1)
            controller = match.group(2).strip().split("\\")[-1]
            action = match.group(3)

            if self._controller_matches(controller, controller_name, controller_base_name):
                # any 支持所有 HTTP 方法
                routes.append(RouteInfo(
                    path=path,
                    method="ANY",
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
            controller_name: 目标控制器名称（如 UserController）
            controller_base_name: 目标控制器基础名称（如 User）

        Returns:
            bool: 是否匹配
        """
        # 精确匹配
        if found_controller == controller_name:
            return True

        # 去掉 Controller 后缀后匹配
        found_base = found_controller.replace("Controller", "")
        if found_base == controller_base_name:
            return True

        # 包含匹配（用于处理命名空间前缀的情况）
        if controller_name in found_controller or found_controller in controller_name:
            return True

        return False

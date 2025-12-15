"""
部署 API 封装模块
处理项目列表获取、单个项目发版、批量发版等功能
"""

import sys
import io
import requests
import time
from typing import List, Dict, Any, Optional
from config import (
    PROJECT_LIST_API,
    DEPLOY_API,
    TOKEN,
    TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY
)

# 注意：不在模块级别重新包装 stdout/stderr
# 这会影响导入此模块的 MCP 服务器的 stdio 通信


class DeployAPIError(Exception):
    """部署 API 错误"""
    pass


def get_project_list() -> Dict[str, Any]:
    """
    获取项目列表（过滤不需要发版的项目）

    过滤规则:
    - is_release=1: 不需要发版
    - release_type=1: 需要 k8s 流水线发版
    - 只返回需要通过部署 API 发版的项目

    Returns:
        包含项目列表的字典
        {
            "total": 20,
            "projects": [
                {"project_id": 1, "project_name": "www", ...},
                ...
            ],
            "filtered_count": 24
        }

    Raises:
        DeployAPIError: 当 API 调用失败时抛出
    """
    for retry in range(MAX_RETRIES):
        try:
            response = requests.get(PROJECT_LIST_API, timeout=TIMEOUT)
            response.raise_for_status()

            data = response.json()

            if data.get("status") == 200:
                all_projects = data.get("data", [])

                # 过滤项目:
                # 1. is_release != 1 (需要发版)
                # 2. release_type != 1 (不使用 k8s 流水线)
                filtered_projects = [
                    p for p in all_projects
                    if p.get("is_release") != 1 and p.get("release_type") != 1
                ]

                filtered_count = len(all_projects) - len(filtered_projects)

                return {
                    "total": len(filtered_projects),
                    "projects": filtered_projects,
                    "filtered_count": filtered_count
                }
            else:
                raise DeployAPIError(f"API 返回错误: {data.get('msg', '未知错误')}")

        except requests.RequestException as e:
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise DeployAPIError(f"获取项目列表失败: {str(e)}")

    raise DeployAPIError("获取项目列表失败: 超过最大重试次数")


def validate_project(project_name: str) -> bool:
    """
    验证项目名是否在可发版列表中

    Args:
        project_name: 项目名称

    Returns:
        如果项目存在返回 True，否则返回 False
    """
    try:
        result = get_project_list()
        project_names = [p["project_name"] for p in result["projects"]]
        return project_name in project_names
    except DeployAPIError:
        return False


def deploy_project(project_name: str, validate: bool = True) -> Dict[str, Any]:
    """
    发版单个项目

    Args:
        project_name: 项目名称
        validate: 是否验证项目名（默认 True）

    Returns:
        发版结果字典
        {
            "project": "3d",
            "status": "success",
            "output": "Git 操作日志..."
        }

    Raises:
        DeployAPIError: 当项目不存在或 API 调用失败时抛出
    """
    # 验证项目名
    if validate and not validate_project(project_name):
        raise DeployAPIError(f"项目 '{project_name}' 不在可发版列表中")

    # 构造 URL
    url = f"{DEPLOY_API}?token={TOKEN}&project={project_name}"

    for retry in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()

            return {
                "project": project_name,
                "status": "success",
                "output": response.text
            }

        except requests.RequestException as e:
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue

            return {
                "project": project_name,
                "status": "error",
                "error": f"发版失败: {str(e)}"
            }

    return {
        "project": project_name,
        "status": "error",
        "error": "发版失败: 超过最大重试次数"
    }


def batch_deploy(project_names: List[str], validate: bool = True) -> List[Dict[str, Any]]:
    """
    批量发版（串行执行）

    Args:
        project_names: 项目名称列表
        validate: 是否验证项目名（默认 True）

    Returns:
        每个项目的发版结果列表
    """
    results = []

    for project_name in project_names:
        try:
            result = deploy_project(project_name, validate=validate)
            results.append(result)
        except DeployAPIError as e:
            results.append({
                "project": project_name,
                "status": "error",
                "error": str(e)
            })

    return results


def deploy_all(exclude: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    发版所有项目（可排除指定项目）

    Args:
        exclude: 要排除的项目名称列表（可选）

    Returns:
        所有项目的发版结果列表

    Raises:
        DeployAPIError: 当获取项目列表失败时抛出
    """
    # 获取项目列表
    project_list = get_project_list()
    all_projects = [p["project_name"] for p in project_list["projects"]]

    # 过滤排除的项目
    exclude = exclude or []
    projects_to_deploy = [p for p in all_projects if p not in exclude]

    # 批量发版
    return batch_deploy(projects_to_deploy, validate=False)

"""测试配置和固件"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings, DatabaseConfig, Settings
from core.connection_pool import ConnectionPool
from database.operations import DatabaseOperations


@pytest.fixture(scope="session")
def test_settings():
    """
    测试环境配置

    注意：这将使用实际的数据库配置，因为精简版不包含 Mock
    如果需要隔离测试，请考虑使用测试数据库
    """
    return get_settings()


@pytest.fixture(scope="session")
def connection_pool(test_settings):
    """
    连接池固件（会话级别，整个测试会话共享）
    """
    pool = ConnectionPool()
    pool.initialize(test_settings)
    yield pool
    # 清理资源（如果需要）


@pytest.fixture(scope="function")
def db_ops(connection_pool):
    """
    数据库操作实例固件（函数级别，每个测试函数独立）
    """
    return DatabaseOperations(connection_pool)


@pytest.fixture
def sample_database():
    """
    提供一个样本数据库名称用于测试

    注意：使用实际存在的数据库
    """
    return "master_3d66_user"


@pytest.fixture
def sample_table():
    """
    提供一个样本表名称用于测试
    """
    return "ll_recharge_success"

"""配置系统测试"""

import pytest
from config.settings import get_settings, DatabaseConfig, ConnectionPoolConfig


@pytest.mark.unit
def test_get_settings():
    """测试获取设置"""
    settings = get_settings()

    # 验证设置对象
    assert settings is not None
    assert hasattr(settings, "database")
    assert hasattr(settings, "pool")


@pytest.mark.unit
def test_database_config():
    """测试数据库配置"""
    settings = get_settings()
    db_config = settings.database

    # 验证数据库配置
    assert isinstance(db_config, DatabaseConfig)
    assert hasattr(db_config, "host")
    assert hasattr(db_config, "port")
    assert hasattr(db_config, "user")
    assert hasattr(db_config, "password")
    assert hasattr(db_config, "charset")

    # 验证默认值
    assert db_config.port == 3306
    assert db_config.charset == "utf8mb4"


@pytest.mark.unit
def test_connection_pool_config():
    """测试连接池配置"""
    settings = get_settings()
    pool_config = settings.pool

    # 验证连接池配置
    assert isinstance(pool_config, ConnectionPoolConfig)
    assert hasattr(pool_config, "pool_size")
    assert hasattr(pool_config, "max_overflow")
    assert hasattr(pool_config, "pool_timeout")
    assert hasattr(pool_config, "pool_recycle")

    # 验证默认值和范围
    assert 1 <= pool_config.pool_size <= 20
    assert pool_config.max_overflow >= 0
    assert pool_config.pool_timeout > 0
    assert pool_config.pool_recycle > 0


@pytest.mark.unit
def test_settings_singleton():
    """测试设置单例模式"""
    settings1 = get_settings()
    settings2 = get_settings()

    # 验证返回的是同一个实例
    assert settings1 is settings2

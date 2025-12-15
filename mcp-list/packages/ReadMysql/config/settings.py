"""配置管理模块 - 使用 Pydantic 进行配置管理和验证"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

# 获取 ReadMysql 项目根目录的绝对路径
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class DatabaseConfig(BaseSettings):
    """数据库配置"""

    host: str = Field(default="localhost", description="数据库主机地址")
    port: int = Field(default=3306, ge=1, le=65535, description="数据库端口")
    user: str = Field(description="数据库用户名")
    password: str = Field(description="数据库密码")
    charset: str = Field(default="utf8mb4", description="字符集")

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        """验证端口号范围"""
        if not 1 <= v <= 65535:
            raise ValueError(f"端口号必须在 1-65535 之间，当前值: {v}")
        return v


class ConnectionPoolConfig(BaseSettings):
    """连接池配置"""

    pool_size: int = Field(default=5, ge=1, le=20, description="连接池大小")
    max_overflow: int = Field(default=10, ge=0, le=50, description="最大溢出连接数")
    pool_timeout: int = Field(default=30, ge=1, description="获取连接超时时间（秒）")
    pool_recycle: int = Field(default=3600, ge=60, description="连接回收时间（秒）")

    model_config = SettingsConfigDict(
        env_prefix="POOL_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator('pool_size')
    @classmethod
    def validate_pool_size(cls, v: int) -> int:
        """验证连接池大小"""
        if not 1 <= v <= 20:
            raise ValueError(f"连接池大小必须在 1-20 之间，当前值: {v}")
        return v


class QueryConfig(BaseSettings):
    """查询配置"""

    max_rows: int = Field(default=1000, ge=1, le=10000, description="单次查询最大返回行数")
    timeout: int = Field(default=30, ge=1, le=300, description="查询超时时间（秒）")
    enable_cache: bool = Field(default=False, description="是否启用查询缓存")
    cache_ttl: int = Field(default=300, ge=0, description="缓存过期时间（秒）")

    model_config = SettingsConfigDict(
        env_prefix="QUERY_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )


class Settings(BaseSettings):
    """全局配置"""

    environment: str = Field(default="production", description="运行环境 (development/production)")
    debug: bool = Field(default=False, description="是否启用调试模式")

    # 子配置
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    pool: ConnectionPoolConfig = Field(default_factory=ConnectionPoolConfig)
    query: QueryConfig = Field(default_factory=QueryConfig)

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> "Settings":
        """
        加载配置

        Args:
            env_file: 环境变量文件路径，默认为 .env

        Returns:
            Settings 实例
        """
        # 如果没有指定 env_file，检查是否存在 .env 文件
        if env_file is None:
            current_dir = Path(__file__).parent.parent
            default_env = current_dir / ".env"
            if default_env.exists():
                env_file = str(default_env)

        # 如果提供了 env_file 参数，使用它
        if env_file:
            os.environ.setdefault("SETTINGS_ENV_FILE", env_file)

        # 创建实例时会自动读取环境变量和 .env 文件
        try:
            return cls()
        except Exception as e:
            # 如果加载失败，尝试从旧的 config.py 加载
            return cls._load_from_legacy_config()

    @classmethod
    def _load_from_legacy_config(cls) -> "Settings":
        """从旧的 config.py 加载配置（向后兼容）"""
        try:
            import sys
            from pathlib import Path

            # 添加父目录到 sys.path
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            # 尝试导入旧的 config
            try:
                from config import DB_CONFIG, QUERY_CONFIG

                return cls(
                    database=DatabaseConfig(
                        host=DB_CONFIG.get("host", "localhost"),
                        port=DB_CONFIG.get("port", 3306),
                        user=DB_CONFIG.get("user", "root"),
                        password=DB_CONFIG.get("password", ""),
                        charset=DB_CONFIG.get("charset", "utf8mb4")
                    ),
                    query=QueryConfig(
                        max_rows=QUERY_CONFIG.get("max_rows", 1000),
                        timeout=QUERY_CONFIG.get("timeout", 30)
                    )
                )
            except ImportError:
                # 如果无法导入，使用默认配置
                raise ValueError(
                    "无法加载配置：请创建 .env 文件或确保旧的 config.py 存在"
                )
        except Exception as e:
            raise ValueError(f"配置加载失败: {str(e)}")


# 全局配置实例（懒加载）
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置实例（单例模式）"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings.load()
    return _settings_instance

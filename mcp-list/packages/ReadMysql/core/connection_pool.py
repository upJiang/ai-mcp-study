"""数据库连接池管理 - 使用 DBUtils 实现高性能连接复用"""

import logging
from contextlib import contextmanager
from typing import Optional, Generator
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB

from .exceptions import ConnectionError as CustomConnectionError, ConfigurationError


logger = logging.getLogger(__name__)


class ConnectionPool:
    """数据库连接池 - 单例模式

    使用 DBUtils.PooledDB 实现连接池，提供以下特性：
    - 连接复用：减少连接创建和销毁的开销
    - 自动重连：检测并处理断开的连接
    - 线程安全：支持多线程并发访问
    - 连接回收：定期回收空闲连接
    - 连接验证：获取连接前自动验证可用性

    示例:
        >>> from config.settings import get_settings
        >>> pool = ConnectionPool()
        >>> pool.initialize(get_settings())
        >>>
        >>> with pool.get_connection() as conn:
        >>>     with conn.cursor() as cursor:
        >>>         cursor.execute("SELECT 1")
        >>>         result = cursor.fetchone()
    """

    _instance: Optional['ConnectionPool'] = None
    _pool: Optional[PooledDB] = None
    _initialized: bool = False

    def __new__(cls) -> 'ConnectionPool':
        """单例模式：确保只有一个连接池实例"""
        if cls._instance is None:
            cls._instance = super(ConnectionPool, cls).__new__(cls)
        return cls._instance

    def initialize(self, settings) -> None:
        """
        初始化连接池

        Args:
            settings: Settings 配置对象

        Raises:
            ConfigurationError: 配置错误
            CustomConnectionError: 连接初始化失败
        """
        if self._initialized:
            logger.warning("连接池已经初始化，跳过重复初始化")
            return

        try:
            logger.info("开始初始化数据库连接池...")
            logger.info(f"数据库配置: {settings.database.host}:{settings.database.port}")
            logger.info(
                f"连接池配置: size={settings.pool.pool_size}, "
                f"max_overflow={settings.pool.max_overflow}, "
                f"timeout={settings.pool.pool_timeout}s, "
                f"recycle={settings.pool.pool_recycle}s"
            )

            # 创建连接池
            self._pool = PooledDB(
                # 数据库驱动
                creator=pymysql,

                # 连接池配置
                maxconnections=settings.pool.pool_size + settings.pool.max_overflow,
                mincached=settings.pool.pool_size,
                maxcached=settings.pool.pool_size,
                maxshared=0,  # 不使用共享连接
                blocking=True,  # 连接池满时阻塞等待
                maxusage=0,  # 连接无限次使用
                setsession=[],  # 连接创建时执行的 SQL
                ping=1,  # 获取连接时检查可用性（1=默认检查）

                # 数据库连接参数
                host=settings.database.host,
                port=settings.database.port,
                user=settings.database.user,
                password=settings.database.password,
                charset=settings.database.charset,
                cursorclass=DictCursor,  # 使用字典游标，返回 dict 格式结果

                # 连接超时和回收
                connect_timeout=settings.pool.pool_timeout,
                read_timeout=settings.query.timeout,
                write_timeout=settings.query.timeout,

                # 自动提交（只读操作，无需事务）
                autocommit=True,
            )

            # 标记为已初始化（在测试前，因为测试需要使用 get_connection）
            self._initialized = True

            # 测试连接池
            try:
                self._test_pool()
                logger.info("✓ 数据库连接池初始化成功")
            except Exception:
                # 如果测试失败，重置初始化标志
                self._initialized = False
                raise

        except pymysql.Error as e:
            error_msg = f"连接池初始化失败: 无法连接到数据库"
            logger.error(f"{error_msg} - {str(e)}")
            raise CustomConnectionError(
                error_msg,
                host=settings.database.host,
                port=settings.database.port,
                original_error=e
            ) from e

        except Exception as e:
            error_msg = f"连接池初始化失败: {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, original_error=e) from e

    def _test_pool(self) -> None:
        """
        测试连接池是否正常工作

        Raises:
            CustomConnectionError: 连接测试失败
        """
        try:
            logger.debug("测试连接池...")
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 AS test")
                    result = cursor.fetchone()
                    if result['test'] != 1:
                        raise CustomConnectionError("连接池测试失败: 查询结果不正确")
            logger.debug("✓ 连接池测试通过")

        except Exception as e:
            raise CustomConnectionError(
                f"连接池测试失败: {str(e)}",
                original_error=e
            ) from e

    @contextmanager
    def get_connection(self, database: Optional[str] = None) -> Generator:
        """
        获取数据库连接（上下文管理器）

        这是获取连接的推荐方式，会自动处理连接的获取和释放。

        Args:
            database: 可选的数据库名称，如果指定则切换到该数据库

        Yields:
            pymysql.Connection: 数据库连接对象

        Raises:
            ConfigurationError: 连接池未初始化
            CustomConnectionError: 获取连接失败

        示例:
            >>> with pool.get_connection('mydb') as conn:
            >>>     with conn.cursor() as cursor:
            >>>         cursor.execute("SELECT * FROM users LIMIT 10")
            >>>         users = cursor.fetchall()
        """
        if not self._initialized or self._pool is None:
            raise ConfigurationError("连接池未初始化，请先调用 initialize() 方法")

        conn = None
        try:
            # 从连接池获取连接
            conn = self._pool.connection()
            logger.debug(f"✓ 从连接池获取连接 (database={database or 'None'})")

            # 如果指定了数据库，切换到该数据库
            if database:
                try:
                    # DBUtils 包装的连接没有 select_db 方法，使用 SQL 语句切换数据库
                    with conn.cursor() as cursor:
                        cursor.execute(f"USE `{database}`")
                    logger.debug(f"✓ 切换到数据库: {database}")
                except pymysql.Error as e:
                    raise CustomConnectionError(
                        f"切换到数据库 '{database}' 失败",
                        original_error=e
                    ) from e

            yield conn

        except pymysql.Error as e:
            logger.error(f"数据库连接错误: {str(e)}")
            raise CustomConnectionError(
                f"获取数据库连接失败: {str(e)}",
                original_error=e
            ) from e

        except Exception as e:
            logger.error(f"连接池错误: {str(e)}")
            raise

        finally:
            # 连接会被 DBUtils 自动归还到池中
            if conn:
                try:
                    conn.close()  # close() 实际上是归还到池中
                    logger.debug("✓ 连接已归还到连接池")
                except Exception as e:
                    logger.warning(f"归还连接时出错（通常可以忽略）: {str(e)}")

    def get_pool_stats(self) -> dict:
        """
        获取连接池统计信息

        Returns:
            包含连接池状态的字典

        示例返回:
            {
                'initialized': True,
                'pool_size': 5,
                'available': 4,
                'in_use': 1
            }
        """
        if not self._initialized or self._pool is None:
            return {
                'initialized': False,
                'pool_size': 0,
                'available': 0,
                'in_use': 0
            }

        try:
            # DBUtils 的 PooledDB 没有直接提供统计信息的 API
            # 这里返回配置信息
            return {
                'initialized': True,
                'pool_configured': True,
                'note': 'DBUtils.PooledDB 不提供实时统计信息'
            }
        except Exception as e:
            logger.warning(f"获取连接池统计信息失败: {str(e)}")
            return {
                'initialized': True,
                'error': str(e)
            }

    def close_all(self) -> None:
        """
        关闭连接池中的所有连接

        通常在应用程序关闭时调用。
        注意：DBUtils 的 PooledDB 会在对象销毁时自动清理连接。
        """
        if self._pool is None:
            logger.warning("连接池未初始化，无需关闭")
            return

        try:
            logger.info("关闭数据库连接池...")
            # DBUtils 的 PooledDB 没有显式的 close 方法
            # 连接会在对象销毁时自动清理
            self._pool = None
            self._initialized = False
            logger.info("✓ 连接池已关闭")

        except Exception as e:
            logger.error(f"关闭连接池时出错: {str(e)}")

    def __del__(self):
        """析构函数：确保连接池被正确关闭"""
        try:
            if self._initialized and self._pool:
                self.close_all()
        except Exception:
            pass  # 析构函数中忽略所有错误

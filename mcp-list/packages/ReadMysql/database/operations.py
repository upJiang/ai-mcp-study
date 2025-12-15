"""数据库操作层 - 使用连接池的高性能数据库操作实现

重构自 mysql_api.py，主要改进：
1. 使用连接池替代直接连接
2. 添加完整的类型提示
3. 增强异常处理和错误分类
4. 添加连接错误重试机制
5. 保持与旧 API 完全兼容
"""

import logging
import time
from typing import List, Dict, Any, Optional
from functools import wraps

from core.connection_pool import ConnectionPool
from core.exceptions import (
    QueryError,
    ValidationError,
    is_retryable_error
)
from config.settings import get_settings
from core.query_logger import get_logger


logger = logging.getLogger(__name__)
query_logger = get_logger()


def retry_on_connection_error(max_retries: int = 3, delay: float = 1.0):
    """
    连接错误重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟时间（秒）

    Returns:
        装饰后的函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if is_retryable_error(e) and attempt < max_retries - 1:
                        logger.warning(
                            f"操作失败（可重试），第 {attempt + 1}/{max_retries} 次尝试: {str(e)}"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        # 不可重试或已达最大重试次数
                        raise

            # 理论上不会到这里，但为了类型检查
            raise last_error

        return wrapper
    return decorator


class DatabaseOperations:
    """数据库操作类 - 提供所有数据库操作的高层 API

    这个类使用连接池来管理数据库连接，提供以下功能：
    - 列出所有数据库
    - 列出数据库中的表
    - 获取表结构
    - 执行 SELECT 查询（只读）
    - 获取表的详细信息

    示例:
        >>> from config.settings import get_settings
        >>> from core.connection_pool import ConnectionPool
        >>> pool = ConnectionPool()
        >>> pool.initialize(get_settings())
        >>> db_ops = DatabaseOperations(pool)
        >>> databases = db_ops.list_databases()
        >>> tables = db_ops.list_tables('mydb')
    """

    def __init__(self, pool: Optional[ConnectionPool] = None):
        """
        初始化数据库操作对象

        Args:
            pool: 连接池对象，如果为 None 则使用全局单例
        """
        self.pool = pool or ConnectionPool()
        self.settings = get_settings()

    @retry_on_connection_error(max_retries=3, delay=1.0)
    def list_databases(self) -> List[str]:
        """
        获取所有数据库列表

        Returns:
            数据库名称列表

        Raises:
            QueryError: 查询失败
        """
        try:
            with self.pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW DATABASES")
                    databases = [row['Database'] for row in cursor.fetchall()]
                    logger.info(f"✓ 获取到 {len(databases)} 个数据库")
                    return databases

        except Exception as e:
            logger.error(f"获取数据库列表失败: {str(e)}")
            raise QueryError(
                "获取数据库列表失败",
                query="SHOW DATABASES",
                original_error=e
            ) from e

    @retry_on_connection_error(max_retries=3, delay=1.0)
    def list_tables(self, database: str) -> List[str]:
        """
        获取指定数据库的所有表

        Args:
            database: 数据库名称

        Returns:
            表名称列表

        Raises:
            ValidationError: 数据库名称无效
            QueryError: 查询失败
        """
        if not database or not isinstance(database, str):
            raise ValidationError(
                "数据库名称无效",
                field="database",
                value=database
            )

        try:
            with self.pool.get_connection(database) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SHOW TABLES")
                    # SHOW TABLES 返回的字段名是 "Tables_in_{database}"
                    key = f"Tables_in_{database}"
                    tables = [row[key] for row in cursor.fetchall()]
                    logger.info(f"✓ 数据库 {database} 有 {len(tables)} 个表")
                    return tables

        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            raise QueryError(
                f"获取数据库 '{database}' 的表列表失败",
                query="SHOW TABLES",
                database=database,
                original_error=e
            ) from e

    @retry_on_connection_error(max_retries=3, delay=1.0)
    def describe_table(self, database: str, table: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息

        Args:
            database: 数据库名称
            table: 表名称

        Returns:
            表结构信息列表，每个元素包含字段信息

        Raises:
            ValidationError: 参数无效
            QueryError: 查询失败
        """
        if not database or not isinstance(database, str):
            raise ValidationError(
                "数据库名称无效",
                field="database",
                value=database
            )

        if not table or not isinstance(table, str):
            raise ValidationError(
                "表名称无效",
                field="table",
                value=table
            )

        try:
            with self.pool.get_connection(database) as conn:
                with conn.cursor() as cursor:
                    # 使用反引号防止表名是保留字
                    cursor.execute(f"DESCRIBE `{table}`")
                    structure = cursor.fetchall()
                    logger.info(f"✓ 获取表 {database}.{table} 的结构信息（{len(structure)} 个字段）")
                    return structure

        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            raise QueryError(
                f"获取表 '{database}.{table}' 的结构失败",
                query=f"DESCRIBE `{table}`",
                database=database,
                original_error=e
            ) from e

    @retry_on_connection_error(max_retries=3, delay=1.0)
    def execute_query(
        self,
        database: str,
        query: str,
        params: Optional[tuple] = None,
        limit: Optional[int] = None,
        tool_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行 SQL 查询（仅支持 SELECT）

        Args:
            database: 数据库名称
            query: SQL 查询语句
            params: 查询参数（用于参数化查询，防止 SQL 注入）
            limit: 限制返回行数，默认使用配置的最大值
            tool_name: MCP 工具名称（用于日志记录）

        Returns:
            包含查询结果和元数据的字典:
            {
                "success": bool,
                "row_count": int,
                "data": List[Dict],
                "columns": List[str],
                "error": str (仅当 success=False)
            }

        Raises:
            ValidationError: 查询验证失败（非 SELECT 语句）
            QueryError: 查询执行失败
        """
        start_time = time.time()

        # 验证数据库名称
        if not database or not isinstance(database, str):
            raise ValidationError(
                "数据库名称无效",
                field="database",
                value=database
            )

        # 验证查询语句
        if not query or not isinstance(query, str):
            raise ValidationError(
                "查询语句无效",
                field="query",
                value=query
            )

        # 验证查询是否为 SELECT 语句
        query_stripped = query.strip().upper()
        if not query_stripped.startswith('SELECT'):
            error_msg = "只允许执行 SELECT 查询语句"
            query_logger.log_query(
                database=database,
                query=query,
                success=False,
                error=error_msg,
                tool_name=tool_name
            )
            raise ValidationError(
                error_msg,
                field="query",
                value=query[:100]  # 只记录前 100 个字符
            )

        # 应用行数限制
        if limit is None:
            limit = self.settings.query.max_rows
        else:
            limit = min(limit, self.settings.query.max_rows)

        # 如果查询中没有 LIMIT 子句，添加一个
        if 'LIMIT' not in query_stripped:
            query = f"{query.rstrip(';')} LIMIT {limit}"

        try:
            with self.pool.get_connection(database) as conn:
                with conn.cursor() as cursor:
                    # 执行查询（使用参数化查询防止 SQL 注入）
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                    results = cursor.fetchall()
                    row_count = len(results)
                    execution_time = time.time() - start_time

                    logger.info(
                        f"✓ 查询成功，返回 {row_count} 行数据 "
                        f"(用时 {execution_time:.3f}s)"
                    )

                    # 记录查询日志
                    query_logger.log_query(
                        database=database,
                        query=query,
                        success=True,
                        row_count=row_count,
                        execution_time=execution_time,
                        tool_name=tool_name
                    )

                    return {
                        "success": True,
                        "row_count": row_count,
                        "data": results,
                        "columns": [desc[0] for desc in cursor.description] if cursor.description else []
                    }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"查询执行失败: {str(e)}")

            # 记录失败日志
            query_logger.log_query(
                database=database,
                query=query,
                success=False,
                execution_time=execution_time,
                error=str(e),
                tool_name=tool_name
            )

            # 返回错误信息（向后兼容）
            return {
                "success": False,
                "error": str(e),
                "row_count": 0,
                "data": [],
                "columns": []
            }

    @retry_on_connection_error(max_retries=3, delay=1.0)
    def get_table_info(self, database: str, table: str) -> Dict[str, Any]:
        """
        获取表的详细信息（包括结构、行数和创建语句）

        Args:
            database: 数据库名称
            table: 表名称

        Returns:
            表的详细信息字典:
            {
                "database": str,
                "table": str,
                "structure": List[Dict],  # 字段结构
                "row_count": int,         # 行数
                "create_statement": str   # CREATE TABLE 语句
            }

        Raises:
            ValidationError: 参数无效
            QueryError: 查询失败
        """
        if not database or not isinstance(database, str):
            raise ValidationError(
                "数据库名称无效",
                field="database",
                value=database
            )

        if not table or not isinstance(table, str):
            raise ValidationError(
                "表名称无效",
                field="table",
                value=table
            )

        try:
            with self.pool.get_connection(database) as conn:
                with conn.cursor() as cursor:
                    # 获取表结构
                    cursor.execute(f"DESCRIBE `{table}`")
                    structure = cursor.fetchall()

                    # 获取表的行数
                    cursor.execute(f"SELECT COUNT(*) as count FROM `{table}`")
                    count_result = cursor.fetchone()
                    row_count = count_result['count'] if count_result else 0

                    # 获取表的创建语句
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    create_table = cursor.fetchone()

                    logger.info(
                        f"✓ 获取表 {database}.{table} 的详细信息 "
                        f"({len(structure)} 个字段, {row_count} 行)"
                    )

                    return {
                        "database": database,
                        "table": table,
                        "structure": structure,
                        "row_count": row_count,
                        "create_statement": create_table['Create Table'] if create_table else None
                    }

        except Exception as e:
            logger.error(f"获取表信息失败: {str(e)}")
            raise QueryError(
                f"获取表 '{database}.{table}' 的详细信息失败",
                database=database,
                original_error=e
            ) from e

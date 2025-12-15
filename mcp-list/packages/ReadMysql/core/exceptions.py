"""自定义异常类 - 提供更精确的错误处理和分类"""

from typing import Optional


class MySQLError(Exception):
    """MySQL 错误基类

    所有自定义 MySQL 相关异常的基类
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Args:
            message: 错误描述信息
            original_error: 原始异常对象（如果有）
        """
        super().__init__(message)
        self.message = message
        self.original_error = original_error

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message} (原始错误: {str(self.original_error)})"
        return self.message


class ConnectionError(MySQLError):
    """连接错误 - 可重试的错误

    包括但不限于：
    - 无法连接到数据库服务器
    - 连接超时
    - 连接池耗尽
    - 网络问题

    这类错误通常是临时的，可以通过重试解决
    """

    def __init__(self, message: str, host: Optional[str] = None,
                 port: Optional[int] = None, original_error: Optional[Exception] = None):
        """
        Args:
            message: 错误描述
            host: 数据库主机地址
            port: 数据库端口
            original_error: 原始异常
        """
        super().__init__(message, original_error)
        self.host = host
        self.port = port

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.host and self.port:
            return f"{base_msg} (主机: {self.host}:{self.port})"
        return base_msg


class QueryError(MySQLError):
    """查询错误 - 不可重试的错误

    包括但不限于：
    - SQL 语法错误
    - 表或字段不存在
    - 权限不足
    - 数据类型不匹配

    这类错误是由于查询本身的问题，重试不会解决
    """

    def __init__(self, message: str, query: Optional[str] = None,
                 database: Optional[str] = None, original_error: Optional[Exception] = None):
        """
        Args:
            message: 错误描述
            query: 导致错误的 SQL 查询
            database: 数据库名称
            original_error: 原始异常
        """
        super().__init__(message, original_error)
        self.query = query
        self.database = database

    def __str__(self) -> str:
        base_msg = super().__str__()
        parts = [base_msg]

        if self.database:
            parts.append(f"数据库: {self.database}")

        if self.query:
            # 截断过长的查询语句
            query_preview = self.query if len(self.query) <= 100 else f"{self.query[:100]}..."
            parts.append(f"查询: {query_preview}")

        return " | ".join(parts)


class ValidationError(MySQLError):
    """验证错误 - 输入参数验证失败

    包括但不限于：
    - 无效的数据库名称
    - 无效的表名称
    - SQL 查询不是 SELECT 语句
    - 参数类型错误
    - 参数超出允许范围
    """

    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[any] = None, original_error: Optional[Exception] = None):
        """
        Args:
            message: 错误描述
            field: 导致错误的字段名
            value: 导致错误的值
            original_error: 原始异常
        """
        super().__init__(message, original_error)
        self.field = field
        self.value = value

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.field:
            return f"{base_msg} (字段: {self.field}, 值: {self.value})"
        return base_msg


class ConfigurationError(MySQLError):
    """配置错误 - 配置文件或环境变量问题

    包括但不限于：
    - 缺少必需的配置项
    - 配置值格式错误
    - 配置文件不存在或无法读取
    - 环境变量未设置
    """

    def __init__(self, message: str, config_key: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        """
        Args:
            message: 错误描述
            config_key: 导致错误的配置键
            original_error: 原始异常
        """
        super().__init__(message, original_error)
        self.config_key = config_key

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.config_key:
            return f"{base_msg} (配置项: {self.config_key})"
        return base_msg


# 错误重试判断函数
def is_retryable_error(error: Exception) -> bool:
    """
    判断错误是否可以重试

    Args:
        error: 异常对象

    Returns:
        True 如果错误可以重试，False 否则
    """
    # ConnectionError 是可重试的
    if isinstance(error, ConnectionError):
        return True

    # 其他类型的 MySQLError 不可重试
    if isinstance(error, MySQLError):
        return False

    # 检查原始 pymysql 错误
    import pymysql

    # pymysql 连接相关错误（可重试）
    if isinstance(error, (
        pymysql.err.OperationalError,  # 操作错误（通常是连接问题）
        pymysql.err.InterfaceError,    # 接口错误
    )):
        # 检查错误代码，某些操作错误不应重试
        if hasattr(error, 'args') and len(error.args) > 0:
            error_code = error.args[0]
            # 2003: Can't connect to MySQL server
            # 2006: MySQL server has gone away
            # 2013: Lost connection to MySQL server
            if error_code in (2003, 2006, 2013):
                return True
        return True

    # pymysql 查询相关错误（不可重试）
    if isinstance(error, (
        pymysql.err.ProgrammingError,  # 编程错误（SQL 语法等）
        pymysql.err.DataError,          # 数据错误
        pymysql.err.IntegrityError,     # 完整性错误
        pymysql.err.NotSupportedError,  # 不支持的操作
    )):
        return False

    # 默认不重试
    return False

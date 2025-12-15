"""数据库操作测试"""

import pytest


@pytest.mark.integration
def test_list_databases(db_ops):
    """测试列出数据库"""
    databases = db_ops.list_databases()

    # 验证返回的是列表
    assert isinstance(databases, list)

    # 验证至少有一个数据库
    assert len(databases) > 0

    # 验证数据库名称是字符串
    assert all(isinstance(db, str) for db in databases)


@pytest.mark.integration
def test_list_tables(db_ops, sample_database):
    """测试列出表"""
    tables = db_ops.list_tables(sample_database)

    # 验证返回的是列表
    assert isinstance(tables, list)

    # 验证表名称是字符串
    assert all(isinstance(table, str) for table in tables)


@pytest.mark.integration
def test_describe_table(db_ops, sample_database, sample_table):
    """测试描述表结构"""
    structure = db_ops.describe_table(sample_database, sample_table)

    # 验证返回的是列表
    assert isinstance(structure, list)

    # 验证至少有一个字段
    assert len(structure) > 0

    # 验证字段结构
    for field in structure:
        assert isinstance(field, dict)
        assert "Field" in field
        assert "Type" in field
        assert "Null" in field
        assert "Key" in field


@pytest.mark.integration
def test_get_table_info(db_ops, sample_database, sample_table):
    """测试获取表完整信息"""
    info = db_ops.get_table_info(sample_database, sample_table)

    # 验证返回的是字典
    assert isinstance(info, dict)

    # 验证必需的键
    assert "database" in info
    assert "table" in info
    assert "structure" in info
    assert "row_count" in info

    # 验证值的类型
    assert info["database"] == sample_database
    assert info["table"] == sample_table
    assert isinstance(info["structure"], list)
    assert isinstance(info["row_count"], int)
    assert info["row_count"] >= 0


@pytest.mark.integration
def test_execute_query_select(db_ops, sample_database, sample_table):
    """测试执行 SELECT 查询"""
    query = f"SELECT * FROM {sample_table} LIMIT 5"

    result = db_ops.execute_query(
        database=sample_database,
        query=query,
        tool_name="test_execute_query_select"
    )

    # 验证返回结果
    assert isinstance(result, dict)
    assert "success" in result
    assert result["success"] is True

    # 验证数据
    if result.get("data"):
        assert isinstance(result["data"], list)
        assert len(result["data"]) <= 5


@pytest.mark.integration
def test_execute_query_with_limit(db_ops, sample_database, sample_table):
    """测试执行带限制的查询"""
    query = f"SELECT * FROM {sample_table}"

    result = db_ops.execute_query(
        database=sample_database,
        query=query,
        limit=10,
        tool_name="test_execute_query_with_limit"
    )

    # 验证返回结果
    assert isinstance(result, dict)
    assert result["success"] is True

    # 验证数据数量不超过限制
    if result.get("data"):
        assert len(result["data"]) <= 10


@pytest.mark.integration
def test_execute_query_invalid_sql(db_ops, sample_database):
    """测试执行无效的 SQL 查询"""
    query = "SELECT * FROM non_existent_table_12345"

    result = db_ops.execute_query(
        database=sample_database,
        query=query,
        tool_name="test_execute_query_invalid_sql"
    )

    # 验证返回错误
    assert isinstance(result, dict)
    assert "success" in result
    assert result["success"] is False
    assert "error" in result


@pytest.mark.integration
def test_execute_query_non_select(db_ops, sample_database):
    """测试执行非 SELECT 查询（应该被拒绝）"""
    query = "DELETE FROM some_table WHERE id = 1"

    result = db_ops.execute_query(
        database=sample_database,
        query=query,
        tool_name="test_execute_query_non_select"
    )

    # 验证返回错误（只允许 SELECT 查询）
    assert isinstance(result, dict)
    assert "success" in result
    assert result["success"] is False
    assert "error" in result
    assert "只允许" in result["error"] or "SELECT" in result["error"]

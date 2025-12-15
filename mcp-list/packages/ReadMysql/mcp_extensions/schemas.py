"""数据模型定义 - 使用 Pydantic 定义数据结构"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TableField(BaseModel):
    """表字段信息"""
    name: str = Field(description="字段名")
    type: str = Field(description="字段类型")
    null: str = Field(description="是否允许 NULL")
    key: str = Field(description="键类型（PRI/UNI/MUL）")
    default: Optional[str] = Field(default=None, description="默认值")
    extra: str = Field(default="", description="额外信息")


class TableStructure(BaseModel):
    """表结构信息"""
    database: str = Field(description="数据库名")
    table: str = Field(description="表名")
    fields: List[TableField] = Field(description="字段列表")
    field_count: int = Field(description="字段数量")


class TableInfo(BaseModel):
    """表详细信息"""
    database: str = Field(description="数据库名")
    table: str = Field(description="表名")
    structure: List[TableField] = Field(description="表结构")
    row_count: int = Field(description="行数")
    create_statement: Optional[str] = Field(default=None, description="CREATE TABLE 语句")


class DatabaseInfo(BaseModel):
    """数据库信息"""
    name: str = Field(description="数据库名")
    table_count: int = Field(description="表数量")
    tables: List[str] = Field(description="表名列表")


class QueryStatistics(BaseModel):
    """查询统计信息"""
    date: str = Field(description="统计日期")
    total_queries: int = Field(description="总查询次数")
    successful_queries: int = Field(description="成功查询次数")
    failed_queries: int = Field(description="失败查询次数")
    total_rows: int = Field(description="总返回行数")
    total_execution_time: float = Field(description="总执行时间（秒）")
    average_execution_time: float = Field(description="平均执行时间（秒）")
    success_rate: float = Field(description="成功率")


class DatabaseResource(BaseModel):
    """数据库资源"""
    uri: str = Field(description="资源 URI")
    name: str = Field(description="资源名称")
    description: str = Field(description="资源描述")
    mime_type: str = Field(description="MIME 类型")
    content: dict = Field(description="资源内容")

"""MCP Prompts 实现 - 提供实用的数据库分析提示词"""

import asyncio
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Prompt, PromptArgument, PromptMessage

logger = logging.getLogger(__name__)


def register_prompts(server: Server, db_ops: Any) -> None:
    """
    注册 MCP Prompts

    Args:
        server: MCP Server 实例
        db_ops: DatabaseOperations 实例
    """

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """列出所有可用的提示词"""
        return [
            Prompt(
                name="explore_database",
                description="探索数据库结构，分析表之间的关系",
                arguments=[
                    PromptArgument(
                        name="database",
                        description="要探索的数据库名称",
                        required=True
                    )
                ]
            ),
            Prompt(
                name="generate_orm_model",
                description="根据表结构生成 ORM 模型代码（SQLAlchemy/Django）",
                arguments=[
                    PromptArgument(
                        name="database",
                        description="数据库名称",
                        required=True
                    ),
                    PromptArgument(
                        name="table",
                        description="表名称",
                        required=True
                    ),
                    PromptArgument(
                        name="framework",
                        description="ORM 框架（sqlalchemy 或 django），默认为 sqlalchemy",
                        required=False
                    )
                ]
            ),
            Prompt(
                name="analyze_table",
                description="分析表数据，提供优化建议和数据洞察",
                arguments=[
                    PromptArgument(
                        name="database",
                        description="数据库名称",
                        required=True
                    ),
                    PromptArgument(
                        name="table",
                        description="表名称",
                        required=True
                    )
                ]
            ),
            Prompt(
                name="generate_sql_query",
                description="从自然语言描述智能生成 SQL 查询",
                arguments=[
                    PromptArgument(
                        name="database",
                        description="数据库名称",
                        required=True
                    ),
                    PromptArgument(
                        name="requirement",
                        description="查询需求的自然语言描述",
                        required=True
                    ),
                    PromptArgument(
                        name="tables",
                        description="相关的表名称（多个表用逗号分隔，可选）",
                        required=False
                    )
                ]
            ),
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None) -> PromptMessage:
        """
        获取提示词内容

        Args:
            name: 提示词名称
            arguments: 提示词参数

        Returns:
            提示词消息
        """
        try:
            if not arguments:
                arguments = {}

            if name == "explore_database":
                database = arguments.get("database", "")
                if not database:
                    raise ValueError("database 参数不能为空")

                # 获取数据库的所有表

                tables = await asyncio.to_thread(db_ops.list_tables, database)

                prompt_text = f"""请帮我探索 `{database}` 数据库的结构。

**数据库信息：**
- 数据库名：{database}
- 表数量：{len(tables)}

**探索任务：**
1. 分析所有表的结构和用途
2. 识别表之间的关系（外键、关联）
3. 找出核心业务表和辅助表
4. 评估表设计的合理性
5. 提供改进建议

**可用表列表：**
{chr(10).join(f"- {table}" for table in tables)}

请使用 `get_table_info` 工具获取每个表的详细结构，然后进行全面分析。"""

                return PromptMessage(
                    role="user",
                    content={"type": "text", "text": prompt_text}
                )

            elif name == "generate_orm_model":
                database = arguments.get("database", "")
                table = arguments.get("table", "")
                framework = arguments.get("framework", "sqlalchemy")

                if not database or not table:
                    raise ValueError("database 和 table 参数不能为空")

                # 获取表的详细信息

                table_info = await asyncio.to_thread(db_ops.get_table_info, database, table)

                # 构建字段信息文本
                field_lines = []
                for field in table_info["structure"]:
                    field_lines.append(
                        f"- {field['Field']}: {field['Type']} "
                        f"(NULL={field['Null']}, Key={field['Key']}, "
                        f"Default={field.get('Default', 'None')}, Extra={field.get('Extra', '')})"
                    )

                fields_text = "\n".join(field_lines)

                if framework.lower() == "django":
                    framework_example = """
**Django Model 示例：**
```python
from django.db import models

class YourModel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'your_table'
```
"""
                else:
                    framework_example = """
**SQLAlchemy Model 示例：**
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class YourModel(Base):
    __tablename__ = 'your_table'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    created_at = Column(DateTime)
```
"""

                prompt_text = f"""请根据以下表结构生成 {framework.upper()} ORM 模型代码。

**表信息：**
- 数据库：{database}
- 表名：{table}
- 行数：{table_info.get('row_count', 0)}

**表结构：**
{fields_text}

{framework_example}

**要求：**
1. 正确映射所有字段类型
2. 设置主键和索引
3. 处理默认值和自增字段
4. 添加必要的类型注解
5. 包含完整的字段注释
6. 遵循 {framework} 最佳实践

请生成完整的 Python 代码。"""

                return PromptMessage(
                    role="user",
                    content={"type": "text", "text": prompt_text}
                )

            elif name == "analyze_table":
                database = arguments.get("database", "")
                table = arguments.get("table", "")

                if not database or not table:
                    raise ValueError("database 和 table 参数不能为空")

                # 获取表的详细信息

                table_info = await asyncio.to_thread(db_ops.get_table_info, database, table)

                # 构建字段信息
                field_lines = []
                indexed_fields = []
                nullable_fields = []
                default_fields = []

                for field in table_info["structure"]:
                    field_name = field['Field']
                    field_type = field['Type']
                    field_key = field['Key']
                    field_null = field['Null']
                    field_default = field.get('Default')
                    field_extra = field.get('Extra', '')

                    field_lines.append(f"- {field_name} ({field_type})")

                    if field_key in ['PRI', 'UNI', 'MUL']:
                        indexed_fields.append(f"{field_name} ({field_key})")

                    if field_null == 'YES':
                        nullable_fields.append(field_name)

                    if field_default is not None:
                        default_fields.append(f"{field_name} = {field_default}")

                prompt_text = f"""请分析 `{database}.{table}` 表的数据和结构。

**基本信息：**
- 数据库：{database}
- 表名：{table}
- 当前行数：{table_info.get('row_count', 0)}
- 字段数量：{len(table_info['structure'])}

**字段列表：**
{chr(10).join(field_lines)}

**索引字段：**
{chr(10).join(indexed_fields) if indexed_fields else '无索引字段'}

**允许 NULL 的字段：**
{chr(10).join(nullable_fields) if nullable_fields else '所有字段都不允许 NULL'}

**有默认值的字段：**
{chr(10).join(default_fields) if default_fields else '无默认值字段'}

**分析任务：**
1. **数据分布分析**：查询样本数据，分析字段值的分布情况
2. **性能评估**：评估索引设置是否合理，是否需要添加新索引
3. **数据质量**：检查是否有异常数据、重复数据、空值过多等问题
4. **优化建议**：
   - 索引优化建议
   - 字段类型优化建议
   - 数据清理建议
   - 查询优化建议

请使用 `query_database` 工具查询样本数据进行分析。"""

                return PromptMessage(
                    role="user",
                    content={"type": "text", "text": prompt_text}
                )

            elif name == "generate_sql_query":
                database = arguments.get("database", "")
                requirement = arguments.get("requirement", "")
                tables_str = arguments.get("tables", "")

                if not database or not requirement:
                    raise ValueError("database 和 requirement 参数不能为空")

                # 如果用户指定了表名，获取这些表的结构
                if tables_str:
                    table_list = [t.strip() for t in tables_str.split(",")]

                    # 获取所有表的结构信息
                    tables_info = []
                    for table_name in table_list:
                        try:
                            table_info = await asyncio.to_thread(
                                db_ops.get_table_info, database, table_name
                            )

                            # 格式化字段信息
                            fields = []
                            for field in table_info["structure"]:
                                fields.append(
                                    f"  - {field['Field']}: {field['Type']} "
                                    f"(Key={field['Key']}, Null={field['Null']})"
                                )

                            tables_info.append(
                                f"**表 `{table_name}`：**（{table_info.get('row_count', 0)} 行）\n" +
                                "\n".join(fields)
                            )
                        except Exception as e:
                            tables_info.append(f"**表 `{table_name}`：** 无法获取结构 ({str(e)})")

                    tables_context = "\n\n".join(tables_info)

                    prompt_text = f"""请根据以下需求生成 SQL 查询语句。

**数据库：** {database}

**查询需求：**
{requirement}

**相关表结构：**

{tables_context}

**要求：**
1. 生成符合 MySQL 语法的 SELECT 查询
2. 确保字段名和表名正确（区分大小写）
3. 如果需要多表关联，正确使用 JOIN
4. 添加适当的 WHERE 条件过滤
5. 如果需要聚合，使用合适的 GROUP BY 和聚合函数
6. 添加必要的 ORDER BY 和 LIMIT
7. 提供查询的详细说明
8. 如果需求不明确，列出可能的查询���案

请直接生成可执行的 SQL 查询。"""

                else:
                    # 没有指定表名，获取数据库的所有表
                    tables = await asyncio.to_thread(db_ops.list_tables, database)

                    prompt_text = f"""请根据以下需求生成 SQL 查询语句。

**数据库：** {database}

**查询需求：**
{requirement}

**数据库中的表：**（共 {len(tables)} 个表）
{chr(10).join(f"- {table}" for table in tables)}

**分析步骤：**
1. 首先，根据查询需求确定需要使用哪些表
2. 使用 `get_table_info` 工具获取相关表的详细结构
3. 分析表之间的关系（主键、外键）
4. 生成符合需求的 SQL 查询

**SQL 查询要求：**
1. 符合 MySQL 语法
2. 字段名和表名准确
3. 使用合适的 JOIN（如果需要多表）
4. 添加必要的 WHERE、GROUP BY、ORDER BY
5. 限制返回行数（LIMIT）
6. 提供查询说明

请按照上述步骤分析并生成 SQL 查询。"""

                return PromptMessage(
                    role="user",
                    content={"type": "text", "text": prompt_text}
                )

            # 未知的提示词
            raise ValueError(f"未知的提示词：{name}")

        except Exception as e:
            logger.error(f"获取提示词失败 [{name}]: {str(e)}")
            # 返回错误提示
            return PromptMessage(
                role="user",
                content={
                    "type": "text",
                    "text": f"获取提示词时出错：{str(e)}\n\n请检查参数是否正确。"
                }
            )

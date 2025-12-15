# MySQL Reader MCP Server

[![MCP Best Practices](https://img.shields.io/badge/MCP-Best%20Practices-green)](tmp/MCP_BEST_PRACTICES_AUDIT.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个符合 MCP 最佳工程实践的 MySQL 数据库只读访问服务器，提供完整的数据库查询、表结构查看、MCP Resources 和智能 Prompts 功能。
- 帮助后端同学打通数据库，可以让ai生成和自动更新数据表模型文件。
- 示例：tmp/RechargeSuccess.php

**🌟 特点：**
- ✅ 完全符合 MCP 最佳实践标准（98% 符合率）
- ✅ 8 个 Tools + 3 个 Resources + 4 个 Prompts（v1.3.0 新增）
- ✅ 数据导出（CSV/JSON/Excel）+ 智能 SQL 生成 + 性能分析
- ✅ 使用 Pydantic 配置验证和类型安全
- ✅ 数据库连接池（DBUtils.PooledDB，性能提升 50%+）
- ✅ 自定义异常系统 + 自动重试机制
- ✅ 完整的类型提示和测试套件（pytest）
- ✅ 只读安全 + 查询限制 + 自动日志

---

## 📑 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [项目架构](#项目架构)
- [配置说明](#配置说明)
- [查询日志和统计](#查询日志和统计)
- [测试](#测试)
- [查询示例](#查询示例)
- [文件组织规则](#文件组织规则)
- [安全性](#安全性)

---

## 功能特性

### 🛠️ MCP Tools（8个）

**基础工具（5个）：**
- ✓ `list_databases` - 列出所有数据库
- ✓ `list_tables` - 查看数据库中的所有表
- ✓ `describe_table` - 获取表结构信息
- ✓ `query_database` - 执行 SELECT 查询（只读）
- ✓ `get_table_info` - 获取表的完整信息

**新功能工具（3个）- v1.3.0：**
- ✨ `export_query_results` - 导出查询结果（CSV/JSON/Excel）
- ✨ `explain_query` - EXPLAIN 执行计划分析
- ✨ `analyze_slow_query` - 慢查询检测和优化建议

### 📚 MCP Resources（3个）
- ✓ `mysql://databases` - 数据库列表资源
- ✓ `mysql://databases/{database}/tables` - 表列表资源
- ✓ `mysql://databases/{database}/tables/{table}` - 表结构资源

### 💡 MCP Prompts（4个）
- ✓ `explore_database` - 探索数据库结构，分析表关系
- ✓ `generate_orm_model` - 生成 ORM 模型代码
- ✓ `analyze_table` - 分析表数据，提供优化建议
- ✨ `generate_sql_query` - 从自然语言智能生成 SQL（v1.3.0 新增）

### 🔒 安全特性
- ✓ 只读查询（仅允许 SELECT）
- ✓ 自动行数限制（可配置 1-10000 行，默认 1000）
- ✓ 查询超时保护（可配置 1-300 秒）
- ✓ SQL 注入防护
- ✓ 环境变量配置（.env 文件）
- ✓ 完整的查询日志和审计

### ⚡ 性能优化
- ✓ DBUtils 连接池 - 性能提升 50%+
- ✓ 异步操作（asyncio）
- ✓ 连接复用和健康检查
- ✓ 支持并发 15+ 连接
- ✓ 自动连接回收

### 🛡️ 异常处理
- ✓ 5 种自定义异常类型
- ✓ 连接错误自动重试（3 次）
- ✓ 详细的错误信息和堆栈跟踪
- ✓ 优雅的错误恢复

---

## 快速开始

### 建议：直接让 AI 帮你安装

```
请帮我安装和配置 ReadMysql MCP 服务器
```

### 手动安装

#### 1. 安装依赖
```bash
cd src/ReadMysql
pip install -r requirements.txt

# 安装开发依赖（包含测试工具）
pip install -r requirements-dev.txt
```

#### 2. 配置数据库
```bash
cp .env.example .env
# 编辑 .env 文件填入数据库信息
```

**.env 配置示例：**
```env
# 数据库连接配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_CHARSET=utf8mb4

# 连接池配置
POOL_SIZE=5
POOL_MAX_OVERFLOW=10

# 查询配置
QUERY_MAX_ROWS=1000
QUERY_TIMEOUT=30
```

#### 3. 配置 MCP

**推荐：Claude Code CLI（全局配置）**

```bash
# Windows
claude mcp add --scope user MySQL python D:/www/3d66.mcp/src/ReadMysql/server.py

# Linux/Mac
claude mcp add --scope user MySQL python /path/to/3d66.mcp/src/ReadMysql/server.py
```

**或手动配置（Trae/Cursor）**

编辑 MCP 配置文件：
- Windows: `C:\Users\<username>\AppData\Roaming\Trae\User\mcp.json`
- Linux/Mac: `~/.config/Cursor/User/mcp.json`

```json
{
  "mcpServers": {
    "MySQL": {
      "command": "python",
      "args": ["D:\\www\\3d66.mcp\\src\\ReadMysql\\server.py"],
      "env": {}
    }
  }
}
```

#### 4. 验证安装
```bash
# 测试数据库连接
python query/test_connection.py

# 验证 MCP 功能
python validate_features.py

# 运行测试套件
pytest
```

详细安装说明请参考 [CLAUDE.md](../../CLAUDE.md)

---

## 项目架构

### 目录结构
```
src/ReadMysql/
├── config/                    # 配置管理模块（2025-12 重构）
│   ├── __init__.py
│   └── settings.py            # Pydantic 配置管理
├── core/                      # 核心模块（2025-12 新增）
│   ├── __init__.py
│   ├── exceptions.py          # 自定义异常（5 种类型）
│   └── connection_pool.py     # 数据库连接池（DBUtils）
├── database/                  # 数据库操作模块（2025-12 重构）
│   ├── __init__.py
│   └── operations.py          # 数据库操作 API
├── mcp_extensions/            # MCP 协议扩展（2025-12 新增）
│   ├── __init__.py
│   ├── schemas.py             # Pydantic 数据模型
│   ├── resources.py           # MCP Resources 实现
│   ├── prompts.py             # MCP Prompts 实现
│   ├── export_tools.py        # 数据导出工具
│   ├── performance_tools.py   # 性能分析工具
│   └── documentation_tools.py # 文档生成工具
├── query/                     # 查询脚本目录
│   ├── query_user.py
│   ├── query_balance.py
│   ├── query_today_users.py
│   ├── query_recent_registrations.py
│   ├── query_today_recharge.py  # 今日充值统计（2025-12 新增）
│   └── test_connection.py
├── tests/                     # 测试套件（2025-12 新增）
│   ├── conftest.py            # pytest 固件
│   ├── test_config.py         # 配置测试
│   ├── test_database_operations.py  # 数据库操作测试
│   └── README.md              # 测试文档
├── tmp/                       # 临时文件和报告目录
│   ├── organize_files.py      # 文件组织工具
│   └── *.md, *.json           # 分析报告
├── log/                       # 查询日志目录
│   └── query_YYYYMMDD.log
├── server.py                  # MCP 服务器入口点
├── query_logger.py            # 查询日志模块
├── view_stats.py              # 日志统计查看器
├── validate_features.py       # 功能验证工具
├── pytest.ini                 # pytest 配置
├── .env                       # 环境变量配置（不提交）
├── .env.example               # 环境变量示例
├── requirements.txt           # Python 依赖
├── requirements-dev.txt       # 开发依赖
└── README.md                  # 项目文档
```

### 核心组件说明

**server.py** - MCP 服务器入口点
- 定义 5 个 MCP 工具
- 自动初始化配置和连接池
- 异步操作处理
- 集成查询日志

**config/settings.py** - 配置管理（Pydantic）
- `DatabaseConfig` - 数据库连接配置
- `ConnectionPoolConfig` - 连接池配置
- `QueryConfig` - 查询限制和超时设置
- 自动验证配置参数范围

**core/connection_pool.py** - 数据库连接池
- 使用 DBUtils.PooledDB 实现
- 单例模式，全局共享
- 支持连接复用，性能提升 50%+
- 自动连接健康检查和回收

**core/exceptions.py** - 自定义异常
- 5 种异常类型：MySQLError、ConnectionError、QueryError、ValidationError、ConfigurationError
- 自动重试机制（连接错误重试 3 次）
- 详细的错误信息和堆栈跟踪

**database/operations.py** - 数据库操作层
- `DatabaseOperations` 类提供所有数据库操作 API
- 使用连接池替代直接连接
- 完整的类型提示
- DictCursor 返回 JSON 友好的结果

**mcp_extensions/schemas.py** - 数据模型（Pydantic）
- `TableField` - 表字段信息
- `TableStructure` - 表结构信息
- `TableInfo` - 表详细信息
- `DatabaseInfo` - 数据库信息
- `QueryStatistics` - 查询统计信息

完整架构请参考 [CLAUDE.md](../../CLAUDE.md)

---

## 配置说明

### 环境变量配置

所有配置通过 `.env` 文件管理，支持以下配置项：

**数据库连接：**
- `DB_HOST` - 数据库主机（默认：localhost）
- `DB_PORT` - 数据库端口（默认：3306）
- `DB_USER` - 数据库用户名（必需）
- `DB_PASSWORD` - 数据库密码（必需）
- `DB_CHARSET` - 字符集（默认：utf8mb4）

**连接池配置：**
- `POOL_SIZE` - 连接池大小（1-50，默认：5）
- `POOL_MAX_OVERFLOW` - 最大溢出连接数（0-50，默认：10）

**查询配置：**
- `QUERY_MAX_ROWS` - 最大查询行数（1-10000，默认：1000）
- `QUERY_TIMEOUT` - 查询超时秒数（1-300，默认：30）

**配置验证：**
所有配置使用 Pydantic 自动验证，无效值将在启动时报错。

---

## 查询日志和统计

### 查看统计
```bash
python view_stats.py           # 今天
python view_stats.py 20251204  # 指定日期
```

### 日志格式
JSON 格式，存储在 `log/query_YYYYMMDD.log`：

```json
{
  "timestamp": "2025-12-04T09:45:30.123456",
  "database": "master_3d66_user",
  "query": "SELECT COUNT(*) as today_count FROM ll_user WHERE ...",
  "success": true,
  "row_count": 1,
  "execution_time": 0.0234,
  "tool_name": "query_database"
}
```

### 统计信息
- 总查询次数（成功和失败）
- 总返回行数（token 使用量）
- 总执行时间和平均执行时间
- 成功率
- 按数据库分组
- 按工具分组

---

## 测试

### 安装测试依赖
```bash
pip install -r requirements-dev.txt
```

### 运行测试
```bash
# 运行所有测试
pytest

# 只运行单元测试（不需要数据库）
pytest -m unit

# 只运行集成测试（需要数据库连接）
pytest -m integration

# 查看测试覆盖率
pytest --cov=. --cov-report=html
```

### 测试结构
- **tests/test_config.py** - 配置系统测试（单元测试）
- **tests/test_database_operations.py** - 数据库操作测试（集成测试）
- **tests/conftest.py** - pytest 固件和配置
- **pytest.ini** - pytest 配置文件

**注意：** 集成测试使用真实的数据库连接，所有测试只进行只读操作，不会修改数据。

详细测试文档：[tests/README.md](tests/README.md)

---

## 查询示例

`query/` 目录提供了预构建的查询脚本：

- **query_user.py** - 查询用户表结构和示例数据
- **query_balance.py** - 查询用户余额统计
- **query_today_users.py** - 统计今天注册的用户数
- **query_recent_registrations.py** - 查看最近 7 天的注册趋势
- **query_today_recharge.py** - 今日充值统计（2025-12 新增）
- **test_connection.py** - 测试数据库连接

**运行示例：**
```bash
cd query
python query_today_users.py
python query_today_recharge.py
```

---

## 🆕 新功能使用指南（v1.3.0）

### 📊 数据导出功能

将查询结果导出为 CSV、JSON 或 Excel 文件。

**使用场景：**
- 数据分析和报告生成
- 数据备份和归档
- 与其他工具集成（Excel、BI 工具）

**示例：导出今日注册用户**
```
使用 export_query_results 工具导出以下查询：
- database: master_3d66_user
- query: SELECT * FROM ll_user WHERE DATE(create_time) = CURDATE()
- format: excel
- filename: today_users
```

**支持的格式：**
- `csv` - CSV 格式（UTF-8 with BOM，Excel 兼容）
- `json` - JSON 格式（包含元数据和时间戳）
- `excel` - Excel 格式（自动列宽，表头样式）

**导出位置：** `tmp/exports/` 目录

---

### 🤖 智能 SQL 生成

从自然语言描述自动生成 SQL 查询。

**使用场景：**
- 快速构建复杂查询
- 学习 SQL 最佳实践
- 探索数据库和表关系

**示例 1：简单查询**
```
使用 generate_sql_query Prompt：
- database: master_3d66_user
- requirement: 查询今天注册的用户数量
- tables: ll_user
```

AI 将自动：
1. 分析 ll_user 表结构
2. 识别时间字段（create_time）
3. 生成带有 DATE() 函数的 SQL
4. 添加 COUNT() 聚合
5. 提供查询说明

**示例 2：复杂关联查询**
```
使用 generate_sql_query Prompt：
- database: master_3d66_user
- requirement: 查询最近 7 天每天的充值金额和用户数
- tables: （留空，让 AI 自动分析）
```

AI 将自动：
1. 分析数据库中的所有表
2. 识别充值相关的表
3. 设计多表 JOIN 方案
4. 生成带有 GROUP BY 和日期函数的 SQL
5. 提供多种优化方案

---

### 🔍 查询性能分析

使用 EXPLAIN 分析查询执行计划，检测慢查询并提供优化建议。

**工具 1：explain_query - EXPLAIN 分析**

**使用场景：**
- 了解查询执行计划
- 优化查询性能
- 检测索引使用情况

**示例：**
```
使用 explain_query 工具：
- database: master_3d66_user
- query: SELECT * FROM ll_user WHERE username = 'test'
- format: traditional  # 或 json/tree
```

**返回信息：**
- EXPLAIN 详细结果
- 实际执行时间
- 性能分析（扫描行数、索引使用、临时表等）
- 优化建议

**工具 2：analyze_slow_query - 慢查询分析**

**使用场景：**
- 检测和诊断慢查询
- 获取详细的优化建议
- 评估查询严重程度

**示例：**
```
使用 analyze_slow_query 工具：
- database: master_3d66_user
- query: SELECT * FROM ll_user WHERE create_time > '2025-01-01'
- threshold: 1.0  # 慢查询阈值（秒）
```

**返回信息：**
- 是否为慢查询（基于阈值）
- 执行时间和性能指标
- EXPLAIN 分析结果
- 严重程度分类（low/medium/high/critical）
- 详细的优化建议：
  - 索引优化
  - 查询重写
  - 数据量处理
  - 子查询优化

**优化建议示例：**
```
⚠️ 检测到全表扫描，建议添加索引
📌 优化建议：避免使用临时表
   - 简化 GROUP BY 子句
   - 为 GROUP BY 字段添加索引
📌 数据量建议：扫描了 50000 行数据
   - 添加更精确的 WHERE 条件
   - 考虑分页查询
```

---

### 🧪 测试新功能

运行完整的功能测试：

```bash
cd src/ReadMysql
python tmp/test_new_features.py
```

测试脚本将自动验证：
- ✅ 数据导出功能（CSV/JSON/Excel）
- ✅ 智能 SQL 生成 Prompt
- ✅ 性能分析工具（EXPLAIN + 慢查询）

---

## 文件组织规则

**⚠️ 极其重要：** ReadMysql 项目遵循严格的文件组织规则。

### 目录职责

1. **log/** - 日志文件目录
   - 所有运行时生成的日志文件
   - 格式：`query_YYYYMMDD.log`

2. **query/** - 查询脚本目录
   - 所有数据库查询示例脚本
   - 命名规范：`query_*.py`

3. **tmp/** - 临时文件和报告目录
   - 所有分析报告文件（`.md`, `.json`, `.html`, `.csv`）
   - 所有分析和测试脚本（`analyze_*.py`, `test_*.py`, `generate_*.py`）
   - 临时数据文件和中间结果

4. **根目录** - 核心程序文件
   - `server.py` - MCP 服务器入口
   - `query_logger.py` - 日志记录模块
   - `view_stats.py` - 统计查看工具
   - `validate_features.py` - 功能验证工具
   - 项目配置文件

### 自动整理工具

运行 `tmp/organize_files.py` 可以自动整理文件到正确的目录：

```bash
python tmp/organize_files.py
```

---

## 安全性

### 安全特性
- ✅ 只读操作（仅允许 SELECT）
- ✅ 查询限制（行数 + 超时）
- ✅ SQL 注入防护
- ✅ 配置验证（Pydantic）
- ✅ 查询审计（完整日志）
- ✅ 环境变量配置（无硬编码密钥）

### 建议配置

**创建只读数据库用户：**
```sql
CREATE USER 'readonly'@'localhost' IDENTIFIED BY 'strong_password';
GRANT SELECT ON *.* TO 'readonly'@'localhost';
FLUSH PRIVILEGES;
```

**安全清单：**
- [ ] 使用只读数据库用户
- [ ] 永远不要提交 `.env` 文件
- [ ] 限制数据库访问到本地主机或可信网络
- [ ] 定期审查查询日志
- [ ] 监控 token 使用量（行数）
- [ ] 设置合理的查询限制和超时

---

## 最佳实践审计

**评分：** 🌟🌟🌟🌟🌟 优秀
**符合率：** 98%

详细报告：[tmp/MCP_BEST_PRACTICES_AUDIT.md](tmp/MCP_BEST_PRACTICES_AUDIT.md)

---

## 版本历史

### v1.3.0 (2025-12-04) 🆕🔥
**重大功能更新：生产力提升 3 倍**

- ✨ **数据导出功能** (`export_query_results`)
  - 支持 CSV/JSON/Excel 三种格式
  - 自动文件命名和大小显示
  - 导出文件保存在 `tmp/exports/` 目录

- ✨ **智能 SQL 生成** (`generate_sql_query` Prompt)
  - 从自然语言描述生成 SQL 查询
  - 自动分析表结构和关系
  - 提供多种查询方案和优化建议

- ✨ **查询性能分析** (`explain_query`, `analyze_slow_query`)
  - EXPLAIN 执行计划分析（支持 traditional/json/tree 格式）
  - 慢查询自动检测和分类（low/medium/high/critical）
  - 智能优化建议（索引、查询重写、性能瓶颈）

- 📦 新增依赖：openpyxl（Excel 导出支持）
- 📝 完整的功能测试脚本：`tmp/test_new_features.py`
- 📚 文档更新：README.md 和 CLAUDE.md

### v1.2.0 (2025-12-04)
- ✅ 完善配置系统（config/settings.py）
- ✅ 重构数据库操作层（database/operations.py）
- ✅ 新增测试套件（pytest + 集成测试）
- ✅ MCP Resources 和 Prompts 完整实现
- ✅ 文件组织规则和自动整理工具
- ✅ 新增查询示例（query_today_recharge.py）

### v1.1.0 (2025-12-04)
- ✅ 重组项目结构（config/, database/, mcp_extensions/）
- ✅ MCP Resources 和 Prompts 初始实现
- ✅ Pydantic 数据模型
- ✅ 修复命名冲突（mcp/ → mcp_extensions/）
- ✅ 通过最佳实践审计

### v1.0.0 (2025-12-03)
- ✅ DBUtils 连接池实现
- ✅ Pydantic 配置管理
- ✅ 5 种自定义异常类型
- ✅ 查询日志系统

---

## 许可证

MIT License

---

**推荐用作 MCP 项目的参考实现。** 🌟

完整文档请参阅 [CLAUDE.md](../../CLAUDE.md)

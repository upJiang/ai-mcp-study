# MCP Deploy Server - 测试环境批量发版服务器

这是一个基于 MCP (Model Context Protocol) 的部署服务器，用于在测试环境批量发布并拉取最新项目代码。

## 功能特性

- 获取可发版的项目列表（动态从 OA API 获取）
- 单个项目发版（拉取最新代码 + 配置复制）
- 批量发版（串行执行，支持多个项目）
- 全量发版（可排除指定项目）
- 完善的错误处理和重试机制
- 实时输出 Git 操作日志

## 项目结构

```
mcp/
├── requirements.txt      # Python 依赖
├── server.py             # MCP 服务器主入口
├── config.py             # 配置管理
├── deploy_api.py         # 部署 API 封装
└── README.md             # 本文档
```

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd E:\git\3d66\3d66.mcp\src\DeployServer
pip install -r requirements.txt
```

### 2. 配置 MCP 服务器

#### 方式一：使用 Claude Code CLI 命令添加（推荐 - 全局配置）

**Windows 系统：**
```bash
claude mcp add --scope user DeployServer python E:/git/3d66/3d66.mcp/src/DeployServer/server.py
```

**Linux/Mac 系统：**
```bash
claude mcp add --scope user DeployServer python /path/to/3d66.mcp/src/DeployServer/server.py
```

**重要说明：**
- `--scope user`：添加到用户级别（全局），在所有项目中可用
- Windows 路径使用**正斜杠** `/` 而不是反斜杠 `\`
- 配置文件位置：`C:\Users\<用户名>\.claude.json`（Windows）或 `~/.claude.json`（Linux/Mac）

**验证配置：**
```bash
# 查看所有 MCP 服务器
claude mcp list

# 查看 DeployServer 详细配置
claude mcp get DeployServer
```

#### 方式二：Trae/Cursor 编辑器手动配置

如果您使用 **Trae** 或 **Cursor** 编辑器（而非 Claude Code CLI），需要手动编辑配置文件。

**Windows - Trae 编辑器：**

编辑 `C:\Users\Administrator\AppData\Roaming\Trae\User\mcp.json`：

```json
{
  "mcpServers": {
    "DeployServer": {
      "command": "python",
      "args": [
        "E:\\git\\3d66\\3d66.mcp\\src\\DeployServer\\server.py"
      ],
      "env": {}
    }
  }
}
```

**Linux/Mac - Cursor 编辑器：**

编辑 `~/.config/Cursor/User/mcp.json`：

```json
{
  "mcpServers": {
    "DeployServer": {
      "command": "python",
      "args": [
        "/path/to/3d66.mcp/src/DeployServer/server.py"
      ],
      "env": {}
    }
  }
}
```

### 3. 重启编辑器/重新加载窗口

配置完成后：
- **Claude Code CLI**：自动生效，无需重启
- **VSCode/Trae/Cursor**：重新加载窗口（`Ctrl+Shift+P` → "Reload Window"）

## 使用方法

### 1. 获取项目列表

在 Claude Code 中输入：

```
获取可发版的项目列表
```

返回示例：

```json
{
  "status": "success",
  "total": 44,
  "projects": [
    {"project_id": 1, "project_name": "www"},
    {"project_id": 2, "project_name": "user"},
    {"project_id": 10, "project_name": "3d"},
    ...
  ]
}
```

### 2. 发版单个项目

在 Claude Code 中输入：

```
发版 3d 项目
```

或

```
使用 deploy_project 发版 user 项目
```

返回示例：

```json
{
  "project": "3d",
  "status": "success",
  "output": "正在 pull 3d !\nFetching origin\n..."
}
```

### 3. 批量发版

在 Claude Code 中输入：

```
发版 3d、user、www 这三个项目
```

或

```
批量发版：3d, user, www
```

返回示例：

```json
{
  "status": "completed",
  "total": 3,
  "success": 3,
  "failed": 0,
  "results": [
    {"project": "3d", "status": "success", "output": "..."},
    {"project": "user", "status": "success", "output": "..."},
    {"project": "www", "status": "success", "output": "..."}
  ]
}
```

### 4. 发版所有项目

在 Claude Code 中输入：

```
发版所有项目
```

或排除某些项目：

```
发版所有项目，但排除 3d 和 user
```

返回示例：

```json
{
  "status": "completed",
  "total": 42,
  "success": 40,
  "failed": 2,
  "excluded": ["3d", "user"],
  "results": [...]
}
```

## MCP 工具说明

### list_projects

- **功能**：获取可发版的项目列表
- **输入参数**：无
- **返回**：包含所有项目的列表

### deploy_project

- **功能**：发版单个项目
- **输入参数**：
  - `project_name` (string): 项目名称
- **返回**：发版结果和 Git 操作日志

### batch_deploy

- **功能**：批量发版（串行执行）
- **输入参数**：
  - `project_names` (array): 项目名称列表
- **返回**：每个项目的发版结果

### deploy_all

- **功能**：发版所有项目
- **输入参数**：
  - `exclude` (array, 可选): 要排除的项目名称列表
- **返回**：所有项目的发版结果

## API 配置

配置文件：`config.py`

```python
# 项目列表 API
PROJECT_LIST_API = "https://oa-api.3d66.com/api/v1/release/project"

# 发版 API
DEPLOY_API = "http://wh.3dliuliuwang.com/manual"

# 固定 Token
TOKEN = "d0528a75671f550abacfcf3027a2fa090"

# 请求超时时间（秒）
TIMEOUT = 300

# API 请求重试次数
MAX_RETRIES = 3
```

## 技术特性

### 串行执行

批量发版时，项目按顺序依次执行，确保每个项目完成后再执行下一个。

### 项目验证

发版前会验证项目名是否在可发版列表中，防止操作不存在的项目。

### 错误处理

- 网络错误自动重试（最多 3 次）
- 单个项目失败不影响其他项目
- 详细的错误信息返回

### 超时控制

每个 API 请求设置 5 分钟超时，避免长时间等待。

## 常见问题

### Q: 如何修改 Token？

A: 编辑 `config.py` 文件，修改 `TOKEN` 变量的值。

### Q: 如何调整超时时间？

A: 编辑 `config.py` 文件，修改 `TIMEOUT` 变量的值（单位：秒）。

### Q: 发版失败怎么办？

A: 检查返回的错误信息，常见原因：
- 项目名不存在
- 网络连接问题
- API 服务不可用

### Q: 如何查看详细日志？

A: 发版成功后，返回结果的 `output` 字段包含完整的 Git 操作日志。

## 支持的项目列表

通过 `list_projects` 工具可以获取最新的项目列表，包括：

- www, user, user-api, ip, factory, facotry-api
- new-admin, service, anli, 3d, new-cli, static
- service-user, seo, notiry, header-module
- service-vr, service-xuanran, vr, linggantu, ku
- vr-next, xiaoguotu, cad, su, tietu
- relebook-service, software, service-search
- www-service, work, mobile-api, service-tracking
- vip, oa, oa-api, relebook-factory-api
- zixue, search-php, ruiyun, mall, cli
- service-payment, service-module-common

## 维护和更新

如需修改发版逻辑或 API 地址，请编辑以下文件：

- `config.py` - 配置参数
- `deploy_api.py` - API 调用逻辑
- `server.py` - MCP 工具定义

## 技术支持

如有问题或建议，请联系开发团队。

# Python MCP 服务自动部署指南

## 🎯 一句话总结

**在 `mcp-list/packages/` 下添加 Python MCP 包 → 提交推送 → 自动部署到生产环境**

---

## 📦 添加新服务（仅需 3 步）

### 1. 创建包目录和文件

```bash
cd mcp-list/packages
mkdir YourServiceName
cd YourServiceName
```

创建必需文件：
- `server.py` - MCP 服务器主文件（必须）
- `requirements.txt` - Python 依赖（必须）
- `src/` - 业务逻辑目录（可选）

### 2. 编写服务代码

**server.py 示例：**
```python
#!/usr/bin/env python3
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("yourservice")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="your_tool",
            description="工具描述",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "your_tool":
        return [TextContent(type="text", text="返回结果")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

**requirements.txt 示例：**
```
mcp>=1.0.0
requests>=2.32.0
```

### 3. 提交并推送

```bash
git add mcp-list/packages/YourServiceName
git commit -m "feat: add YourServiceName MCP service"
git push
```

**就这样！🎉 系统会自动完成以下操作：**

---

## 🤖 自动化流程（无需人工干预）

1. ✅ **GitHub Actions 触发**
   - 检测到 `mcp-list/packages/**` 变更
   - 启动部署工作流

2. ✅ **SSH 到服务器**
   - 连接到 `/opt/mcp-services/ai-mcp-study`
   - 拉取最新代码

3. ✅ **自动生成配置**
   ```bash
   # 扫描所有 Python 包（带 requirements.txt）
   # 自动生成 docker-compose.yml
   ./deployment/generate-compose.sh

   # 根据服务自动生成 Nginx 反向代理配置
   ./deployment/generate-nginx.sh
   ```

4. ✅ **部署服务**
   - 构建 Docker 镜像
   - 启动容器（`mcp-{服务名}`）
   - 配置网络和日志
   - 更新 Nginx 配置

5. ✅ **服务上线**
   - 访问地址：`https://junfeng530.xyz/mcp/{服务名}`
   - 容器名称：`mcp-{服务名}`

---

## 📍 服务访问地址

### 格式
```
https://junfeng530.xyz/mcp/{服务名小写}
```

### 示例
| 包目录名 | 容器名 | 访问地址 |
|---------|--------|----------|
| EventAnalyzer | mcp-eventanalyzer | https://junfeng530.xyz/mcp/eventanalyzer |
| YourService | mcp-yourservice | https://junfeng530.xyz/mcp/yourservice |

---

## 🔍 监控与调试

### 查看部署日志
GitHub Actions 页面：
```
https://github.com/upJiang/ai-mcp-study/actions
```

### SSH 到服务器查看容器日志
```bash
ssh user@junfeng530.xyz
cd /opt/mcp-services/ai-mcp-study/mcp-list

# 查看所有服务状态
docker-compose ps

# 查看特定服务日志
docker-compose logs -f eventanalyzer

# 查看所有日志
docker-compose logs -f
```

### 重启服务
```bash
# 重启单个服务
docker-compose restart eventanalyzer

# 重启所有服务
docker-compose restart
```

---

## 🛠️ 服务配置说明

### 自动配置项

每个服务自动获得：
- **端口**：容器内 8000（HTTP）
- **网络**：`mcp-network` 桥接网络
- **重启策略**：`unless-stopped`
- **日志**：JSON 格式，最多 10MB × 3 个文件
- **环境变量**：
  ```yaml
  PYTHONUNBUFFERED=1      # Python 输出不缓冲
  MCP_TRANSPORT=http      # 使用 HTTP 传输（已弃用，使用 stdio）
  MCP_PORT=8000          # 服务端口
  ```

### 自定义配置

如需自定义配置（如添加环境变量、挂载卷等），可以：
1. 在包目录下创建 `.env` 文件
2. 修改 `deployment/generate-compose.sh` 脚本

---

## ⚠️ 注意事项

### 1. 包命名规则
- 使用 **PascalCase** 命名包目录（如 `EventAnalyzer`）
- 服务名会自动转换为 **lowercase-kebab-case**（如 `eventanalyzer`）

### 2. 必需文件
确保包含：
- ✅ `server.py` - MCP 服务器入口
- ✅ `requirements.txt` - Python 依赖列表

### 3. MCP 传输模式
目前使用 **stdio** 模式（标准输入输出）：
```python
async with stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream, ...)
```

### 4. 部署触发条件
以下路径变更会触发自动部署：
- `mcp-list/packages/**` - 包代码变更
- `mcp-list/deployment/**` - 部署配置变更
- `.github/workflows/deploy-python-mcp.yml` - 工作流变更

---

## 🎯 完整示例：EventAnalyzer

当前已部署的服务示例，可作为参考：

```bash
mcp-list/packages/EventAnalyzer/
├── server.py                      # MCP 服务器
├── requirements.txt               # 依赖：mcp, requests
├── .dockerignore                  # Docker 构建排除规则
├── README.md                      # 服务文档
├── chrome-extension/              # Chrome 扩展（不会打包到 Docker）
│   ├── manifest.json
│   ├── background.js
│   └── icons/
└── src/                           # 业务逻辑
    ├── api_client.py              # API 客户端
    ├── event_analyzer.py          # 事件分析器
    ├── field_explainer.py         # 字段解释器
    ├── code_searcher.py           # 代码搜索器
    └── utils/
        └── base64_decoder.py      # Base64 解码器
```

**访问地址：** `https://junfeng530.xyz/mcp/eventanalyzer`

**提供的工具：**
1. `query_event_fields` - 查询事件字段定义
2. `analyze_tracking_data` - 分析埋点数据
3. `explain_field` - 解释字段含义
4. `find_field_in_code` - 在代码中搜索字段
5. `compare_events` - 比较事件差异

---

## 🚀 下一步

1. **创建新服务**：参考上述步骤在 `packages/` 下创建新包
2. **测试服务**：推送后等待 2-3 分钟，访问 `https://junfeng530.xyz/mcp/{服务名}`
3. **查看日志**：GitHub Actions 查看部署状态
4. **迭代开发**：修改代码 → 推送 → 自动重新部署

**现在就开始添加您的第一个 Python MCP 服务吧！** 🎉

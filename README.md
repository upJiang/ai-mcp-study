# Claude Stats MCP - AI 使用统计分析工具

基于 MCP (Model Context Protocol) 的 Claude Code 使用统计分析工具。提供 Node.js 和 Python 两种实现方式。

## 🚀 快速启动（推荐）

### 启动 Node.js 版本

```bash
./start-node.sh
```

**特点**：
- ✅ 自动检查 Node.js 环境
- ✅ 自动安装依赖
- ✅ 适合本地开发
- ✅ STDIO 模式，可直接在 Cursor 中配置

### 启动 Python 版本

```bash
./start-python.sh
```

**特点**：
- ✅ 自动检查 Python 环境
- ✅ 自动创建虚拟环境
- ✅ 自动安装依赖
- ✅ 支持 STDIO 和 HTTP 两种模式
- ✅ 适合远程部署

启动后可选择：
1. **STDIO 模式** - 本地使用，配合 Cursor
2. **HTTP 模式** - 远程访问，地址: `http://localhost:8000/mcp`

### 📦 NPX/PIPX 快速使用（推荐分发）

**Node.js 版本（NPX）**：
```bash
# 发布到 npm
./publish-npm.sh

# 用户使用
npx claude-stats-mcp
```

**Python 版本（PIPX）**：
```bash
# 发布到 PyPI
./publish-pypi.sh

# 用户使用
pipx install claude-stats-mcp
```

**详细说明**: 查看 [使用指南.md](./使用指南.md)

## 📁 项目结构

```
ai-mcp-study/
├── start-node.sh           # Node.js 快速启动脚本 ⭐
├── start-python.sh         # Python 快速启动脚本 ⭐
├── publish-npm.sh          # NPM 包发布脚本 📦
├── publish-pypi.sh         # PyPI 包发布脚本 🐍
├── keys.json               # API Key 配置文件
├── node-mcp-demo/          # Node.js 实现
│   ├── src/
│   │   ├── index.ts        # MCP 服务器入口
│   │   ├── tools.ts        # 8个工具函数
│   │   └── utils/          # 工具模块
│   └── package.json
├── python-mcp-demo/        # Python 实现
│   ├── server.py           # MCP 服务器 + 工具
│   ├── utils/              # 工具模块
│   └── requirements.txt
└── 快速开始.md             # 详细教程
```

## 🛠️ 在 Cursor 中配置

### Node.js 版本配置

编辑 `~/.cursor/mcp.json` 或 `~/.config/cursor/config.json`:

```json
{
  "mcpServers": {
    "claude-stats-node": {
      "command": "npx",
      "args": ["tsx", "/完整路径/node-mcp-demo/src/index.ts"],
      "env": {
        "KEYS_CONFIG_PATH": "/完整路径/keys.json"
      }
    }
  }
}
```

### Python 版本配置

#### STDIO 模式（本地）

```json
{
  "mcpServers": {
    "claude-stats-python": {
      "command": "/完整路径/python-mcp-demo/venv/bin/python",
      "args": ["/完整路径/python-mcp-demo/server.py"],
      "env": {
        "KEYS_CONFIG_PATH": "/完整路径/keys.json"
      }
    }
  }
}
```

#### HTTP 模式（远程）

```json
{
  "mcpServers": {
    "claude-stats-python": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## 🔧 8个可用工具

| 工具名称 | 功能描述 | 示例问题 |
|---------|---------|---------|
| `query_today_stats` | 查询今日统计 | "今天总共花了多少钱？" |
| `query_monthly_stats` | 查询本月统计 | "本月使用情况怎么样？" |
| `query_user_stats` | 查询特定用户 | "查询江俊锋的使用情况" |
| `query_top_users` | Top用户排行 | "使用率最高的是谁？" |
| `compare_users` | 对比用户 | "对比江俊锋和陈雷" |
| `analyze_usage_trend` | 趋势分析 | "分析使用趋势" |
| `detect_anomalies` | 异常检测 | "有没有超出限额的？" |
| `generate_report` | 生成报告 | "生成今日报告" |

## ✅ 快速验证

启动服务后，在 Cursor 中重启，然后尝试：

```
你: 今天使用率最高的是谁？
AI: [会自动调用 query_top_users 工具并返回结果]
```

## 📖 详细文档

- [快速开始指南](./快速开始.md) - 5分钟快速体验
- [使用指南](./使用指南.md) - ⭐ NPX/PIPX 完整使用说明
- [MCP开发入门与实战](./MCP开发入门与实战.md) - 完整教程
- [部署指南](./DEPLOYMENT.md) - 生产环境部署
- [Node.js Demo 文档](./node-mcp-demo/README.md) - Node.js 版详细说明
- [Python Demo 文档](./python-mcp-demo/README.md) - Python 版详细说明

## 🐛 故障排查

### Node.js 脚本问题

```bash
# 检查 Node 版本（需要 >= 18）
node -v

# 手动清理重装
cd node-mcp-demo
rm -rf node_modules package-lock.json
npm install
```

### Python 脚本问题

```bash
# 检查 Python 版本（需要 >= 3.8）
python3 --version

# 手动重建虚拟环境
cd python-mcp-demo
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 配置文件问题

确保 `keys.json` 文件存在且格式正确：

```json
{
  "api_keys": [
    {
      "name": "用户名",
      "account": "账号标识",
      "apiKey": "cr_xxxxx"
    }
  ]
}
```

## 🔄 手动启动（不使用脚本）

### Node.js

```bash
cd node-mcp-demo
npm install
export KEYS_CONFIG_PATH=/完整路径/keys.json
npm run dev
```

### Python

```bash
cd python-mcp-demo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# STDIO 模式
KEYS_CONFIG_PATH=/完整路径/keys.json python server.py

# HTTP 模式
KEYS_CONFIG_PATH=/完整路径/keys.json \
MCP_TRANSPORT=http \
MCP_PORT=8000 \
python server.py
```

## 🎯 技术栈

### Node.js 版本
- FastMCP (TypeScript)
- Axios
- TypeScript
- Zod (类型验证)

### Python 版本
- FastMCP (Python)
- HTTPX
- Pydantic
- python-dotenv

## 📚 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io)
- [FastMCP TypeScript](https://github.com/punkpeye/fastmcp)
- [FastMCP Python](https://github.com/jlowin/fastmcp)
- [Cursor MCP 文档](https://docs.cursor.com/advanced/mcp)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT

---

**开发愉快！** 🚀

有问题？查看[快速开始指南](./快速开始.md)或各 Demo 的 README！

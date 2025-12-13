# MCP 快速开发模板

**5 分钟开发你的 MCP 工具** - 无需懂 Node.js

## 前置准备

只需要 3 个东西：
1. 安装 [Node.js](https://nodejs.org/) (>= 18)
2. 安装 Cursor 或 Claude Code
3. npm 账号（用于发布，[点击注册](https://www.npmjs.com/signup)）

## 快速开始

### 第 1 步：在此目录打开 AI 工具

```bash
# 在本目录打开 Cursor
code .

# 或打开 Claude Code
claude .
```

### 第 2 步：告诉 AI 你的需求

直接对 AI 说：

> "创建一个 MCP 项目，用于查询公司的 MySQL 数据库"

或

> "创建一个 MCP 工具，调用外部 API 获取天气信息"

**AI 会自动生成所有代码！**

### 第 3 步：安装依赖

```bash
npm install
```

### 第 4 步：测试

```bash
npm run dev
```

### 第 5 步：发布

```bash
./scripts/publish-npm.sh
```

## 就这么简单！

不需要懂代码，AI 会帮你搞定一切。

---

## 详细指南

- [5 分钟快速开始](QUICKSTART.md)
- [开发前检查清单](checklists/before-dev.md)
- [常见问题](checklists/troubleshooting.md)
- [示例项目](docs/examples/)

## 如何使用你的 MCP 工具

发布成功后，在 Cursor/Claude Code 配置文件中添加：

```json
{
  "mcpServers": {
    "my-tool": {
      "command": "npx",
      "args": ["-y", "你的包名"]
    }
  }
}
```

重启 AI 工具，开始使用！

## 常见场景

- 📊 **查询数据库**：让 AI 帮你生成数据库查询工具
- 🌐 **调用 API**：集成任何外部 API 服务
- 📁 **文件操作**：读取、搜索、处理文件
- 🔧 **自定义工具**：任何你能想到的功能

## 需要帮助？

1. 查看 [详细文档](docs/mcp-development-guide.md)
2. 参考 [示例项目](docs/examples/)
3. 运行 [环境检查](scripts/check-env.sh)

---

**记住**：你只需要描述需求，AI 会完成所有技术工作！

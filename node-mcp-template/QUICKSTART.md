# 5 分钟快速开始

## 你需要的背景知识

**零！** 你不需要懂任何编程。

## 详细步骤

### 步骤 1：检查环境 (1 分钟)

运行检查脚本：
```bash
./scripts/check-env.sh
```

如果提示缺少 Node.js，安装它：
- **Mac**: `brew install node`
- **Windows**: 从 [nodejs.org](https://nodejs.org/) 下载安装包
- **Linux**: `sudo apt install nodejs npm` 或 `sudo yum install nodejs npm`

### 步骤 2：打开 AI 工具 (30 秒)

在本目录打开 Cursor 或 Claude Code：

```bash
# 使用 Cursor
code .

# 或使用 Claude Code
claude .
```

### 步骤 3：描述需求 (1 分钟)

**方式 1：直接描述**

在 AI 工具中对话：

<details>
<summary>示例 1：数据库查询工具</summary>

```
创建一个 MCP 项目，用于：
- 查询公司的订单数据库
- 数据库类型：MySQL
- 连接信息存在配置文件中
- 包含以下功能：
  1. 查询订单列表
  2. 查询订单详情
  3. 统计订单数量
```
</details>

<details>
<summary>示例 2：API 集成工具</summary>

```
创建一个 MCP 工具，用于：
- 调用高德地图 API
- 功能：
  1. 地址转经纬度
  2. 路径规划
  3. 周边搜索
- API Key 存在环境变量中
```
</details>

<details>
<summary>示例 3：文件处理工具</summary>

```
创建一个 MCP 工具，用于：
- 搜索项目中的 TODO 注释
- 统计代码行数
- 生成项目结构树
```
</details>

**方式 2：参考示例**

查看 `docs/examples/` 选择类似的示例，告诉 AI：

```
参考 docs/examples/database-query.md，
创建一个查询我们公司数据库的工具
```

### 步骤 4：AI 生成代码 (自动)

AI 会自动生成：
- ✅ 完整的项目结构
- ✅ 所有代码文件（TypeScript）
- ✅ 配置文件模板
- ✅ package.json 配置
- ✅ README 文档

**你不需要理解这些代码！**

### 步骤 5：安装依赖 (1 分钟)

```bash
npm install
```

等待依赖安装完成。

### 步骤 6：配置（如果需要）(30 秒)

如果工具需要配置（数据库连接、API 密钥等），AI 会生成配置文件模板。

例如 `config/database.json.example`：

```json
{
  "host": "localhost",
  "user": "root",
  "password": "your-password",
  "database": "your-database"
}
```

复制并填写真实配置：

```bash
cp config/database.json.example config/database.json
# 然后编辑 config/database.json 填写真实信息
```

### 步骤 7：测试运行 (30 秒)

```bash
npm run dev
```

看到类似输出就成功了：

```
========================================
MCP Server: My Tool
Transport: STDIO
========================================
Server started successfully
```

按 `Ctrl + C` 停止服务器。

### 步骤 8：发布到 npm (1 分钟)

#### 8.1 首次发布需要登录 npm

```bash
npm login
# 输入你的 npm 用户名、密码、邮箱
```

没有账号？去 [npmjs.com](https://www.npmjs.com/signup) 注册一个。

#### 8.2 运行发布脚本

```bash
./scripts/publish-npm.sh
```

脚本会引导你完成：
1. ✅ 检查配置
2. ✅ 运行构建
3. ✅ 选择版本号
4. ✅ 发布到 npm

### 步骤 9：配置使用 (30 秒)

发布成功后，在 Cursor/Claude Code 配置文件中添加：

**Cursor 配置位置**：
- Mac: `~/Library/Application Support/Cursor/User/globalStorage/rooveterinaryinc.roo-cline/settings/cline_mcp_settings.json`
- Windows: `%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json`

**配置内容**：

```json
{
  "mcpServers": {
    "my-tool": {
      "command": "npx",
      "args": ["-y", "@your-org/your-package-name"]
    }
  }
}
```

替换 `@your-org/your-package-name` 为你的包名（在 package.json 中的 `name` 字段）。

### 步骤 10：重启并使用 (10 秒)

1. 重启 Cursor/Claude Code
2. 在对话中测试你的工具

例如：

```
帮我查询一下订单数据库中的最新 10 条订单
```

AI 会自动调用你刚创建的 MCP 工具！

## 完成！

总共不到 5 分钟，你已经：
- ✅ 开发了一个 MCP 工具
- ✅ 发布到了 npm
- ✅ 配置到了 Cursor/Claude Code
- ✅ 可以在 AI 对话中使用

**不需要懂任何代码！**

---

## 常见问题

### Q1: 我不懂 TypeScript，能开发吗？

**A**: 能！你只需要描述需求，AI 会生成所有代码。

### Q2: 包名已被占用怎么办？

**A**: 修改 `package.json` 中的 `name` 字段，换一个唯一的名字。

建议格式：
- `@your-username/your-package`（推荐）
- `your-company-your-package`

### Q3: 发布失败怎么办？

**A**: 运行诊断脚本：

```bash
./scripts/check-env.sh
```

常见原因：
1. 未登录 npm → 运行 `npm login`
2. 包名重复 → 修改 `package.json` 中的 `name`
3. 网络问题 → 检查网络连接

### Q4: 如何更新已发布的工具？

**A**: 修改代码后，再次运行发布脚本：

```bash
./scripts/publish-npm.sh
```

选择合适的版本更新类型：
- `patch` (1.0.0 → 1.0.1) - 小修复
- `minor` (1.0.0 → 1.1.0) - 新功能
- `major` (1.0.0 → 2.0.0) - 重大更新

### Q5: 如何删除已发布的包？

**A**:

```bash
npm unpublish @your-org/package-name --force
```

**注意**：发布后 24 小时内可以删除，超过 24 小时需要联系 npm 支持。

### Q6: 工具在 Cursor 中不显示？

**A**: 检查清单：

1. ✅ 确认已发布到 npm：访问 `https://www.npmjs.com/package/你的包名`
2. ✅ 确认配置文件路径正确
3. ✅ 确认配置格式正确（JSON 语法）
4. ✅ 重启 Cursor
5. ✅ 查看 Cursor 的 MCP 日志（如果有错误会显示）

### Q7: 如何调试工具？

**A**:

在开发模式运行：

```bash
npm run dev
```

AI 工具会连接到这个本地服务器进行测试。

查看日志输出，AI 会在 `console.error()` 中输出调试信息。

---

## 下一步

- 📚 查看 [完整开发指南](docs/mcp-development-guide.md)
- 🎯 浏览 [工具模板](docs/tool-templates.md)
- 💡 参考 [示例项目](docs/examples/)
- ✅ 使用 [检查清单](checklists/) 确保质量

**记住**：遇到问题就问 AI，它会帮你解决！

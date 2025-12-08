# Claude Stats MCP - Node.js版本

基于FastMCP (TypeScript)的Claude Code使用统计MCP服务器。

## 功能特性

✨ **8个强大的工具函数**：
- 📊 查询今日/本月统计
- 👤 查询特定用户数据
- 🏆 查询Top用户排行
- 🔄 对比用户使用情况
- 📈 分析使用趋势
- ⚠️ 检测异常使用
- 📑 生成完整报告

🚀 **多种使用方式**：
- 本地开发（STDIO模式）
- 发布到npm（npx直接使用）
- 远程HTTPS部署

## 快速开始

### 前置要求

- Node.js >= 18.0.0
- npm 或 yarn

### 安装依赖

```bash
cd node-mcp-demo
npm install
```

### 配置

1. **复制配置文件**

```bash
# 从ccReport复制keys.json到node-mcp-demo目录
cp ../ccReport/config/keys.json ./config/keys.json

# 或创建符号链接
ln -s ../ccReport/config/keys.json ./config/keys.json
```

2. **环境变量配置（可选）**

```bash
# 复制示例文件
cp .env.example .env

# 编辑.env文件
# MCP_TRANSPORT=stdio  # 或 http
# MCP_PORT=8000
# KEYS_CONFIG_PATH=../ccReport/config/keys.json
```

### 本地运行

#### 开发模式（推荐）

```bash
npm run dev
```

#### 构建后运行

```bash
npm run build
npm start
```

## 在Cursor中使用

### 方式1: 本地开发模式

在Cursor的MCP配置文件中添加：

**macOS/Linux**: `~/.config/cursor/config.json`
**Windows**: `%APPDATA%\Cursor\config.json`

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["tsx", "/Users/your-path/node-mcp-demo/src/index.ts"],
      "env": {
        "KEYS_CONFIG_PATH": "/Users/your-path/ccReport/config/keys.json"
      }
    }
  }
}
```

### 方式2: 通过npm包使用（发布后）

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["claude-stats-mcp"]
    }
  }
}
```

### 方式3: HTTP远程模式

```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

## 工具说明

### 1. query_today_stats

查询今日所有账号的使用统计。

**参数**：
- `forceRefresh` (boolean, 可选): 是否强制刷新缓存

**AI使用示例**：
```
用户：今天的使用情况怎么样？
AI：[调用 query_today_stats] 
    今日共9个账号，总费用$125.80，总请求数2,450次
```

### 2. query_monthly_stats

查询本月所有账号的使用统计。

**参数**：
- `forceRefresh` (boolean, 可选): 是否强制刷新缓存

**AI使用示例**：
```
用户：本月总共花了多少钱？
AI：[调用 query_monthly_stats]
    本月总费用$2,580.50
```

### 3. query_user_stats

查询特定用户的统计数据。

**参数**：
- `userName` (string, 必填): 用户名称或账号关键词
- `period` (string, 可选): daily 或 monthly，默认daily

**AI使用示例**：
```
用户：查询江俊锋今天的使用情况
AI：[调用 query_user_stats userName="江俊锋" period="daily"]
    江俊锋今日费用$18.50，请求数425次
```

### 4. query_top_users

查询使用率最高的前N名用户。

**参数**：
- `limit` (number, 可选): 返回数量（1-20），默认5
- `period` (string, 可选): daily 或 monthly，默认daily

**AI使用示例**：
```
用户：今天使用率最高的是谁？
AI：[调用 query_top_users limit=1 period="daily"]
    使用率最高的是江俊锋，费用$18.50
```

### 5. compare_users

比较两个用户的使用情况。

**参数**：
- `user1Name` (string, 必填): 第一个用户名称
- `user2Name` (string, 必填): 第二个用户名称
- `period` (string, 可选): daily 或 monthly，默认daily

**AI使用示例**：
```
用户：对比江俊锋和陈雷的本月使用情况
AI：[调用 compare_users user1Name="江俊锋" user2Name="陈雷" period="monthly"]
    江俊锋: $280.50, 2450次请求
    陈雷: $195.30, 1680次请求
    江俊锋的使用量高出43.6%
```

### 6. get_usage_trend

获取使用趋势分析。

**参数**：无

**AI使用示例**：
```
用户：分析一下使用趋势
AI：[调用 get_usage_trend]
    今日费用$125.80，本月日均$118.50
    今日使用量高于平均水平6.2%
```

### 7. detect_anomalies

检测异常使用情况。

**参数**：
- `threshold` (number, 可选): 费用阈值，默认$40
- `period` (string, 可选): daily 或 monthly，默认daily

**AI使用示例**：
```
用户：检测有没有超出限额的账号
AI：[调用 detect_anomalies threshold=40 period="daily"]
    发现1个账号超过阈值：
    - 账号3: $45.20（超出$5.20）
```

### 8. generate_report

生成完整的使用报告和优化建议。

**参数**：
- `period` (string, 可选): daily 或 monthly，默认daily

**AI使用示例**：
```
用户：生成今日使用报告
AI：[调用 generate_report period="daily"]
    [返回完整的报告，包括摘要、Top用户、异常、建议等]
```

## 发布到npm

### 1. 准备发布

```bash
# 构建项目
npm run build

# 测试构建结果
node dist/index.js
```

### 2. 登录npm

```bash
npm login
```

### 3. 发布

```bash
# 首次发布
npm publish

# 更新版本后发布
npm version patch  # 或 minor, major
npm publish
```

### 4. 使用已发布的包

```bash
# 用户可以直接使用
npx claude-stats-mcp

# 或全局安装
npm install -g claude-stats-mcp
claude-stats-mcp
```

## 远程HTTP部署

### 使用PM2部署

1. **安装PM2**

```bash
npm install -g pm2
```

2. **创建PM2配置** (`ecosystem.config.js`)

```javascript
module.exports = {
  apps: [{
    name: 'claude-stats-mcp',
    script: './dist/index.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      MCP_TRANSPORT: 'httpStream',
      MCP_PORT: 8000
    }
  }]
};
```

3. **启动服务**

```bash
npm run build
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /mcp {
        proxy_pass http://localhost:8000/mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 配置HTTPS

```bash
# 使用Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

## Docker部署

### 1. 创建Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist ./dist
COPY config ./config

ENV MCP_TRANSPORT=httpStream
ENV MCP_PORT=8000

EXPOSE 8000

CMD ["node", "dist/index.js"]
```

### 2. 构建镜像

```bash
npm run build
docker build -t claude-stats-mcp .
```

### 3. 运行容器

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  --name claude-stats-mcp \
  claude-stats-mcp
```

## 故障排查

### 问题1: 找不到配置文件

```
错误: 加载API Key配置失败: 配置文件不存在
```

**解决方案**:
- 确保 `config/keys.json` 存在
- 或设置环境变量 `KEYS_CONFIG_PATH`

### 问题2: API请求失败

```
错误: 获取统计数据失败
```

**解决方案**:
- 检查网络连接
- 检查API Key是否有效
- 查看API服务是否正常

### 问题3: Cursor无法连接MCP服务器

**解决方案**:
- 检查配置文件路径是否正确
- 确保命令可执行（`npx tsx` 或 `node`）
- 查看Cursor的开发者工具日志

### 问题4: TypeScript编译错误

```bash
# 清除缓存重新编译
rm -rf dist node_modules
npm install
npm run build
```

## 开发调试

### 查看日志

```bash
# STDIO模式（输出到stderr）
npm run dev 2> debug.log

# HTTP模式
npm run dev
# 访问 http://localhost:8000/mcp
```

### 测试工具

```bash
# 使用MCP Inspector测试
npx @modelcontextprotocol/inspector npx tsx src/index.ts
```

## 技术栈

- **FastMCP**: MCP服务器框架
- **TypeScript**: 类型安全的JavaScript
- **Zod**: 参数验证
- **Axios**: HTTP客户端
- **dotenv**: 环境变量管理

## 项目结构

```
node-mcp-demo/
├── src/
│   ├── index.ts              # MCP服务器入口
│   ├── tools.ts              # 工具函数定义
│   └── utils/
│       ├── apiClient.ts      # API客户端
│       ├── dataAnalyzer.ts   # 数据分析
│       └── configLoader.ts   # 配置加载
├── dist/                     # 编译输出
├── config/                   # 配置文件
├── package.json
├── tsconfig.json
└── README.md
```

## 相关链接

- [FastMCP文档](https://github.com/punkpeye/fastmcp)
- [MCP官方文档](https://modelcontextprotocol.io)
- [Cursor MCP配置指南](https://docs.cursor.com/advanced/mcp)

## License

MIT

---

**开发愉快！** 🎉

如有问题，欢迎提Issue或查阅主文档。


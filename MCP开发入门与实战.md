# MCP开发入门与实战

## 目录

- [什么是MCP](#什么是mcp)
- [MCP的作用](#mcp的作用)
- [使用方式](#使用方式)
- [支持的语言](#支持的语言)
- [交互方式](#交互方式)
- [快速开发框架介绍](#快速开发框架介绍)
- [实战Demo预览](#实战demo预览)
- [开始使用](#开始使用)

---

## 什么是MCP

**MCP（Model Context Protocol，模型上下文协议）** 是由 Anthropic 开发的开放协议，用于标准化 AI 应用程序与外部数据源和工具之间的集成方式。

### 核心概念

MCP 就像是 AI 应用的"USB-C接口"，它提供了一种统一的方式让大型语言模型（LLM）能够：
- 🔌 **连接外部系统**：数据库、API、文件系统等
- 🛠️ **调用工具函数**：执行具体操作
- 📚 **访问资源**：获取上下文信息
- 💬 **使用提示模板**：标准化交互方式

### 架构示意

```
┌─────────────────┐
│   AI 应用       │
│ (Cursor/Claude) │
└────────┬────────┘
         │ MCP 协议
         │ (JSON-RPC 2.0)
         │
┌────────┴────────┐
│   MCP Server    │
│                 │
│  ┌───────────┐  │
│  │  Tools    │  │  执行操作
│  ├───────────┤  │
│  │ Resources │  │  提供数据
│  ├───────────┤  │
│  │  Prompts  │  │  交互模板
│  └───────────┘  │
└────────┬────────┘
         │
    ┌────┴─────┐
    │  外部系统 │
    │ 数据/服务 │
    └──────────┘
```

---

## MCP的作用

### 1. 扩展AI能力

通过MCP，AI可以突破纯语言模型的限制，获得实际操作能力：
- 📊 **数据查询**：从数据库、API获取实时数据
- ✍️ **文件操作**：读写文件、管理文档
- 🌐 **网络请求**：调用REST API、获取网页内容
- 🔧 **系统操作**：执行命令、管理进程

### 2. 标准化集成

- ✅ **统一接口**：一次开发，多处使用
- ✅ **插件式架构**：轻松添加新功能
- ✅ **协议标准**：不同系统间互操作
- ✅ **降低成本**：减少重复开发工作

### 3. 提高开发效率

- ⚡ **快速构建**：使用框架快速开发MCP服务器
- 🔄 **复用代码**：现有API可轻松封装为MCP工具
- 🧩 **模块化**：工具、资源、提示独立管理
- 🚀 **易于部署**：支持本地和远程多种部署方式

---

## 使用方式

MCP 支持多种传输模式，适应不同的使用场景：

### 1. STDIO（标准输入输出）

**特点**：
- 📍 适合本地开发和测试
- 🔒 安全性高（本地进程通信）
- ⚡ 延迟低
- 💻 需要在同一台机器上运行

**使用场景**：
- Cursor IDE 本地开发
- Claude Desktop 本地工具
- 命令行工具集成

**配置示例**：
```json
{
  "mcpServers": {
    "my-tool": {
      "command": "npx",
      "args": ["my-mcp-server"]
    }
  }
}
```

### 2. SSE（Server-Sent Events）

**特点**：
- 📡 单向流式传输（服务器到客户端）
- 🌐 基于HTTP，易于部署
- ⚠️ 仅支持服务器推送
- 📜 旧版协议，逐渐被替代

**使用场景**：
- 服务器主动推送更新
- 实时通知系统
- 向后兼容旧版本

### 3. HTTP/Streamable HTTP（推荐）

**特点**：
- 🔄 双向通信
- 🌍 支持远程部署
- 🔐 可配置HTTPS加密
- 📈 可扩展性强

**使用场景**：
- 远程MCP服务器
- 团队共享工具
- 生产环境部署
- 跨网络访问

**配置示例**：
```json
{
  "mcpServers": {
    "remote-tool": {
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

---

## 支持的语言

MCP 是语言无关的协议，目前官方和社区提供了多种语言的SDK：

| 语言 | 状态 | 推荐框架 | 特点 |
|-----|------|---------|------|
| **TypeScript/Node.js** | ✅ 官方支持 | FastMCP | 生态丰富，易于发布npm包 |
| **Python** | ✅ 官方支持 | FastMCP | 简洁易用，适合数据处理 |
| **C#** | ✅ 官方支持 | MCP SDK | .NET生态集成 |
| **Java** | ✅ 官方支持 | MCP SDK | 企业级应用 |
| **Swift** | ✅ 官方支持 | MCP SDK | iOS/macOS原生支持 |
| **PHP** | 🔶 社区支持 | MCP PHP SDK | Web后端集成 |
| **Rust** | 🔶 社区支持 | rmcp | 高性能场景 |
| **Go** | 🔶 社区支持 | MCP DevTools | 轻量级工具 |

---

## 交互方式

MCP 基于 **JSON-RPC 2.0** 协议进行通信，提供三种核心交互方式：

### 1. 工具调用（Tools）

**说明**：由模型控制，允许AI执行具体操作。

**示例场景**：
- 查询数据库
- 发送邮件
- 创建文件
- 调用API

**代码示例**（FastMCP）：
```typescript
server.addTool({
  name: "search_database",
  description: "在数据库中搜索用户",
  parameters: z.object({
    keyword: z.string().describe("搜索关键词"),
    limit: z.number().default(10).describe("返回结果数量")
  }),
  execute: async ({ keyword, limit }) => {
    const results = await db.search(keyword, limit);
    return JSON.stringify(results);
  }
});
```

### 2. 资源访问（Resources）

**说明**：由应用控制，为AI提供上下文数据。

**示例场景**：
- 文件内容
- 配置信息
- 历史记录
- 系统状态

**代码示例**（FastMCP）：
```typescript
server.addResource({
  uri: "config://database",
  name: "数据库配置",
  mimeType: "application/json",
  fn: async () => {
    return JSON.stringify(config.database);
  }
});
```

### 3. 提示模板（Prompts）

**说明**：由用户控制，预定义的交互模板。

**示例场景**：
- 斜杠命令
- 快捷操作
- 工作流模板
- 常用查询

**代码示例**（FastMCP）：
```python
@mcp.prompt()
def analyze_code(file_path: str):
    return f"请分析以下文件的代码质量：{file_path}"
```

---

## 快速开发框架介绍

### FastMCP - 快速构建MCP服务器

**FastMCP** 是支持 TypeScript 和 Python 两种语言的快速开发框架，让MCP开发变得简单高效。

#### 核心特性

| 特性 | TypeScript | Python | 说明 |
|-----|-----------|--------|------|
| **简单API** | ✅ | ✅ | 简洁的API设计 |
| **类型安全** | ✅ (Zod) | ✅ (类型注解) | 完整的类型检查 |
| **多传输模式** | ✅ | ✅ | STDIO + HTTP |
| **装饰器支持** | ❌ | ✅ | Python支持装饰器 |
| **验证框架** | Zod | Pydantic | 参数验证 |

#### 对比官方SDK

| 项目 | FastMCP | 官方SDK |
|-----|---------|---------|
| **学习曲线** | 平缓 | 陡峭 |
| **代码量** | 少 | 多 |
| **开发速度** | 快 | 中等 |
| **灵活性** | 高 | 更高 |
| **文档** | 简洁 | 详细 |
| **社区** | 成长中 | 官方维护 |

#### 选择建议

- 🟢 **选择FastMCP**：快速开发、简单场景、团队协作
- 🟡 **选择官方SDK**：复杂需求、深度定制、生产环境

---

## 实战Demo预览

本教程提供两个实战Demo，实现 **Claude Code 使用统计查询** 功能。

### Demo功能概述

通过MCP服务器，让AI能够查询和分析Claude Code的使用情况：

**8个核心工具**：

1. **`query_today_stats`** - 查询今日所有账号统计
2. **`query_monthly_stats`** - 查询本月所有账号统计
3. **`query_user_stats`** - 查询特定用户的统计数据
4. **`query_top_users`** - 查询使用率最高的前N名用户
5. **`compare_users`** - 比较多个用户的使用情况
6. **`get_usage_trend`** - 获取使用趋势分析
7. **`detect_anomalies`** - 检测异常使用情况
8. **`generate_report`** - 生成可视化报告建议

### AI对话示例

```
用户：今天使用率最高的是谁？
AI：让我查询一下... [调用 query_top_users]
    今天使用率最高的是江俊锋，费用$12.50，请求数350次。

用户：对比一下江俊锋和陈雷的本月使用情况
AI：[调用 compare_users] 
    本月对比：
    - 江俊锋：$280.50，2,450次请求
    - 陈雷：$195.30，1,680次请求
    江俊锋的使用量高出43.6%

用户：检测一下有没有异常使用情况
AI：[调用 detect_anomalies]
    发现1个异常：账号3今日费用$45.20，超出日限额$40
```

### Demo 1: Node.js 版本

**技术栈**：
- FastMCP (TypeScript)
- Zod 参数验证
- Axios HTTP客户端

**适用场景**：
- ✅ 本地开发（通过npx）
- ✅ 发布到npm
- ✅ 远程HTTPS部署

**部署方式**：
```bash
# 发布到npm后
npx claude-stats-mcp

# 或本地开发
cd node-mcp-demo
npm install
npm start
```

### Demo 2: Python 版本

**技术栈**：
- FastMCP (Python)
- Pydantic 数据验证
- HTTPX 异步HTTP客户端

**适用场景**：
- ✅ Docker部署（推荐）
- ✅ 远程HTTPS部署
- ⚠️ 本地开发（需Python环境）

**部署方式**：
```bash
# Docker部署（推荐）
cd python-mcp-demo
docker-compose up -d

# 或服务器部署
python server.py
```

---

## 开始使用

### 选择合适的Demo

| 使用场景 | 推荐版本 | 原因 |
|---------|---------|------|
| **本地开发使用** | Node.js | 通过npm/npx，无需额外环境 |
| **团队共享部署** | Python (Docker) | 统一环境，一键部署 |
| **远程服务访问** | 两者都可 | 通过HTTPS访问，体验一致 |
| **学习MCP协议** | Node.js | 代码更易读，生态丰富 |

### 快速开始

1. **选择Demo目录**
   ```bash
   cd node-mcp-demo  # 或 python-mcp-demo
   ```

2. **查看README**
   - 每个Demo都有详细的README文档
   - 包含安装、配置、部署说明
   - 提供完整的使用示例

3. **配置API密钥**
   - 复制 `ccReport/config/keys.json` 到Demo目录
   - 或配置环境变量

4. **启动服务**
   - Node.js: `npm start`
   - Python: `python server.py` 或 `docker-compose up`

5. **在Cursor中配置**
   - 打开Cursor设置
   - 添加MCP服务器配置
   - 开始使用AI查询统计数据！

### 相关链接

- 📚 [MCP官方文档](https://modelcontextprotocol.io)
- 🚀 [FastMCP TypeScript](https://github.com/punkpeye/fastmcp)
- 🐍 [FastMCP Python](https://github.com/jlowin/fastmcp)
- 💬 [MCP Discord社区](https://discord.gg/modelcontextprotocol)

---

## FastMCP快速开发指南（Node.js/TypeScript）

### 1. 初始化项目

#### 创建项目结构

```bash
mkdir my-mcp-server
cd my-mcp-server
npm init -y
```

#### 安装依赖

```bash
# 安装FastMCP和必要依赖
npm install fastmcp zod axios dotenv

# 安装开发依赖
npm install -D typescript tsx @types/node
```

#### 配置package.json

```json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "my-mcp-server": "./dist/index.js"
  },
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "fastmcp": "latest",
    "zod": "^3.22.4"
  }
}
```

#### 配置TypeScript（tsconfig.json）

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

### 2. 创建MCP服务器

#### 基础服务器（src/index.ts）

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import { z } from 'zod';

// 创建服务器实例
const server = new FastMCP({
  name: 'My MCP Server',
  version: '1.0.0',
});

// 定义第一个工具
server.addTool({
  name: 'hello',
  description: '向用户问好',
  parameters: z.object({
    name: z.string().describe('用户名称')
  }),
  execute: async (args) => {
    return `你好，${args.name}！`;
  }
});

// 启动服务器（STDIO模式）
server.start({
  transportType: 'stdio'
});
```

#### 测试运行

```bash
npm run dev
```

### 3. 定义工具（Tools）

#### 基础工具定义

```typescript
server.addTool({
  name: 'tool_name',           // 工具名称（必填）
  description: '工具描述',      // 工具说明（必填）
  parameters: z.object({       // 参数定义（使用Zod）
    param1: z.string().describe('参数1说明'),
    param2: z.number().optional().describe('参数2说明（可选）')
  }),
  execute: async (args) => {   // 执行函数
    // 处理逻辑
    return '返回结果';
  }
});
```

#### 完整示例：封装API调用

```typescript
import axios from 'axios';
import { z } from 'zod';

// 定义数据查询工具
server.addTool({
  name: 'query_user_data',
  description: '查询用户数据',
  parameters: z.object({
    userId: z.string().describe('用户ID'),
    includeDetails: z.boolean().default(false).describe('是否包含详细信息')
  }),
  execute: async (args) => {
    try {
      // 调用外部API
      const response = await axios.get(
        `https://api.example.com/users/${args.userId}`,
        {
          params: { details: args.includeDetails }
        }
      );
      
      // 返回格式化的结果
      return JSON.stringify(response.data, null, 2);
    } catch (error: any) {
      // 错误处理
      return JSON.stringify({ 
        error: '查询失败', 
        message: error.message 
      }, null, 2);
    }
  }
});
```

#### 带数据处理的工具

```typescript
// 定义统计分析工具
server.addTool({
  name: 'analyze_stats',
  description: '分析统计数据并生成报告',
  parameters: z.object({
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期'),
    threshold: z.number().min(0).default(100).describe('阈值')
  }),
  execute: async (args) => {
    // 1. 获取数据
    const data = await fetchDataFromAPI(args.period);
    
    // 2. 数据处理
    const processed = data
      .filter(item => item.value > args.threshold)
      .sort((a, b) => b.value - a.value);
    
    // 3. 生成分析结果
    const analysis = {
      period: args.period,
      totalItems: data.length,
      itemsAboveThreshold: processed.length,
      topItems: processed.slice(0, 5).map(item => ({
        name: item.name,
        value: item.value
      })),
      summary: `在${processed.length}个项目中，发现${processed.length}个超过阈值`
    };
    
    // 4. 返回JSON格式结果
    return JSON.stringify(analysis, null, 2);
  }
});
```

#### 无参数工具

```typescript
server.addTool({
  name: 'get_server_status',
  description: '获取服务器状态',
  parameters: z.object({}),  // 空对象表示无参数
  execute: async () => {
    return JSON.stringify({
      status: 'running',
      uptime: process.uptime(),
      memory: process.memoryUsage()
    }, null, 2);
  }
});
```

### 4. 与AI对话交互

#### AI如何调用工具

1. **用户提问**：`"今天使用率最高的是谁？"`

2. **AI识别意图**：分析用户问题，决定调用 `query_top_users` 工具

3. **工具调用**：
```json
{
  "name": "query_top_users",
  "arguments": {
    "limit": 1,
    "period": "daily"
  }
}
```

4. **服务器执行**：FastMCP调用execute函数

5. **返回结果**：工具返回JSON数据

6. **AI解释**：AI将结果转换为自然语言回复用户

#### 优化工具描述

**好的描述**（AI更容易理解）：

```typescript
server.addTool({
  name: 'search_user',
  description: '在数据库中搜索用户信息。支持按姓名、邮箱、ID搜索。返回匹配的用户列表及详细信息。',
  parameters: z.object({
    keyword: z.string().describe('搜索关键词：可以是用户名、邮箱或ID'),
    limit: z.number().default(10).describe('返回结果数量，最多100条')
  }),
  execute: async (args) => {
    // ...
  }
});
```

**不好的描述**：

```typescript
server.addTool({
  name: 'search',
  description: '搜索',  // 太模糊
  parameters: z.object({
    q: z.string()  // 缺少描述
  }),
  execute: async (args) => {
    // ...
  }
});
```

### 5. 发布到npm

#### 准备发布

**1. 更新package.json**

```json
{
  "name": "claude-stats-mcp",
  "version": "1.0.0",
  "description": "MCP服务器用于查询Claude Code使用统计",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "claude-stats-mcp": "./dist/index.js"
  },
  "files": [
    "dist",
    "README.md"
  ],
  "keywords": [
    "mcp",
    "claude",
    "statistics"
  ],
  "author": "Your Name",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/claude-stats-mcp"
  }
}
```

**2. 添加Shebang到入口文件**

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
// ... 其余代码
```

**3. 创建.npmignore**

```
src/
tsconfig.json
*.log
.env
.env.*
node_modules/
.DS_Store
```

**4. 构建项目**

```bash
npm run build
```

**5. 测试本地包**

```bash
# 测试构建结果
node dist/index.js

# 或使用npm link测试
npm link
claude-stats-mcp  # 测试命令是否可用
npm unlink
```

#### 发布步骤

```bash
# 1. 登录npm
npm login

# 2. 检查package.json
cat package.json

# 3. 发布
npm publish

# 4. 验证发布
npm info claude-stats-mcp
```

#### 使用已发布的包

```bash
# 用户直接使用（无需安装）
npx claude-stats-mcp

# 或全局安装
npm install -g claude-stats-mcp
claude-stats-mcp
```

### 6. 支持HTTP/HTTPS部署

#### HTTP模式配置

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';

const server = new FastMCP({
  name: 'My Server',
  version: '1.0.0',
});

// ... 添加工具 ...

// 从环境变量获取配置
const transport = process.env.MCP_TRANSPORT || 'stdio';
const port = parseInt(process.env.MCP_PORT || '8000', 10);

if (transport === 'http') {
  // HTTP模式
  server.start({
    transportType: 'httpStream',
    httpStream: {
      port
    }
  });
} else {
  // STDIO模式
  server.start({
    transportType: 'stdio'
  });
}
```

#### 启动HTTP服务器

```bash
# 通过环境变量启动
MCP_TRANSPORT=http MCP_PORT=8000 npm start

# 服务运行在: http://localhost:8000/mcp
```

#### Nginx HTTPS反向代理

**nginx配置文件**：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书（使用Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # MCP代理
    location /mcp {
        proxy_pass http://localhost:8000;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**配置HTTPS**：

```bash
# 1. 安装certbot
sudo apt install certbot python3-certbot-nginx

# 2. 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 3. 测试配置
sudo nginx -t

# 4. 重启Nginx
sudo systemctl restart nginx
```

### 7. 三种调用方式

#### 方式1: npx调用（推荐）

**发布到npm后**：

```bash
# 用户直接使用
npx claude-stats-mcp
```

**Cursor配置**：

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

**优点**：
- ✅ 无需安装
- ✅ 自动使用最新版本
- ✅ 跨平台兼容

#### 方式2: 本地调用

**开发模式**：

```bash
# 直接运行TypeScript源码
npx tsx src/index.ts
```

**Cursor配置**：

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["tsx", "/Users/your-path/my-mcp-server/src/index.ts"],
      "env": {
        "API_KEY": "your-api-key",
        "CONFIG_PATH": "/path/to/config.json"
      }
    }
  }
}
```

**生产模式**：

```bash
# 先构建
npm run build

# 使用Node运行
node dist/index.js
```

**Cursor配置**：

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "node",
      "args": ["/Users/your-path/my-mcp-server/dist/index.js"]
    }
  }
}
```

**优点**：
- ✅ 完全控制代码
- ✅ 适合开发调试
- ✅ 可以修改源码

#### 方式3: HTTPS远程调用

**启动HTTP服务器**：

```bash
# 环境变量方式
MCP_TRANSPORT=http MCP_PORT=8000 npm start

# 或修改代码默认值
```

**Cursor配置**：

```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

**优点**：
- ✅ 团队共享
- ✅ 集中管理
- ✅ 无需本地环境
- ✅ 支持多客户端

### 8. 实战：封装API为MCP工具

#### 场景：查询天气API

```typescript
import { FastMCP } from 'fastmcp';
import { z } from 'zod';
import axios from 'axios';

const server = new FastMCP({
  name: 'Weather MCP',
  version: '1.0.0',
});

// 封装天气查询API
server.addTool({
  name: 'get_weather',
  description: '查询指定城市的天气信息',
  parameters: z.object({
    city: z.string().describe('城市名称，如：北京、上海'),
    unit: z.enum(['celsius', 'fahrenheit']).default('celsius').describe('温度单位')
  }),
  execute: async (args) => {
    try {
      // 调用第三方天气API
      const response = await axios.get('https://api.weather.com/v1/current', {
        params: {
          q: args.city,
          units: args.unit === 'celsius' ? 'metric' : 'imperial',
          appid: process.env.WEATHER_API_KEY
        }
      });
      
      const weather = response.data;
      
      // 格式化返回结果
      const result = {
        city: args.city,
        temperature: weather.main.temp,
        description: weather.weather[0].description,
        humidity: weather.main.humidity,
        windSpeed: weather.wind.speed
      };
      
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({
        error: '查询失败',
        message: error.message
      }, null, 2);
    }
  }
});

server.start({ transportType: 'stdio' });
```

#### 场景：数据库查询

```typescript
// 封装数据库查询
server.addTool({
  name: 'search_database',
  description: '在数据库中搜索记录',
  parameters: z.object({
    table: z.string().describe('表名'),
    keyword: z.string().describe('搜索关键词'),
    limit: z.number().min(1).max(100).default(10).describe('返回条数')
  }),
  execute: async (args) => {
    // 使用数据库客户端
    const db = await connectDatabase();
    
    const results = await db.query(`
      SELECT * FROM ${args.table} 
      WHERE content LIKE ? 
      LIMIT ?
    `, [`%${args.keyword}%`, args.limit]);
    
    await db.close();
    
    return JSON.stringify({
      table: args.table,
      keyword: args.keyword,
      count: results.length,
      results
    }, null, 2);
  }
});
```

#### 场景：文件操作

```typescript
import fs from 'fs/promises';
import path from 'path';

server.addTool({
  name: 'read_config',
  description: '读取配置文件',
  parameters: z.object({
    fileName: z.string().describe('配置文件名')
  }),
  execute: async (args) => {
    const configPath = path.join(process.cwd(), 'config', args.fileName);
    
    try {
      const content = await fs.readFile(configPath, 'utf-8');
      const config = JSON.parse(content);
      
      return JSON.stringify(config, null, 2);
    } catch (error: any) {
      return JSON.stringify({
        error: '读取配置失败',
        file: args.fileName,
        message: error.message
      }, null, 2);
    }
  }
});
```

### 9. 完整示例：Claude Stats MCP

查看本项目的 [`node-mcp-demo`](./node-mcp-demo) 了解完整实现：

```typescript
// 实现的8个工具
1. query_today_stats    - 查询今日统计
2. query_monthly_stats  - 查询本月统计  
3. query_user_stats     - 查询特定用户
4. query_top_users      - Top用户排行
5. compare_users        - 用户对比
6. get_usage_trend      - 趋势分析
7. detect_anomalies     - 异常检测
8. generate_report      - 生成报告
```

**核心代码结构**：

```
src/
├── index.ts              # 服务器入口，注册所有工具
├── utils/
│   ├── apiClient.ts      # API封装层
│   ├── dataAnalyzer.ts   # 数据处理层
│   └── configLoader.ts   # 配置管理
```

**最佳实践**：
- ✅ 分层架构：API层、业务层、工具层
- ✅ 类型安全：使用TypeScript + Zod
- ✅ 错误处理：完善的try-catch和重试机制
- ✅ 数据缓存：避免频繁API调用
- ✅ 配置管理：支持环境变量和配置文件

### 10. 部署检查清单

#### 发布前检查

- [ ] package.json配置正确（name, version, bin）
- [ ] 添加了#!/usr/bin/env node到入口文件
- [ ] 构建成功（npm run build）
- [ ] 本地测试通过（npx tsx src/index.ts）
- [ ] README文档完善
- [ ] .npmignore配置正确
- [ ] LICENSE文件存在

#### 部署前检查

- [ ] 环境变量配置（.env文件）
- [ ] API密钥安全存储
- [ ] 端口未被占用
- [ ] 防火墙规则配置
- [ ] SSL证书有效
- [ ] 日志目录权限正确
- [ ] 进程管理配置（PM2/Systemd）

### 11. 调试技巧

#### 查看MCP通信日志

```typescript
// 添加日志中间件
server.addTool({
  name: 'my_tool',
  description: '...',
  parameters: z.object({...}),
  execute: async (args) => {
    console.error('[DEBUG] Tool called:', 'my_tool');
    console.error('[DEBUG] Args:', JSON.stringify(args));
    
    const result = await doSomething(args);
    
    console.error('[DEBUG] Result:', result);
    return result;
  }
});
```

#### 使用MCP Inspector

```bash
# FastMCP内置Inspector支持
npx fastmcp inspect src/index.ts

# 或使用官方Inspector
npx @modelcontextprotocol/inspector npx tsx src/index.ts
```

#### 测试工具

```bash
# 使用fastmcp dev测试
npx fastmcp dev src/index.ts

# 在另一个终端测试调用
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

---

## 下一步

- 📖 阅读 [Node.js Demo 完整代码](./node-mcp-demo/README.md)
- 📖 阅读 [Python Demo README](./python-mcp-demo/README.md)
- 🔧 尝试添加自己的工具函数
- 📦 发布你的第一个MCP服务器到npm
- 🚀 将MCP服务器部署到生产环境

---

**祝你开发愉快！🎉**

如有问题，欢迎查阅各Demo的README或官方文档：
- [FastMCP TypeScript](https://github.com/punkpeye/fastmcp)
- [MCP官方文档](https://modelcontextprotocol.io)


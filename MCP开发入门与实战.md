# MCP 开发入门与实战

---

## 一、什么是 MCP

**MCP（Model Context Protocol，模型上下文协议）** 是由 Anthropic 于 2024 年 11 月推出的开放协议，用于标准化 AI 应用程序与外部数据源、工具之间的集成方式。

简单来说，MCP 就像是 AI 应用的 **"USB-C 接口"** 或 **"万能插头"**。

### MCP 解决了什么问题？

在没有 MCP 之前，AI 应用接入外部工具面临 **"M×N 问题"**：

```
传统方式：每个 AI 应用都要单独对接每个工具

┌──────────┐     ┌──────────┐     ┌──────────┐
│ Claude   │     │ ChatGPT  │     │ Gemini   │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     ├────────────────┼────────────────┤
     │                │                │
     ▼                ▼                ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ GitHub   │     │ Database │     │ Slack    │
└──────────┘     └──────────┘     └──────────┘

问题：3 个 AI × 3 个工具 = 9 套对接代码
```

有了 MCP 后，变成 **"M+N 问题"**：

```
MCP 方式：统一协议，即插即用

┌──────────┐     ┌──────────┐     ┌──────────┐
│ Claude   │     │ ChatGPT  │     │ Gemini   │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     └────────────────┼────────────────┘
                      │
              ┌───────▼───────┐
              │  MCP 协议层    │
              └───────┬───────┘
                      │
     ┌────────────────┼────────────────┐
     │                │                │
     ▼                ▼                ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ GitHub   │     │ Database │     │ Slack    │
│ (MCP)    │     │ (MCP)    │     │ (MCP)    │
└──────────┘     └──────────┘     └──────────┘

结果：3 个 AI + 3 个工具 = 6 套代码
```

### MCP vs Function Call：有什么区别？

在介绍 MCP 之前，先了解一下 **Function Call（函数调用）** 是什么。

#### 什么是 Function Call？

Function Call 是 OpenAI 在 2023 年推出的一项能力，允许 AI 模型在对话过程中"调用函数"。简单来说，AI 可以识别用户意图，然后告诉你应该调用哪个函数、传什么参数。

**Function Call 的工作流程：**

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 用户提问："北京今天天气怎么样？"                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. AI 分析意图，返回要调用的函数和参数                            │
│     { "name": "get_weather", "arguments": { "city": "北京" } }   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. 开发者自己执行函数，获取结果                                   │
│     const result = await get_weather("北京");  // 你自己实现      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. 把结果发回给 AI，AI 生成最终回复                               │
│     "北京今天晴，气温 25°C，适合出行。"                            │
└─────────────────────────────────────────────────────────────────┘
```

**Function Call 代码示例：**

```javascript
// Function Call 是 API 级别的能力
const response = await openai.chat.completions.create({
  model: "gpt-4",
  messages: [{ role: "user", content: "北京今天天气怎么样？" }],
  tools: [{
    type: "function",
    function: {
      name: "get_weather",
      description: "获取指定城市的天气信息",
      parameters: {
        type: "object",
        properties: {
          city: { type: "string", description: "城市名称" }
        },
        required: ["city"]
      }
    }
  }]
});

// AI 返回要调用的函数和参数
if (response.choices[0].message.tool_calls) {
  const toolCall = response.choices[0].message.tool_calls[0];
  const args = JSON.parse(toolCall.function.arguments);

  // 开发者自己实现并执行函数
  const weatherResult = await get_weather(args.city);

  // 把结果发回给 AI
  const finalResponse = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      { role: "user", content: "北京今天天气怎么样？" },
      response.choices[0].message,
      { role: "tool", tool_call_id: toolCall.id, content: weatherResult }
    ]
  });
}
```

**Function Call 的局限性：**

| 问题 | 说明 |
|-----|------|
| **工具定义重复** | 每次 API 请求都要带上完整的工具定义 |
| **执行逻辑自己写** | AI 只告诉你调用什么，具体执行要自己实现 |
| **平台不统一** | OpenAI、Claude、Gemini 各有各的格式 |
| **无法复用** | 每个项目都要重新定义和实现工具 |
| **无工具发现** | 没有标准的方式让 AI 发现可用工具 |

#### MCP 如何解决这些问题？

MCP 把 Function Call 的"定义"和"执行"都封装到独立的服务中：

```javascript
// MCP 是独立的服务层
const server = new FastMCP({ name: 'Weather MCP' });

server.addTool({
  name: 'get_weather',
  description: '获取天气信息',
  parameters: z.object({ city: z.string() }),
  execute: async (args) => {
    // 工具逻辑在 Server 端实现，不需要开发者再写
    return await fetchWeatherFromAPI(args.city);
  }
});

server.start({ transportType: 'stdio' });

// AI 应用通过 MCP Client 自动发现和调用工具
// 开发者只需要配置一下，不需要写调用代码
```

#### 核心区别对比

| 特性 | Function Call | MCP |
|-----|--------------|-----|
| **架构** | API 请求参数 | 独立服务协议 |
| **工具执行** | 开发者自己实现 | MCP Server 实现 |
| **跨平台** | 各平台格式不同 | 统一标准 |
| **工具发现** | 无 | 自动发现 |
| **复用性** | 每个项目重写 | 一次开发，到处使用 |
| **生态** | 无 | 上万个现成工具 |

**一句话总结：**

> Function Call 是"AI 告诉你要调用什么，你自己去执行"；MCP 是"AI 直接调用现成的服务，拿到结果"。

### MCP 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      AI 应用（Host）                         │
│                   Cursor / Claude Code                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ MCP 协议 (JSON-RPC 2.0)
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     MCP Client                               │
│              （内置于 AI 应用中）                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ MCP Server │  │ MCP Server │  │ MCP Server │
   │   工具 A    │  │   工具 B    │  │   工具 C    │
   └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
         │               │               │
         ▼               ▼               ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │  数据库   │    │   API    │    │  文件系统 │
   └──────────┘    └──────────┘    └──────────┘
```

**核心概念：**
- **Host（宿主）**：AI 应用程序，如 Cursor、Claude Code
- **Client（客户端）**：内置于 Host 中，负责与 Server 通信
- **Server（服务器）**：提供具体工具和资源的服务

---

## 二、MCP 的用途

### 1. 扩展 AI 能力

通过 MCP，AI 可以突破纯语言模型的限制，获得实际操作能力：

- **数据查询**：从数据库、API 获取实时数据
- **文件操作**：读写文件、管理文档
- **网络请求**：调用 REST API、获取网页内容
- **系统操作**：执行命令、管理进程

### 2. 标准化集成

- **统一接口**：一次开发，到处使用
- **即插即用**：新工具无需修改 AI 应用代码
- **降低成本**：减少重复开发工作

### 3. 提高开发效率

- **快速构建**：使用 FastMCP 框架，几分钟即可开发一个 MCP 服务
- **复用代码**：现有 API 可轻松封装为 MCP 工具
- **模块化**：工具、资源、提示独立管理

---

## 三、MCP 的三种传输模式

MCP 支持三种传输模式，适应不同场景。下面分别介绍每种模式的原理和核心代码。

### 1. STDIO（标准输入输出）

**最常用的本地开发模式。**

- 适合：本地开发、个人使用
- 优点：安全性高（本地进程通信）、延迟低、无需网络
- 缺点：必须在同一台机器上运行

**通信原理：**

```
┌─────────────┐                    ┌─────────────┐
│  MCP Client │ ──── stdin ─────▶ │  MCP Server │
│  (AI 应用)   │ ◀─── stdout ───── │  (子进程)    │
└─────────────┘                    └─────────────┘
```

**服务端代码（Node.js）：**

```typescript
import { FastMCP } from 'fastmcp';

const server = new FastMCP({
  name: 'My MCP Server',
  version: '1.0.0',
});

// 添加工具...

// STDIO 模式启动
server.start({
  transportType: 'stdio'
});
```

**客户端配置（Cursor mcp.json）：**

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/server.js"]
    }
  }
}
```

**底层原理：** Client 启动 Server 作为子进程，通过 `process.stdin` 和 `process.stdout` 进行 JSON-RPC 通信。

---

### 2. SSE（Server-Sent Events）

**单向流式传输，基于 HTTP 的服务器推送技术。**

- 适合：服务器主动推送、实时通知场景
- 特点：服务器可以持续推送消息给客户端
- 现状：MCP 早期使用，现逐渐被 Streamable HTTP 替代

**通信原理：**

```
┌─────────────┐                         ┌─────────────┐
│  MCP Client │ ──── HTTP POST ──────▶ │  MCP Server │
│             │ ◀─── SSE Stream ────── │             │
└─────────────┘   (text/event-stream)   └─────────────┘
```

**服务端代码（Node.js 原生实现）：**

```typescript
import express from 'express';

const app = express();

// SSE 端点 - 服务器推送消息
app.get('/mcp/sse', (req, res) => {
  // 设置 SSE 响应头
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // 发送消息给客户端
  const sendEvent = (data: any) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  // 示例：每秒推送一次
  const interval = setInterval(() => {
    sendEvent({ type: 'heartbeat', timestamp: Date.now() });
  }, 1000);

  // 客户端断开时清理
  req.on('close', () => {
    clearInterval(interval);
  });
});

// 接收客户端请求
app.post('/mcp/message', express.json(), (req, res) => {
  const message = req.body;
  // 处理 JSON-RPC 请求...
  res.json({ jsonrpc: '2.0', id: message.id, result: {...} });
});

app.listen(8000);
```

**客户端代码（浏览器 EventSource）：**

```typescript
// 使用浏览器原生 EventSource API
const eventSource = new EventSource('http://localhost:8000/mcp/sse');

// 监听服务器推送的消息
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到服务器消息:', data);
};

// 监听连接打开
eventSource.onopen = () => {
  console.log('SSE 连接已建立');
};

// 监听错误
eventSource.onerror = (error) => {
  console.error('SSE 连接错误:', error);
  eventSource.close();
};

// 发送请求到服务器（SSE 是单向的，需要用 fetch 发送）
async function callTool(toolName: string, args: any) {
  const response = await fetch('http://localhost:8000/mcp/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: { name: toolName, arguments: args }
    })
  });
  return response.json();
}
```

**Node.js 客户端代码（eventsource 库）：**

```typescript
import EventSource from 'eventsource';

// Node.js 环境需要安装 eventsource 包
const es = new EventSource('http://localhost:8000/mcp/sse');

es.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到:', data);
};

es.onerror = (err) => {
  console.error('连接错误:', err);
};
```

---

### 3. HTTP / Streamable HTTP（推荐）

**生产环境首选模式，支持双向通信和流式响应。**

- 适合：远程部署、团队共享、生产环境
- 优点：双向通信、可配置 HTTPS 加密、支持多客户端
- 缺点：需要额外的服务器部署

**通信原理：**

```
┌─────────────┐                              ┌─────────────┐
│  MCP Client │ ──── HTTP POST ───────────▶ │  MCP Server │
│             │ ◀─── Streaming Response ─── │  (独立服务)  │
└─────────────┘                              └─────────────┘
        │                                           │
        │              ┌─────────┐                  │
        └──── HTTPS ───│  Nginx  │──── HTTP ────────┘
                       └─────────┘
```

**服务端代码（FastMCP）：**

```typescript
import { FastMCP } from 'fastmcp';

const server = new FastMCP({
  name: 'My MCP Server',
  version: '1.0.0',
});

// 添加工具
server.addTool({
  name: 'query_data',
  description: '查询数据',
  parameters: z.object({
    keyword: z.string()
  }),
  execute: async (args) => {
    return JSON.stringify({ result: 'data...' });
  }
});

// HTTP 模式启动
server.start({
  transportType: 'httpStream',
  httpStream: {
    port: 8000
  }
});

// 服务运行在 http://localhost:8000/mcp
```

**客户端代码（原生 fetch 调用）：**

```typescript
// HTTP 模式的客户端调用
async function callMcpTool(serverUrl: string, toolName: string, args: any) {
  const response = await fetch(`${serverUrl}/mcp`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: args
      }
    })
  });

  // 处理流式响应
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (reader) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    console.log('收到数据块:', chunk);
  }
}

// 调用示例
callMcpTool('http://localhost:8000', 'query_data', { keyword: 'test' });
```

**客户端配置（Cursor mcp.json - HTTP 模式）：**

```json
{
  "mcpServers": {
    "remote-server": {
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

---

### 三种模式对比

| 特性 | STDIO | SSE | HTTP/Streamable |
|-----|-------|-----|-----------------|
| **通信方向** | 双向 | 单向（服务器→客户端） | 双向 |
| **适用场景** | 本地开发 | 实时推送 | 生产环境 |
| **部署复杂度** | 最简单 | 中等 | 较复杂 |
| **网络要求** | 无 | HTTP | HTTP/HTTPS |
| **多客户端** | 不支持 | 支持 | 支持 |
| **推荐程度** | 开发首选 | 逐渐淘汰 | 生产首选 |

**选择建议：**
- **本地开发调试**：使用 STDIO，最简单
- **生产环境部署**：使用 HTTP/Streamable HTTP
- **需要实时推送**：可以考虑 SSE，但建议直接用 HTTP

---

## 四、MCP 在 Cursor 和 Claude Code 中的配置

### Cursor 配置

**配置文件路径：**
- macOS: `~/.cursor/mcp.json`
- Windows: `%USERPROFILE%\.cursor\mcp.json`

**STDIO 模式配置（npx 方式）：**

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["claude-stats-mcp"],
      "env": {
        "CONFIG_PATH": "/path/to/keys.json"
      }
    }
  }
}
```

**STDIO 模式配置（本地开发）：**

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["tsx", "/path/to/project/src/index.ts"],
      "env": {
        "CONFIG_PATH": "/path/to/keys.json"
      }
    }
  }
}
```

**HTTP 模式配置：**

```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

### Claude Code 配置

**配置文件路径：**
- macOS/Linux: `~/.claude.json`

**配置示例：**

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

---

## 五、实战：开发一个最简易的 MCP

接下来，我们用 **Node.js + FastMCP** 开发一个完整的 MCP 服务。

### 什么是 FastMCP

**FastMCP** 是一个快速开发 MCP 服务器的框架，支持 TypeScript 和 Python 两种语言。相比官方 SDK，它的 API 更简洁，学习曲线更平缓。

**安装依赖：**

```bash
npm install fastmcp zod
```

### 核心代码

**1. 初始化服务器**

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';

// 创建 MCP 服务器实例
const server = new FastMCP({
  name: 'My MCP Server',
  version: '1.0.0',
});
```

这就是创建一个 MCP 服务器所需的全部代码。`name` 和 `version` 会在客户端连接时展示。

**2. 添加工具（Tool）**

工具是 MCP 的核心，它定义了 AI 可以调用的具体功能：

```typescript
import { z } from 'zod';

server.addTool({
  name: 'query_user',           // 工具名称
  description: '查询用户信息',   // 工具描述（AI 根据这个来判断何时调用）
  parameters: z.object({        // 参数定义（使用 Zod 进行类型验证）
    userId: z.string().describe('用户ID'),
    includeDetails: z.boolean().default(false).describe('是否包含详情')
  }),
  execute: async (args) => {    // 执行函数
    // 这里写业务逻辑
    const user = await fetchUser(args.userId);
    return JSON.stringify(user, null, 2);
  }
});
```

**关键点：**
- `description` 非常重要，AI 会根据它来判断何时调用这个工具
- `parameters` 使用 Zod 进行参数验证，确保类型安全
- `execute` 函数返回字符串，通常是 JSON 格式

**3. 启动服务器**

```typescript
// STDIO 模式（本地开发）
server.start({
  transportType: 'stdio'
});

// 或 HTTP 模式（远程部署）
server.start({
  transportType: 'httpStream',
  httpStream: {
    port: 8000
  }
});
```

### 完整示例

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import { z } from 'zod';

const server = new FastMCP({
  name: 'Claude Stats MCP',
  version: '1.0.0',
});

// 工具1：查询今日统计
server.addTool({
  name: 'query_today_stats',
  description: '查询今日所有账号的使用统计，包括费用、请求数等',
  parameters: z.object({
    forceRefresh: z.boolean().optional().describe('是否强制刷新缓存')
  }),
  execute: async (args) => {
    const stats = await getDailyStats(args.forceRefresh);
    return JSON.stringify(stats, null, 2);
  }
});

// 工具2：查询特定用户
server.addTool({
  name: 'query_user_stats',
  description: '查询特定用户的统计数据',
  parameters: z.object({
    userName: z.string().describe('用户名称'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期')
  }),
  execute: async (args) => {
    const user = await findUser(args.userName, args.period);
    return JSON.stringify(user, null, 2);
  }
});

// 启动服务器
server.start({ transportType: 'stdio' });
```

### 数据流程图

当用户向 AI 提问时，整个调用流程如下：

```
┌─────────────────────────────────────────────────────────────────┐
│  用户提问："今天使用率最高的是谁？"                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI 分析意图，决定调用 query_top_users 工具                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Client 发送请求到 MCP Server                                │
│  { "method": "tools/call", "params": { "name": "query_top_users" }}
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server 执行 execute 函数                                    │
│  → 调用 API 获取数据                                             │
│  → 处理数据                                                      │
│  → 返回 JSON 结果                                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI 将 JSON 结果转换为自然语言回复用户                            │
│  "今天使用率最高的是张三，费用 $12.50，请求数 350 次"              │
└─────────────────────────────────────────────────────────────────┘
```

### 与 Agent 交互

MCP 工具的 `description` 字段是与 AI Agent 交互的关键：

```typescript
// 好的描述 - AI 能准确理解何时调用
server.addTool({
  name: 'search_user',
  description: '在数据库中搜索用户信息。支持按姓名、邮箱、ID搜索。返回匹配的用户列表。',
  // ...
});

// 不好的描述 - AI 可能会误判
server.addTool({
  name: 'search',
  description: '搜索',  // 太模糊，AI 不知道搜索什么
  // ...
});
```

---

## 六、NPX 发布流程

开发完成后，可以发布到 npm，让其他用户通过 `npx` 直接使用。

### 1. 配置 package.json

```json
{
  "name": "claude-stats-mcp",
  "version": "1.0.0",
  "description": "MCP 服务器用于查询 Claude Code 使用统计",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "claude-stats-mcp": "./dist/index.js"
  },
  "files": [
    "dist",
    "README.md"
  ],
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  }
}
```

**关键配置：**
- `bin`：定义命令行工具名称
- `files`：指定发布时包含的文件
- `prepublishOnly`：发布前自动构建

### 2. 添加 Shebang

确保入口文件第一行有 shebang：

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
// ...
```

### 3. 发布到 npm

```bash
# 登录 npm
npm login

# 构建项目
npm run build

# 发布
npm publish
```

### 4. 用户使用

发布后，用户可以直接使用：

```bash
# 无需安装，直接运行
npx claude-stats-mcp

# 或全局安装
npm install -g claude-stats-mcp
claude-stats-mcp
```

---

## 七、HTTPS 发布简要流程

如果需要远程访问，可以通过 HTTPS 方式部署。

### 1. 启动 HTTP 模式

```bash
# 通过环境变量启动
MCP_TRANSPORT=http MCP_PORT=8000 npm start
```

服务将运行在 `http://localhost:8000/mcp`

### 2. Nginx 反向代理

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location /mcp {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 3. 获取 SSL 证书

```bash
# 使用 Let's Encrypt 免费证书
sudo certbot --nginx -d your-domain.com
```

配置完成后，在 Cursor 中使用 `https://your-domain.com/mcp` 即可访问。

---

## 八、Python Demo 简介

FastMCP 同样支持 Python，使用装饰器语法更加简洁。

### 核心代码

```python
#!/usr/bin/env python3
from fastmcp import FastMCP

# 创建 MCP 实例
mcp = FastMCP(
    name="Claude Stats MCP",
    instructions="用于查询 Claude Code 使用统计的 MCP 服务器"
)

# 使用装饰器定义工具
@mcp.tool()
async def query_today_stats(force_refresh: bool = False) -> str:
    """
    查询今日所有账号的使用统计

    Args:
        force_refresh: 是否强制刷新缓存数据

    Returns:
        JSON 格式的统计数据
    """
    stats = await get_daily_stats(force_refresh)
    return json.dumps(stats, ensure_ascii=False, indent=2)

@mcp.tool()
async def query_user_stats(user_name: str, period: str = 'daily') -> str:
    """查询特定用户的统计数据"""
    user = await find_user(user_name, period)
    return json.dumps(user, ensure_ascii=False, indent=2)

# 启动服务器
if __name__ == "__main__":
    mcp.run(transport='stdio')  # 或 transport='http', port=8000
```

### Node.js vs Python 对比

| 特性 | Node.js (TypeScript) | Python |
|-----|---------------------|--------|
| 工具定义 | `server.addTool({...})` | `@mcp.tool()` 装饰器 |
| 参数验证 | Zod | 类型注解 + docstring |
| 异步支持 | async/await | async/await |
| 启动方式 | `server.start({...})` | `mcp.run(...)` |

两者功能完全相同，选择哪个取决于你的技术栈偏好。

---

## 九、MCP 其他应用场景

MCP 的应用场景非常广泛，以下是一些典型例子：

- **数据库查询**：让 AI 直接查询 MySQL、PostgreSQL、MongoDB
- **文件系统操作**：读写本地文件、管理文档
- **第三方 API 集成**：GitHub、Jira、Notion、飞书
- **自动化工作流**：CI/CD 触发、定时任务管理
- **代码分析**：静态分析、依赖检查、安全扫描
- **监控告警**：服务器状态、日志分析、异常检测

社区已经开发了超过 **一万种** MCP Server，覆盖各种场景。

---

## 十、MCP 发展形势与总结

### 行业采纳

MCP 正在快速成为 AI 工具集成的行业标准：

- **2024年11月**：Anthropic 发布 MCP 协议
- **2025年3月**：OpenAI 正式采纳 MCP，集成到 ChatGPT 桌面版和 Agents SDK
- **2025年4月**：Google DeepMind CEO 确认 Gemini 将支持 MCP
- **2025年6月**：MCP 规范更新，完善授权机制（Auth0 参与）

### 社区热度

今年以来，AI 开发社区掀起了一场 **"MCP 淘金热"**：

- 短短三个月内，数千个工具接入 MCP 协议
- MCP Server 数量超过一万种
- 被称为 AI 基础设施领域的"现象级事件"

### 理性看待

社区也有理性的声音：

> "MCP 不是万能钥匙，更像是专业扳手——在某些场景下表现出色，在其他场合却显得水土不服。"

**当前挑战：**
- 生态成熟度仍在发展中
- 网络传输的标准化支持还不完善
- 工具选择的 UI/UX 模式尚未统一

### 未来趋势

- **标准化**：更多大厂采纳，协议更加完善
- **安全性**：授权机制、数据隔离更加成熟
- **行业定制**：针对特定领域的专业解决方案

---

## 参考资源

**官方资源：**
- MCP 官网：https://modelcontextprotocol.io/
- MCP GitHub：https://github.com/modelcontextprotocol
- Anthropic 公告：https://www.anthropic.com/news/model-context-protocol

**框架文档：**
- FastMCP TypeScript：https://github.com/punkpeye/fastmcp
- FastMCP Python：https://github.com/jlowin/fastmcp

**学习教程：**
- DataCamp 教程：https://www.datacamp.com/tutorial/mcp-model-context-protocol
- DEV 社区完整指南：https://dev.to/krlz/the-complete-guide-to-model-context-protocol-mcp-connect-ai-to-everything-in-2025-52g0
- 知乎深入研究报告：https://zhuanlan.zhihu.com/p/1890070269206434486

**社区讨论：**
- 腾讯新闻 - MCP 是 AI 智能体的"万能插头"吗：https://news.qq.com/rain/a/20250325A04HJD00
- 阿里云 - 十大开源 MCP 服务器：https://developer.aliyun.com/article/1661309

---

> 本文基于项目 `ai-mcp-study` 实战总结，包含 Node.js 和 Python 两个完整 Demo。

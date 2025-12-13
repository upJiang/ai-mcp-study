# 示例：数据库查询 MCP 工具

本示例展示如何创建一个完整的数据库查询 MCP 工具。

## 场景说明

**需求**：创建一个 MCP 工具，用于查询公司的 MySQL 订单数据库。

**功能**：
- 查询订单列表
- 查询订单详情
- 统计订单数量
- 支持按日期范围筛选

---

## 第 1 步：告诉 AI 你的需求

在 Cursor/Claude Code 中输入：

```
创建一个 MCP 项目，用于查询公司的订单数据库：

项目信息：
- 项目名：@mycompany/order-query-mcp
- 功能：查询 MySQL 订单数据库
- 作者：张三 <zhangsan@company.com>
- 命令名：order-query

需要的工具：
1. query_orders - 查询订单列表
   - 支持按日期范围筛选
   - 支持分页
   - 返回订单基本信息

2. get_order_detail - 查询订单详情
   - 输入：订单ID
   - 返回：完整订单信息（包括商品明细）

3. count_orders - 统计订单数量
   - 支持按状态统计
   - 支持按日期范围统计

数据库连接信息存放在配置文件中。
```

---

## 第 2 步：AI 生成的项目结构

```
order-query-mcp/
├── src/
│   ├── index.ts
│   ├── tools/
│   │   ├── queryOrders.ts
│   │   ├── getOrderDetail.ts
│   │   └── countOrders.ts
│   └── utils/
│       └── config.ts
├── config/
│   └── example.database.json
├── package.json
├── tsconfig.json
├── .gitignore
├── .env.example
└── README.md
```

---

## 第 3 步：生成的代码示例

### package.json

```json
{
  "name": "@mycompany/order-query-mcp",
  "version": "1.0.0",
  "description": "MCP tool for querying company order database",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "bin": {
    "order-query": "./dist/index.js"
  },
  "files": ["dist"],
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["mcp", "fastmcp", "database", "mysql", "orders"],
  "author": "张三 <zhangsan@company.com>",
  "license": "MIT",
  "dependencies": {
    "dotenv": "^17.2.3",
    "fastmcp": "^3.25.3",
    "mysql2": "^3.6.0",
    "zod": "^4.1.13"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.3"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### config/example.database.json

```json
{
  "host": "localhost",
  "port": 3306,
  "user": "your_database_user",
  "password": "your_database_password",
  "database": "orders_db"
}
```

### src/tools/queryOrders.ts

```typescript
import mysql from 'mysql2/promise';
import { loadConfig } from '../utils/config.js';
import { z } from 'zod';

interface DatabaseConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
}

export const queryOrdersTool = {
  name: 'query_orders',
  description: '查询订单列表，支持按日期范围和分页查询',

  parameters: z.object({
    startDate: z.string().optional().describe('开始日期 (YYYY-MM-DD)'),
    endDate: z.string().optional().describe('结束日期 (YYYY-MM-DD)'),
    status: z.string().optional().describe('订单状态（pending, completed, cancelled）'),
    limit: z.number().optional().describe('返回数量限制，默认 10'),
    offset: z.number().optional().describe('偏移量，默认 0')
  }),

  execute: async (args: {
    startDate?: string;
    endDate?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) => {
    let connection: mysql.Connection | null = null;

    try {
      // 加载数据库配置
      const config = loadConfig<DatabaseConfig>('./config/database.json');
      connection = await mysql.createConnection(config);

      // 构建 SQL 查询
      let sql = 'SELECT * FROM orders WHERE 1=1';
      const params: any[] = [];

      if (args.startDate) {
        sql += ' AND order_date >= ?';
        params.push(args.startDate);
      }

      if (args.endDate) {
        sql += ' AND order_date <= ?';
        params.push(args.endDate);
      }

      if (args.status) {
        sql += ' AND status = ?';
        params.push(args.status);
      }

      sql += ' ORDER BY order_date DESC LIMIT ? OFFSET ?';
      params.push(args.limit || 10);
      params.push(args.offset || 0);

      // 执行查询
      const [rows] = await connection.execute(sql, params);

      return JSON.stringify({
        success: true,
        data: rows,
        count: Array.isArray(rows) ? rows.length : 0
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] query_orders:', error);

      return JSON.stringify({
        success: false,
        error: error.message,
        code: error.code,
        suggestion: error.code === 'ENOENT'
          ? '请先创建配置文件 config/database.json'
          : '请检查数据库连接配置'
      }, null, 2);
    } finally {
      if (connection) await connection.end();
    }
  }
};
```

### src/tools/getOrderDetail.ts

```typescript
import mysql from 'mysql2/promise';
import { loadConfig } from '../utils/config.js';
import { z } from 'zod';

interface DatabaseConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
}

export const getOrderDetailTool = {
  name: 'get_order_detail',
  description: '根据订单ID查询订单完整信息，包括商品明细',

  parameters: z.object({
    orderId: z.string().describe('订单ID')
  }),

  execute: async (args: { orderId: string }) => {
    let connection: mysql.Connection | null = null;

    try {
      const config = loadConfig<DatabaseConfig>('./config/database.json');
      connection = await mysql.createConnection(config);

      // 查询订单基本信息
      const [orderRows] = await connection.execute(
        'SELECT * FROM orders WHERE order_id = ?',
        [args.orderId]
      );

      if (!Array.isArray(orderRows) || orderRows.length === 0) {
        throw new Error(`订单不存在: ${args.orderId}`);
      }

      const order = orderRows[0];

      // 查询订单商品明细
      const [itemRows] = await connection.execute(
        'SELECT * FROM order_items WHERE order_id = ?',
        [args.orderId]
      );

      return JSON.stringify({
        success: true,
        data: {
          order: order,
          items: itemRows
        }
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] get_order_detail:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    } finally {
      if (connection) await connection.end();
    }
  }
};
```

### src/tools/countOrders.ts

```typescript
import mysql from 'mysql2/promise';
import { loadConfig } from '../utils/config.js';
import { z } from 'zod';

interface DatabaseConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
}

export const countOrdersTool = {
  name: 'count_orders',
  description: '统计订单数量，支持按状态和日期范围统计',

  parameters: z.object({
    status: z.string().optional().describe('订单状态筛选'),
    startDate: z.string().optional().describe('开始日期 (YYYY-MM-DD)'),
    endDate: z.string().optional().describe('结束日期 (YYYY-MM-DD)')
  }),

  execute: async (args: {
    status?: string;
    startDate?: string;
    endDate?: string;
  }) => {
    let connection: mysql.Connection | null = null;

    try {
      const config = loadConfig<DatabaseConfig>('./config/database.json');
      connection = await mysql.createConnection(config);

      // 构建 SQL
      let sql = 'SELECT COUNT(*) as total FROM orders WHERE 1=1';
      const params: any[] = [];

      if (args.status) {
        sql += ' AND status = ?';
        params.push(args.status);
      }

      if (args.startDate) {
        sql += ' AND order_date >= ?';
        params.push(args.startDate);
      }

      if (args.endDate) {
        sql += ' AND order_date <= ?';
        params.push(args.endDate);
      }

      const [rows] = await connection.execute(sql, params);
      const total = Array.isArray(rows) && rows[0] ? (rows[0] as any).total : 0;

      return JSON.stringify({
        success: true,
        data: { total }
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] count_orders:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    } finally {
      if (connection) await connection.end();
    }
  }
};
```

### src/index.ts

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import * as dotenv from 'dotenv';
import { queryOrdersTool } from './tools/queryOrders.js';
import { getOrderDetailTool } from './tools/getOrderDetail.js';
import { countOrdersTool } from './tools/countOrders.js';

dotenv.config();

const server = new FastMCP({
  name: 'Order Query MCP',
  version: '1.0.0',
});

// 注册工具
server.addTool(queryOrdersTool);
server.addTool(getOrderDetailTool);
server.addTool(countOrdersTool);

// 启动服务器
const transport = process.env.MCP_TRANSPORT || 'stdio';

console.error('========================================');
console.error(`MCP Server: ${server.name}`);
console.error(`Transport: ${transport.toUpperCase()}`);
console.error('========================================');

server.start({ transportType: 'stdio' });

process.on('SIGINT', () => {
  console.error('\n正在关闭服务器...');
  process.exit(0);
});
```

---

## 第 4 步：配置和测试

### 4.1 安装依赖

```bash
npm install
```

### 4.2 配置数据库

```bash
# 复制配置文件模板
cp config/example.database.json config/database.json

# 编辑配置文件，填写真实数据库信息
vi config/database.json
```

### 4.3 测试运行

```bash
npm run dev
```

看到以下输出说明成功：

```
========================================
MCP Server: Order Query MCP
Transport: STDIO
========================================
```

---

## 第 5 步：在 Cursor 中使用

### 5.1 发布到 npm

```bash
./scripts/publish-npm.sh
```

### 5.2 配置 Cursor

在 Cursor 配置文件中添加：

```json
{
  "mcpServers": {
    "order-query": {
      "command": "npx",
      "args": ["-y", "@mycompany/order-query-mcp"]
    }
  }
}
```

### 5.3 测试使用

在 Cursor 中对话：

```
查询最近 7 天的已完成订单，返回前 10 条
```

AI 会自动调用 `query_orders` 工具：

```json
{
  "startDate": "2024-01-15",
  "endDate": "2024-01-22",
  "status": "completed",
  "limit": 10
}
```

---

## 常见问题

### Q1: 数据库连接失败？

**A**: 检查 `config/database.json` 配置是否正确，特别是：
- host 和 port
- 用户名和密码
- 数据库名称
- 网络连接

### Q2: 查询结果为空？

**A**: 检查：
- 表名是否正确（`orders`, `order_items`）
- 字段名是否匹配
- 数据库中是否有数据

### Q3: 如何添加更多查询功能？

**A**: 告诉 AI：

```
添加一个新工具 search_orders，支持按客户名称、商品名称搜索订单
```

AI 会自动生成新的工具代码。

---

## 总结

这个示例展示了：
- ✅ 如何创建数据库查询 MCP 工具
- ✅ 如何处理多个相关工具
- ✅ 如何使用配置文件
- ✅ 如何实现参数化查询（防止 SQL 注入）
- ✅ 如何在 Cursor 中使用

**下一步**：参考这个示例创建你自己的数据库查询工具！

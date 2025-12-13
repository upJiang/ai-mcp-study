# MCP 工具模板库

本文档提供各种常见场景的 MCP 工具模板，AI 可以参考这些模板快速生成代码。

---

## 目录

1. [基础模板](#基础模板)
2. [数据库操作](#数据库操作)
3. [API 调用](#api-调用)
4. [文件操作](#文件操作)
5. [数据处理](#数据处理)
6. [外部服务集成](#外部服务集成)

---

## 基础模板

### 最简单的工具

```typescript
import { z } from 'zod';

export const simpleToolTool = {
  name: 'simple_tool',
  description: '一个简单的示例工具，返回问候信息',

  parameters: z.object({
    name: z.string().describe('要问候的名字')
  }),

  execute: async (args: { name: string }) => {
    try {
      const result = `Hello, ${args.name}!`;

      return JSON.stringify({
        success: true,
        data: result
      }, null, 2);
    } catch (error: any) {
      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

---

## 数据库操作

### MySQL 查询

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

export const queryMySQLTool = {
  name: 'query_mysql',
  description: '查询 MySQL 数据库，仅支持 SELECT 语句',

  parameters: z.object({
    sql: z.string().describe('SQL 查询语句'),
    params: z.array(z.any()).optional().describe('SQL 参数（防止注入）')
  }),

  execute: async (args: { sql: string; params?: any[] }) => {
    let connection: mysql.Connection | null = null;

    try {
      // 安全检查
      if (!args.sql.trim().toLowerCase().startsWith('select')) {
        throw new Error('仅支持 SELECT 查询');
      }

      const config = loadConfig<DatabaseConfig>('./config/database.json');
      connection = await mysql.createConnection(config);

      const [rows] = await connection.execute(args.sql, args.params || []);

      return JSON.stringify({
        success: true,
        data: rows,
        count: Array.isArray(rows) ? rows.length : 0
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] query_mysql:', error);

      return JSON.stringify({
        success: false,
        error: error.message,
        suggestion: '请检查 SQL 语句和数据库连接'
      }, null, 2);
    } finally {
      if (connection) await connection.end();
    }
  }
};
```

### PostgreSQL 查询

```typescript
import pg from 'pg';
import { loadConfig } from '../utils/config.js';
import { z } from 'zod';

const { Pool } = pg;

interface PostgresConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
}

export const queryPostgresTool = {
  name: 'query_postgres',
  description: '查询 PostgreSQL 数据库',

  parameters: z.object({
    sql: z.string().describe('SQL 查询语句'),
    params: z.array(z.any()).optional().describe('SQL 参数')
  }),

  execute: async (args: { sql: string; params?: any[] }) => {
    const config = loadConfig<PostgresConfig>('./config/database.json');
    const pool = new Pool(config);

    try {
      const result = await pool.query(args.sql, args.params || []);

      return JSON.stringify({
        success: true,
        data: result.rows,
        count: result.rowCount
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] query_postgres:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    } finally {
      await pool.end();
    }
  }
};
```

### MongoDB 查询

```typescript
import { MongoClient } from 'mongodb';
import { loadConfig } from '../utils/config.js';
import { z } from 'zod';

interface MongoConfig {
  url: string;
  database: string;
}

export const queryMongoTool = {
  name: 'query_mongo',
  description: '查询 MongoDB 数据库',

  parameters: z.object({
    collection: z.string().describe('集合名称'),
    query: z.record(z.any()).describe('查询条件（JSON 对象）'),
    limit: z.number().optional().describe('返回数量限制')
  }),

  execute: async (args: { collection: string; query: Record<string, any>; limit?: number }) => {
    const config = loadConfig<MongoConfig>('./config/database.json');
    const client = new MongoClient(config.url);

    try {
      await client.connect();
      const db = client.db(config.database);
      const collection = db.collection(args.collection);

      const cursor = collection.find(args.query);
      if (args.limit) cursor.limit(args.limit);

      const results = await cursor.toArray();

      return JSON.stringify({
        success: true,
        data: results,
        count: results.length
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] query_mongo:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    } finally {
      await client.close();
    }
  }
};
```

---

## API 调用

### GET 请求

```typescript
import { z } from 'zod';

export const fetchApiTool = {
  name: 'fetch_api',
  description: '调用 GET API 并返回结果',

  parameters: z.object({
    url: z.string().describe('API URL'),
    headers: z.record(z.string()).optional().describe('请求头（可选）')
  }),

  execute: async (args: { url: string; headers?: Record<string, string> }) => {
    try {
      const response = await fetch(args.url, {
        method: 'GET',
        headers: args.headers || {}
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      return JSON.stringify({
        success: true,
        data: data
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] fetch_api:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### POST 请求（带认证）

```typescript
import { z } from 'zod';

export const postApiTool = {
  name: 'post_api',
  description: '调用 POST API，支持 Bearer Token 认证',

  parameters: z.object({
    url: z.string().describe('API URL'),
    body: z.record(z.any()).describe('请求体（JSON 对象）'),
    token: z.string().optional().describe('Bearer Token（可选）')
  }),

  execute: async (args: { url: string; body: Record<string, any>; token?: string }) => {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };

      if (args.token) {
        headers['Authorization'] = `Bearer ${args.token}`;
      }

      const response = await fetch(args.url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(args.body)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      return JSON.stringify({
        success: true,
        data: data
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] post_api:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### 带缓存的 API 调用

```typescript
import { z } from 'zod';
import { SimpleCache } from '../utils/cache.js';

const cache = new SimpleCache<any>();

export const cachedApiTool = {
  name: 'cached_api',
  description: '调用 API 并缓存结果，减少重复请求',

  parameters: z.object({
    url: z.string().describe('API URL'),
    cacheDuration: z.number().optional().describe('缓存时长（毫秒），默认 5 分钟')
  }),

  execute: async (args: { url: string; cacheDuration?: number }) => {
    const cacheKey = `api_${args.url}`;
    const duration = args.cacheDuration || 5 * 60 * 1000; // 默认 5 分钟

    try {
      // 尝试从缓存获取
      const cached = cache.get(cacheKey);
      if (cached) {
        return JSON.stringify({
          success: true,
          data: cached,
          fromCache: true
        }, null, 2);
      }

      // 调用 API
      const response = await fetch(args.url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // 存入缓存
      cache.set(cacheKey, data, duration);

      return JSON.stringify({
        success: true,
        data: data,
        fromCache: false
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] cached_api:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

---

## 文件操作

### 读取文件

```typescript
import fs from 'fs/promises';
import path from 'path';
import { z } from 'zod';

export const readFileTool = {
  name: 'read_file',
  description: '读取文件内容',

  parameters: z.object({
    filePath: z.string().describe('文件路径'),
    encoding: z.enum(['utf8', 'base64']).optional().describe('编码方式，默认 utf8')
  }),

  execute: async (args: { filePath: string; encoding?: 'utf8' | 'base64' }) => {
    try {
      const absolutePath = path.resolve(args.filePath);

      // 安全检查：确保文件存在
      await fs.access(absolutePath);

      const encoding = args.encoding || 'utf8';
      const content = await fs.readFile(absolutePath, encoding as BufferEncoding);

      return JSON.stringify({
        success: true,
        data: {
          content: content,
          path: absolutePath,
          encoding: encoding
        }
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] read_file:', error);

      return JSON.stringify({
        success: false,
        error: error.message,
        suggestion: error.code === 'ENOENT' ? '文件不存在' : '请检查文件路径和权限'
      }, null, 2);
    }
  }
};
```

### 搜索文件

```typescript
import fs from 'fs';
import path from 'path';
import { z } from 'zod';

export const searchFilesTool = {
  name: 'search_files',
  description: '在目录中搜索包含关键词的文件',

  parameters: z.object({
    directory: z.string().describe('搜索目录'),
    keyword: z.string().describe('搜索关键词'),
    fileExtension: z.string().optional().describe('文件扩展名过滤（如 .ts）'),
    maxResults: z.number().optional().describe('最大结果数，默认 10')
  }),

  execute: async (args: {
    directory: string;
    keyword: string;
    fileExtension?: string;
    maxResults?: number;
  }) => {
    try {
      const absolutePath = path.resolve(args.directory);
      const maxResults = args.maxResults || 10;
      const results: Array<{ file: string; line: number; content: string }> = [];

      function searchDir(dir: string) {
        if (results.length >= maxResults) return;

        const files = fs.readdirSync(dir);

        for (const file of files) {
          if (results.length >= maxResults) break;

          const filePath = path.join(dir, file);
          const stat = fs.statSync(filePath);

          if (stat.isDirectory()) {
            searchDir(filePath);
          } else if (stat.isFile()) {
            // 检查扩展名
            if (args.fileExtension && !filePath.endsWith(args.fileExtension)) {
              continue;
            }

            // 搜索内容
            try {
              const content = fs.readFileSync(filePath, 'utf8');
              const lines = content.split('\n');

              lines.forEach((line, index) => {
                if (results.length >= maxResults) return;
                if (line.includes(args.keyword)) {
                  results.push({
                    file: path.relative(absolutePath, filePath),
                    line: index + 1,
                    content: line.trim()
                  });
                }
              });
            } catch (e) {
              // 跳过无法读取的文件
            }
          }
        }
      }

      searchDir(absolutePath);

      return JSON.stringify({
        success: true,
        data: results,
        count: results.length
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] search_files:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

---

## 数据处理

### JSON 数据转换

```typescript
import { z } from 'zod';

export const transformJsonTool = {
  name: 'transform_json',
  description: '转换 JSON 数据格式',

  parameters: z.object({
    data: z.record(z.any()).describe('要转换的 JSON 数据'),
    mappings: z.record(z.string()).describe('字段映射关系，如 {"oldKey": "newKey"}')
  }),

  execute: async (args: {
    data: Record<string, any>;
    mappings: Record<string, string>;
  }) => {
    try {
      const result: Record<string, any> = {};

      for (const [oldKey, newKey] of Object.entries(args.mappings)) {
        if (oldKey in args.data) {
          result[newKey] = args.data[oldKey];
        }
      }

      return JSON.stringify({
        success: true,
        data: result
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] transform_json:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### CSV 解析

```typescript
import { parse } from 'csv-parse/sync';
import { z } from 'zod';

export const parseCsvTool = {
  name: 'parse_csv',
  description: '解析 CSV 数据为 JSON',

  parameters: z.object({
    csv: z.string().describe('CSV 字符串'),
    hasHeader: z.boolean().optional().describe('是否有表头，默认 true')
  }),

  execute: async (args: { csv: string; hasHeader?: boolean }) => {
    try {
      const records = parse(args.csv, {
        columns: args.hasHeader !== false,
        skip_empty_lines: true
      });

      return JSON.stringify({
        success: true,
        data: records,
        count: records.length
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] parse_csv:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

---

## 外部服务集成

### 发送邮件（Nodemailer）

```typescript
import nodemailer from 'nodemailer';
import { z } from 'zod';

export const sendEmailTool = {
  name: 'send_email',
  description: '发送邮件',

  parameters: z.object({
    to: z.string().describe('收件人邮箱'),
    subject: z.string().describe('邮件主题'),
    text: z.string().describe('邮件正文（纯文本）'),
    html: z.string().optional().describe('邮件正文（HTML）')
  }),

  execute: async (args: {
    to: string;
    subject: string;
    text: string;
    html?: string;
  }) => {
    try {
      const transporter = nodemailer.createTransporter({
        host: process.env.SMTP_HOST,
        port: parseInt(process.env.SMTP_PORT || '587'),
        secure: false,
        auth: {
          user: process.env.SMTP_USER,
          pass: process.env.SMTP_PASS
        }
      });

      const info = await transporter.sendMail({
        from: process.env.SMTP_FROM,
        to: args.to,
        subject: args.subject,
        text: args.text,
        html: args.html
      });

      return JSON.stringify({
        success: true,
        data: {
          messageId: info.messageId,
          to: args.to
        }
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] send_email:', error);

      return JSON.stringify({
        success: false,
        error: error.message,
        suggestion: '请检查 SMTP 配置和网络连接'
      }, null, 2);
    }
  }
};
```

### Slack 通知

```typescript
import { z } from 'zod';

export const sendSlackTool = {
  name: 'send_slack',
  description: '发送 Slack 消息',

  parameters: z.object({
    channel: z.string().describe('频道名称（如 #general）'),
    text: z.string().describe('消息内容')
  }),

  execute: async (args: { channel: string; text: string }) => {
    try {
      const webhookUrl = process.env.SLACK_WEBHOOK_URL;
      if (!webhookUrl) {
        throw new Error('未配置 SLACK_WEBHOOK_URL');
      }

      const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel: args.channel,
          text: args.text
        })
      });

      if (!response.ok) {
        throw new Error(`Slack API 错误: ${response.statusText}`);
      }

      return JSON.stringify({
        success: true,
        data: { sent: true }
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] send_slack:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

---

## 使用说明

### 如何使用这些模板

1. **选择合适的模板**：根据需求选择最接近的模板
2. **复制代码**：复制到 `src/tools/` 目录
3. **修改参数**：根据实际需求调整参数定义
4. **实现业务逻辑**：在 `execute` 函数中实现具体逻辑
5. **注册工具**：在 `src/index.ts` 中注册工具

### 模板组合

可以组合多个模板创建复杂功能，例如：

- **数据库 + 邮件**：查询数据后发送报表邮件
- **API + 缓存**：调用外部 API 并缓存结果
- **文件 + 数据处理**：读取 CSV 并导入数据库

### 最佳实践

1. **错误处理**：所有模板都包含完整的错误处理
2. **参数验证**：使用 Zod 进行严格的类型检查
3. **安全性**：敏感信息使用环境变量
4. **日志记录**：使用 `console.error()` 记录错误
5. **资源清理**：及时关闭数据库连接、文件句柄等

---

**提示**：这些模板仅供参考，实际使用时应根据具体需求进行调整。

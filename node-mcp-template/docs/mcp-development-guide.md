# MCP 开发完整指南（AI 参考）

## 概述

本文档用于指导 AI 生成符合规范的 MCP (Model Context Protocol) 代码。

**目标读者**：AI 助手（Cursor、Claude Code 等）

**使用场景**：当用户请求创建 MCP 项目或添加工具时，AI 应参考此文档生成代码。

---

## 核心原则

1. **开箱即用**：生成的代码必须无需修改即可运行
2. **类型安全**：使用 TypeScript 和 Zod 确保类型安全
3. **错误处理**：所有异步操作必须有 try-catch
4. **标准化**：遵循统一的命名和结构规范
5. **简洁性**：避免过度工程，只实现所需功能

---

## 项目初始化

### 当用户请求"创建 MCP 项目"时

#### 第 1 步：询问项目信息

必须询问以下信息：
1. **项目名称**（用于 package.json 的 name）
2. **功能描述**（用于 description）
3. **作者信息**（用于 author）
4. **bin 命令名**（用于可执行命令）
5. **需要哪些工具/功能**

示例对话：
```
AI: 我需要一些信息来创建项目：
1. 项目名称是什么？（例如：@mycompany/database-mcp）
2. 简短描述项目功能？
3. 作者信息？（姓名 <邮箱>）
4. 希望的命令名？（例如：db-query）
5. 需要哪些具体功能？
```

#### 第 2 步：生成目录结构

```
项目名/
├── src/
│   ├── index.ts           # 入口文件
│   ├── tools/             # 工具目录
│   │   └── [功能].ts      # 具体工具
│   └── utils/            # 工具类
│       ├── config.ts      # 配置加载
│       └── cache.ts       # 缓存（可选）
├── config/               # 配置文件目录
│   └── example.*.json    # 配置模板
├── package.json
├── tsconfig.json
├── .gitignore
├── .env.example          # 环境变量模板
└── README.md
```

#### 第 3 步：生成 package.json

```json
{
  "name": "@组织/项目名",
  "version": "1.0.0",
  "description": "根据用户需求填写",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "bin": {
    "命令名": "./dist/index.js"
  },
  "files": ["dist"],
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["mcp", "fastmcp", "相关关键词"],
  "author": "用户名 <邮箱>",
  "license": "MIT",
  "dependencies": {
    "dotenv": "^17.2.3",
    "fastmcp": "^3.25.3",
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

**注意**：
- 根据功能需求添加额外依赖（如 `mysql2`, `axios` 等）
- 确保 `name` 字段全网唯一
- `type: "module"` 是必需的（使用 ES Modules）

#### 第 4 步：生成 tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "node",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

#### 第 5 步：生成 .gitignore

```gitignore
# Node
node_modules/
dist/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 环境变量
.env
.env.*
!.env.example

# 配置文件
config/*.json
!config/example.*.json

# 系统文件
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
```

#### 第 6 步：生成 src/index.ts

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import * as dotenv from 'dotenv';
// 导入工具
// import { toolName } from './tools/toolName.js';

// 加载环境变量
dotenv.config();

// 创建 FastMCP 服务器
const server = new FastMCP({
  name: process.env.MCP_NAME || 'MCP Server Name',
  version: '1.0.0',
});

// 注册工具
// server.addTool(toolName);

// 启动服务器
const transport = process.env.MCP_TRANSPORT || 'stdio';
const port = parseInt(process.env.MCP_PORT || '3000', 10);

console.error('========================================');
console.error(`MCP Server: ${server.name}`);
console.error(`Transport: ${transport.toUpperCase()}`);
console.error('========================================');

if (transport === 'httpStream') {
  console.error(`Port: ${port}`);
  server.start({
    transportType: 'httpStream',
    httpStream: { port }
  });
} else {
  server.start({
    transportType: 'stdio'
  });
}

// 优雅退出
process.on('SIGINT', () => {
  console.error('\n正在关闭服务器...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('\n正在关闭服务器...');
  process.exit(0);
});
```

**关键点**：
- 第一行必须是 `#!/usr/bin/env node`
- 所有导入必须使用 `.js` 扩展名（ES Modules 规范）
- 使用 `console.error()` 输出日志（stdout 用于 MCP 通信）

#### 第 7 步：生成工具类

**src/utils/config.ts**:

```typescript
import fs from 'fs';
import path from 'path';

/**
 * 加载 JSON 配置文件
 * @param configPath 配置文件路径（相对或绝对）
 * @returns 配置对象
 */
export function loadConfig<T = any>(configPath: string): T {
  try {
    const absolutePath = path.resolve(configPath);

    if (!fs.existsSync(absolutePath)) {
      throw new Error(`配置文件不存在: ${absolutePath}`);
    }

    const data = fs.readFileSync(absolutePath, 'utf8');
    return JSON.parse(data) as T;
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      throw new Error(`配置文件不存在: ${configPath}`);
    } else if (error instanceof SyntaxError) {
      throw new Error(`配置文件 JSON 格式错误: ${error.message}`);
    } else {
      throw new Error(`加载配置失败: ${error.message}`);
    }
  }
}

/**
 * 加载可选配置（文件不存在时返回默认值）
 */
export function loadConfigOptional<T>(configPath: string, defaultConfig: T): T {
  try {
    return loadConfig<T>(configPath);
  } catch (error) {
    return defaultConfig;
  }
}
```

**src/utils/cache.ts** (可选):

```typescript
/**
 * 简单的内存缓存
 */
export class SimpleCache<T> {
  private cache: Map<string, { value: T; expireAt: number }> = new Map();

  /**
   * 设置缓存
   * @param key 缓存键
   * @param value 缓存值
   * @param ttl 过期时间（毫秒）
   */
  set(key: string, value: T, ttl: number = 60000): void {
    const expireAt = Date.now() + ttl;
    this.cache.set(key, { value, expireAt });
  }

  /**
   * 获取缓存
   * @param key 缓存键
   * @returns 缓存值或 undefined
   */
  get(key: string): T | undefined {
    const item = this.cache.get(key);
    if (!item) return undefined;

    if (Date.now() > item.expireAt) {
      this.cache.delete(key);
      return undefined;
    }

    return item.value;
  }

  /**
   * 清除缓存
   * @param key 缓存键（不传则清除所有）
   */
  clear(key?: string): void {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }
}
```

#### 第 8 步：提示用户

```
✅ MCP 项目创建成功！

下一步：
1. 运行 `npm install` 安装依赖
2. 添加你的工具到 `src/tools/`
3. 在 `src/index.ts` 中注册工具
4. 运行 `npm run dev` 测试

提示：告诉我你需要什么功能，我会帮你生成工具代码！
```

---

## 工具定义规范

### 工具的 4 个必需部分

每个 MCP 工具**必须**包含以下 4 个部分：

#### 1. name (必需)

- **格式**：`snake_case`
- **要求**：简短、描述性、唯一
- **示例**：
  - ✅ `query_database`
  - ✅ `send_email`
  - ✅ `analyze_data`
  - ❌ `queryDatabase`（不是 snake_case）
  - ❌ `read-file`（使用了连字符）

#### 2. description (必需)

- **作用**：AI 根据此描述决定是否调用工具
- **要求**：
  - 清晰说明功能
  - 说明使用场景
  - 说明限制条件
- **示例**：
  ```typescript
  description: '查询 MySQL 数据库并返回结果，支持 SELECT 语句，用于获取订单、用户等数据'
  ```

#### 3. parameters (必需)

- **格式**：Zod schema
- **要求**：
  - 使用 `z.object({...})` 定义
  - 每个参数必须有 `.describe()` 说明
  - 区分必需和可选参数
- **示例**：
  ```typescript
  import { z } from 'zod';

  parameters: z.object({
    query: z.string().describe('SQL 查询语句'),
    limit: z.number().optional().describe('返回结果数量限制'),
    offset: z.number().optional().describe('结果偏移量')
  })
  ```

#### 4. execute (必需)

- **格式**：async 函数
- **要求**：
  - 必须是 `async` 函数
  - 必须返回 `JSON.stringify()` 格式的字符串
  - 必须包含 `try-catch` 错误处理
  - 返回结构化数据（`{ success, data, error }` 格式）
- **示例**：
  ```typescript
  execute: async (args: { query: string; limit?: number }) => {
    try {
      // 业务逻辑
      const result = await doSomething(args);

      return JSON.stringify({
        success: true,
        data: result
      }, null, 2);
    } catch (error: any) {
      console.error(`[ERROR] 工具执行失败:`, error);

      return JSON.stringify({
        success: false,
        error: error.message,
        code: error.code || 'UNKNOWN_ERROR'
      }, null, 2);
    }
  }
  ```

### 完整工具模板

```typescript
import { z } from 'zod';

export const toolName = {
  name: 'tool_name',
  description: '详细描述工具功能，AI 会根据这个描述决定是否调用此工具',

  parameters: z.object({
    param1: z.string().describe('参数1的说明'),
    param2: z.number().optional().describe('可选参数2的说明'),
  }),

  execute: async (args: { param1: string; param2?: number }) => {
    try {
      // 参数验证（可选，Zod 已验证基本类型）
      if (args.param1.length === 0) {
        throw new Error('param1 不能为空');
      }

      // 业务逻辑
      const result = await performOperation(args);

      // 返回成功结果
      return JSON.stringify({
        success: true,
        data: result,
        message: '操作成功'
      }, null, 2);
    } catch (error: any) {
      // 错误日志
      console.error(`[ERROR] ${toolName.name} 执行失败:`, error);

      // 返回错误信息
      return JSON.stringify({
        success: false,
        error: error.message,
        code: error.code || 'UNKNOWN_ERROR',
        suggestion: '请检查输入参数是否正确'
      }, null, 2);
    }
  }
};
```

---

## 常见场景实现

### 场景 1：数据库查询工具

**用户需求**：创建查询数据库的工具

**AI 应询问**：
1. 数据库类型（MySQL/PostgreSQL/MongoDB/SQLite）
2. 连接方式（配置文件/环境变量）
3. 允许的操作（仅查询/增删改查）

**生成步骤**：

#### 1. 添加依赖

在 `package.json` 添加：
```json
{
  "dependencies": {
    "mysql2": "^3.6.0"  // 或其他数据库驱动
  }
}
```

#### 2. 生成配置文件模板

`config/example.database.json`:
```json
{
  "host": "localhost",
  "port": 3306,
  "user": "root",
  "password": "your-password",
  "database": "your-database"
}
```

#### 3. 生成工具代码

`src/tools/queryDatabase.ts`:
```typescript
import mysql from 'mysql2/promise';
import { loadConfig } from '../utils/config.js';
import { z } from 'zod';

// 配置类型
interface DatabaseConfig {
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
}

export const queryDatabaseTool = {
  name: 'query_database',
  description: '查询 MySQL 数据库并返回结果，仅支持 SELECT 语句，用于获取订单、用户、产品等数据',

  parameters: z.object({
    sql: z.string().describe('SQL 查询语句（仅支持 SELECT）'),
    params: z.array(z.any()).optional().describe('SQL 参数数组，用于防止注入攻击')
  }),

  execute: async (args: { sql: string; params?: any[] }) => {
    let connection: mysql.Connection | null = null;

    try {
      // 安全检查：只允许 SELECT
      const trimmedSql = args.sql.trim().toLowerCase();
      if (!trimmedSql.startsWith('select')) {
        throw new Error('安全限制：仅支持 SELECT 查询');
      }

      // 加载数据库配置
      const config = loadConfig<DatabaseConfig>('./config/database.json');

      // 创建连接
      connection = await mysql.createConnection(config);

      // 执行查询
      const [rows] = await connection.execute(args.sql, args.params || []);

      // 返回结果
      return JSON.stringify({
        success: true,
        data: rows,
        count: Array.isArray(rows) ? rows.length : 0
      }, null, 2);
    } catch (error: any) {
      console.error(`[ERROR] query_database 失败:`, error);

      return JSON.stringify({
        success: false,
        error: error.message,
        code: error.code || 'DB_ERROR',
        suggestion: error.code === 'ENOENT'
          ? '请先创建配置文件 config/database.json'
          : '请检查 SQL 语句和数据库连接'
      }, null, 2);
    } finally {
      // 关闭连接
      if (connection) {
        await connection.end();
      }
    }
  }
};
```

#### 4. 注册工具

在 `src/index.ts` 添加：
```typescript
import { queryDatabaseTool } from './tools/queryDatabase.js';

server.addTool(queryDatabaseTool);
```

#### 5. 提示用户

```
✅ 数据库查询工具创建成功！

下一步：
1. 复制配置文件：
   cp config/example.database.json config/database.json

2. 编辑 config/database.json 填写真实数据库连接信息

3. 运行 npm install 安装 mysql2 依赖

4. 测试工具：npm run dev
```

### 场景 2：API 调用工具

**用户需求**：创建调用外部 API 的工具

**AI 应询问**：
1. API 端点 URL
2. 认证方式（API Key/Bearer Token/OAuth/无需认证）
3. 请求方法（GET/POST/PUT/DELETE）
4. 是否需要缓存

**生成步骤**：

#### 1. 生成工具代码

`src/tools/callApi.ts`:
```typescript
import { z } from 'zod';
import { SimpleCache } from '../utils/cache.js';

// 缓存实例（可选）
const cache = new SimpleCache<any>();

export const callApiTool = {
  name: 'call_weather_api',
  description: '调用天气 API 获取城市天气信息，支持缓存以减少 API 调用次数',

  parameters: z.object({
    city: z.string().describe('城市名称，如"北京"、"上海"'),
    useCache: z.boolean().optional().describe('是否使用缓存（默认 true）')
  }),

  execute: async (args: { city: string; useCache?: boolean }) => {
    const cacheKey = `weather_${args.city}`;
    const useCache = args.useCache !== false;

    try {
      // 尝试从缓存获取
      if (useCache) {
        const cached = cache.get(cacheKey);
        if (cached) {
          return JSON.stringify({
            success: true,
            data: cached,
            fromCache: true
          }, null, 2);
        }
      }

      // 调用 API
      const apiKey = process.env.WEATHER_API_KEY;
      if (!apiKey) {
        throw new Error('未配置 WEATHER_API_KEY 环境变量');
      }

      const url = `https://api.weatherapi.com/v1/current.json?key=${apiKey}&q=${encodeURIComponent(args.city)}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`API 请求失败: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // 存入缓存（15 分钟）
      if (useCache) {
        cache.set(cacheKey, data, 15 * 60 * 1000);
      }

      return JSON.stringify({
        success: true,
        data: data,
        fromCache: false
      }, null, 2);
    } catch (error: any) {
      console.error(`[ERROR] call_weather_api 失败:`, error);

      return JSON.stringify({
        success: false,
        error: error.message,
        suggestion: '请检查城市名称和网络连接'
      }, null, 2);
    }
  }
};
```

#### 2. 生成 .env.example

```bash
# 天气 API 密钥
WEATHER_API_KEY=your_api_key_here
```

#### 3. 提示用户

```
✅ API 调用工具创建成功！

下一步：
1. 复制环境变量文件：
   cp .env.example .env

2. 编辑 .env 填写真实 API 密钥

3. 测试工具：npm run dev
```

### 场景 3：文件操作工具

**用户需求**：创建文件处理工具

**AI 应询问**：
1. 操作类型（读取/写入/搜索/分析）
2. 文件格式（JSON/CSV/TXT/PDF）
3. 是否需要权限限制（如只读特定目录）

**生成步骤**：

#### 1. 生成工具代码

`src/tools/searchFiles.ts`:
```typescript
import fs from 'fs';
import path from 'path';
import { z } from 'zod';

export const searchFilesTool = {
  name: 'search_files',
  description: '在指定目录中搜索包含关键词的文件，支持文本文件搜索',

  parameters: z.object({
    directory: z.string().describe('要搜索的目录路径'),
    keyword: z.string().describe('要搜索的关键词'),
    fileExtension: z.string().optional().describe('文件扩展名过滤（如 .txt, .js）'),
    maxResults: z.number().optional().describe('最大结果数量（默认 10）')
  }),

  execute: async (args: {
    directory: string;
    keyword: string;
    fileExtension?: string;
    maxResults?: number;
  }) => {
    try {
      // 路径安全检查
      const absolutePath = path.resolve(args.directory);
      if (!fs.existsSync(absolutePath)) {
        throw new Error(`目录不存在: ${args.directory}`);
      }

      if (!fs.statSync(absolutePath).isDirectory()) {
        throw new Error(`不是有效的目录: ${args.directory}`);
      }

      // 搜索文件
      const results: Array<{ file: string; line: number; content: string }> = [];
      const maxResults = args.maxResults || 10;

      function searchInDirectory(dir: string) {
        const files = fs.readdirSync(dir);

        for (const file of files) {
          if (results.length >= maxResults) break;

          const filePath = path.join(dir, file);
          const stat = fs.statSync(filePath);

          if (stat.isDirectory()) {
            searchInDirectory(filePath);
          } else if (stat.isFile()) {
            // 检查文件扩展名
            if (args.fileExtension && !filePath.endsWith(args.fileExtension)) {
              continue;
            }

            // 搜索文件内容
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
            } catch (error) {
              // 跳过无法读取的文件（如二进制文件）
            }
          }
        }
      }

      searchInDirectory(absolutePath);

      return JSON.stringify({
        success: true,
        data: results,
        count: results.length,
        message: results.length === maxResults ? '已达到最大结果数' : undefined
      }, null, 2);
    } catch (error: any) {
      console.error(`[ERROR] search_files 失败:`, error);

      return JSON.stringify({
        success: false,
        error: error.message,
        suggestion: '请检查目录路径是否正确'
      }, null, 2);
    }
  }
};
```

---

## 错误处理最佳实践

### 1. 统一错误格式

所有错误返回必须包含：
- `success: false`
- `error`: 错误消息
- `code`: 错误代码（可选）
- `suggestion`: 解决建议（可选）

### 2. 错误分类

```typescript
// 参数错误
if (!args.param) {
  throw new Error('参数 param 是必需的');
}

// 配置错误
if (!config) {
  throw new Error('未找到配置文件，请先创建 config/xxx.json');
}

// 网络错误
if (!response.ok) {
  throw new Error(`网络请求失败: ${response.status}`);
}

// 业务错误
if (result.length === 0) {
  throw new Error('未找到符合条件的数据');
}
```

### 3. 日志记录

```typescript
// 使用 console.error 记录错误（stdout 用于 MCP 通信）
console.error(`[ERROR] ${toolName} 执行失败:`, error);
console.error(`[ERROR] 参数:`, args);
console.error(`[ERROR] 堆栈:`, error.stack);
```

---

## 测试和调试

### 开发模式测试

生成代码后，提示用户：

```
✅ 工具创建成功！

测试方法：
1. 安装依赖：npm install
2. 运行开发模式：npm run dev
3. 在 Cursor/Claude Code 中连接本地服务器
4. 测试工具调用
5. 查看终端输出的日志
```

### 调试技巧

在工具中添加调试日志：

```typescript
console.error(`[DEBUG] 工具被调用，参数:`, args);
console.error(`[DEBUG] 执行结果:`, result);
```

---

## 发布准备

### 发布前检查清单

生成代码后，提示用户检查：

1. ✅ `package.json` 配置完整
   - `name` 唯一
   - `description` 清晰
   - `author` 已填写
   - `bin` 命令名合适

2. ✅ 代码可以构建
   ```bash
   npm run build
   ```

3. ✅ 所有工具有清晰的 description

4. ✅ 敏感配置已添加到 `.gitignore`

5. ✅ 有 README.md 说明如何使用

### 发布步骤

```
准备发布？执行以下步骤：

1. 构建项目：
   npm run build

2. 运行发布脚本：
   ./scripts/publish-npm.sh

3. 按提示完成发布

发布后，用户可以通过以下方式使用：
npx -y 你的包名
```

---

## 代码生成检查清单

AI 生成代码前，确认：

- [ ] 使用 TypeScript
- [ ] 使用 ES Modules (`"type": "module"`)
- [ ] 所有导入使用 `.js` 扩展名
- [ ] 入口文件第一行是 `#!/usr/bin/env node`
- [ ] 所有工具有 4 个必需部分
- [ ] 所有异步操作有 try-catch
- [ ] 返回 JSON.stringify() 格式
- [ ] 工具名使用 snake_case
- [ ] 有清晰的错误提示
- [ ] 敏感信息使用环境变量或配置文件
- [ ] 有配置文件示例

---

## 总结

**生成代码时记住**：

1. ✅ 开箱即用（用户不需要改代码）
2. ✅ 类型安全（TypeScript + Zod）
3. ✅ 错误处理（所有 async 函数都有 try-catch）
4. ✅ 清晰提示（告诉用户下一步做什么）
5. ✅ 安全第一（参数验证、路径检查）
6. ✅ 简洁实用（只实现所需功能）

**用户可能完全不懂编程**，所以：
- 生成的代码必须完整可用
- 提供清晰的下一步指引
- 错误信息要易懂
- 提供配置文件模板

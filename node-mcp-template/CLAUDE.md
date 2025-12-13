# MCP 开发规则

## 项目类型
这是一个 FastMCP (Model Context Protocol) 服务器项目开发模板。

## 强制规范

### 项目结构
当用户要求创建 MCP 项目时，MUST 使用以下结构：
```
项目名/
├── src/
│   ├── index.ts           # 入口文件，注册工具
│   ├── tools/             # 工具目录
│   │   └── *.ts          # 各个工具文件
│   └── utils/            # 工具类（可选）
│       ├── config.ts      # 配置加载
│       └── cache.ts       # 缓存工具
├── config/               # 配置文件目录（可选）
├── package.json
├── tsconfig.json
├── .gitignore
└── README.md
```

### 工具定义规范
每个 MCP 工具 MUST 包含以下 4 个部分：

1. **name** (必需): 使用 snake_case 命名
   - 示例：`query_database`、`send_email`、`analyze_data`
   - 不要使用：`queryDatabase`、`read-file`

2. **description** (必需): 详细描述工具功能
   - AI 会根据这个描述决定是否调用此工具
   - 必须清晰说明工具的用途和使用场景
   - 示例："查询 MySQL 数据库并返回结果，支持 SELECT 语句"

3. **parameters** (必需): Zod schema 验证
   - 使用 `z.object({...})` 定义参数
   - 每个参数必须有 `.describe()` 说明
   - 示例：
     ```typescript
     parameters: z.object({
       query: z.string().describe('SQL 查询语句'),
       limit: z.number().optional().describe('返回结果数量限制')
     })
     ```

4. **execute** (必需): async 函数
   - 必须是 async 函数
   - 必须返回 JSON.stringify() 格式的字符串
   - 必须包含 try-catch 错误处理
   - 示例：
     ```typescript
     execute: async (args) => {
       try {
         const result = await doSomething(args);
         return JSON.stringify({ success: true, data: result }, null, 2);
       } catch (error: any) {
         return JSON.stringify({ success: false, error: error.message }, null, 2);
       }
     }
     ```

### 代码规范
- MUST 使用 TypeScript
- MUST 使用 ES Modules (`"type": "module"` 在 package.json)
- MUST 在入口文件第一行添加 `#!/usr/bin/env node`
- MUST 使用 try-catch 错误处理
- MUST 返回 JSON.stringify() 格式（不要返回普通对象）
- MUST 在所有导入中使用 `.js` 扩展名（因为是 ES Modules）
  - 正确：`import { tool } from './tools/myTool.js';`
  - 错误：`import { tool } from './tools/myTool';`

### 依赖管理
MUST 包含以下核心依赖：
```json
{
  "dependencies": {
    "fastmcp": "^3.25.3",
    "zod": "^4.1.13",
    "dotenv": "^17.2.3"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.3"
  }
}
```

MUST NOT 包含不必要的依赖。

### package.json 规范
MUST 包含以下字段：
```json
{
  "name": "@org/package-name",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "bin": {
    "command-name": "./dist/index.js"
  },
  "files": ["dist"],
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "prepublishOnly": "npm run build"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

## 当用户说...

### "创建 MCP 项目" 或 "初始化 MCP 项目"
执行以下步骤：

1. **询问项目信息**：
   - 项目名称（用于 package.json 的 name）
   - 功能描述（用于 description）
   - 作者信息（用于 author）
   - bin 命令名（用于可执行命令）

2. **创建项目结构**：
   - 创建 `src/`, `src/tools/`, `src/utils/` 目录
   - 生成完整的 `package.json`
   - 生成 `tsconfig.json`
   - 创建 `.gitignore`
   - 创建 `src/index.ts`（包含 FastMCP 初始化代码）
   - 创建 `README.md`

3. **生成模板代码**：
   - `src/utils/config.ts` - 配置文件加载工具
   - `src/utils/cache.ts` - 缓存工具（如果需要）

4. **提示用户**：
   ```
   ✅ MCP 项目创建成功！

   下一步：
   1. 运行 `npm install` 安装依赖
   2. 添加你的工具到 `src/tools/`
   3. 在 `src/index.ts` 中注册工具
   4. 运行 `npm run dev` 测试
   ```

### "添加一个工具..." 或 "创建工具..."
执行以下步骤：

1. **询问工具信息**：
   - 工具名称（snake_case）
   - 功能描述
   - 需要哪些参数
   - 是否需要外部配置（API密钥、数据库连接等）

2. **生成工具文件**：
   - 在 `src/tools/` 创建新文件
   - 使用标准模板定义工具
   - 包含完整的类型定义
   - 包含错误处理

3. **更新 index.ts**：
   - 添加导入语句
   - 添加 `server.addTool()` 调用

4. **生成配置文件**（如果需要）：
   - 创建配置文件模板
   - 添加到 `.gitignore`

5. **提示测试方法**：
   ```
   ✅ 工具创建成功！

   测试方法：
   1. 运行 `npm run dev`
   2. 在 Cursor 中测试工具调用
   ```

### "发布到 npm" 或 "如何发布"
提示用户：

1. 检查 `package.json` 配置：
   - `name` 必须唯一
   - `description` 已填写
   - `author` 已填写
   - `bin` 命令名称合适

2. 运行构建：
   ```bash
   npm run build
   ```

3. 使用发布脚本：
   ```bash
   cd /Users/mac/Desktop/studyProject/ai-mcp-study/node-mcp-template
   cp scripts/publish-npm.sh ../你的项目/
   cd ../你的项目
   chmod +x publish-npm.sh
   ./publish-npm.sh
   ```

## 特定场景代码生成规则

### 场景 1：数据库查询工具
当用户说"创建查询数据库的工具"时：

1. **询问**：
   - 数据库类型（MySQL/PostgreSQL/MongoDB/SQLite）
   - 连接方式（配置文件/环境变量）

2. **生成代码**：
   - 安装对应的数据库驱动依赖
   - 创建数据库连接工具
   - 创建查询工具（包含 SQL注入防护）
   - 生成配置文件模板
   - 添加错误处理

3. **示例**（MySQL）：
   ```typescript
   import mysql from 'mysql2/promise';
   import { loadConfig } from '../utils/config.js';
   import { z } from 'zod';

   export const queryDatabaseTool = {
     name: 'query_database',
     description: '查询 MySQL 数据库并返回结果，仅支持 SELECT 语句',

     parameters: z.object({
       sql: z.string().describe('SQL 查询语句（仅支持 SELECT）'),
       params: z.array(z.any()).optional().describe('SQL 参数（防止注入）')
     }),

     execute: async (args: { sql: string; params?: any[] }) => {
       try {
         // 安全检查：只允许 SELECT
         if (!args.sql.trim().toLowerCase().startsWith('select')) {
           throw new Error('仅支持 SELECT 查询');
         }

         const config = loadConfig<DatabaseConfig>('./config/database.json');
         const connection = await mysql.createConnection(config);

         const [rows] = await connection.execute(args.sql, args.params || []);
         await connection.end();

         return JSON.stringify({
           success: true,
           data: rows,
           count: Array.isArray(rows) ? rows.length : 0
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

### 场景 2：API 调用工具
当用户说"创建调用 API 的工具"时：

1. **询问**：
   - API 端点
   - 认证方式（API Key/Bearer Token/OAuth）
   - 请求方法（GET/POST/PUT/DELETE）
   - 是否需要缓存

2. **生成代码**：
   - 创建 API 客户端
   - 处理认证
   - 错误处理和重试逻辑
   - 可选的缓存支持

### 场景 3：文件操作工具
当用户说"创建文件操作工具"时：

1. **询问**：
   - 操作类型（读取/写入/搜索）
   - 文件格式（JSON/CSV/TXT/PDF）
   - 是否需要权限限制

2. **生成代码**：
   - 路径安全检查
   - 文件格式解析
   - 错误处理

## 代码模板

### src/index.ts 标准模板
```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import * as dotenv from 'dotenv';
// 导入工具
// import { myTool } from './tools/myTool.js';

// 加载环境变量
dotenv.config();

// 创建 FastMCP 服务器
const server = new FastMCP({
  name: process.env.MCP_NAME || 'MCP Server Name',
  version: '1.0.0',
});

// 注册工具
// server.addTool(myTool);

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

### src/utils/config.ts 标准模板
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

### .gitignore 标准模板
```gitignore
# Node
node_modules/
dist/
*.log
npm-debug.log*

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

## 错误处理规范

所有工具的 execute 函数 MUST：
1. 使用 try-catch 包裹所有逻辑
2. 返回结构化的错误信息
3. 包含有用的错误提示和解决建议
4. 记录错误日志（使用 console.error）

示例：
```typescript
execute: async (args) => {
  try {
    // 业务逻辑
    const result = await doSomething(args);
    return JSON.stringify({ success: true, data: result }, null, 2);
  } catch (error: any) {
    console.error(`[ERROR] 工具执行失败:`, error);
    return JSON.stringify({
      success: false,
      error: error.message,
      code: error.code || 'UNKNOWN_ERROR',
      suggestion: '请检查输入参数是否正确'
    }, null, 2);
  }
}
```

## 测试和调试

生成代码后，MUST 提示用户：

1. **安装依赖**：
   ```bash
   npm install
   ```

2. **开发模式运行**：
   ```bash
   npm run dev
   ```

3. **在 Cursor 中测试**：
   - 配置 Cursor 的 mcp.json
   - 测试工具调用
   - 检查返回结果

4. **调试技巧**：
   - 使用 `console.error()` 输出调试信息
   - 检查参数验证
   - 查看错误堆栈

## 文档规范

生成的 README.md MUST 包含：
1. 项目简介
2. 安装方法
3. 配置说明
4. 使用示例
5. 可用工具列表
6. 开发和发布指南

## 参考文档

生成代码时，参考以下文档：
- `docs/mcp-development-guide.md` - 完整开发指南
- `docs/tool-templates.md` - 工具模板
- `docs/examples/` - 各种场景示例

## 总结

记住：
1. ✅ 用户可能完全不懂 Node.js
2. ✅ 生成的代码必须开箱即用
3. ✅ 所有步骤必须有清晰的提示
4. ✅ 错误信息必须有用且易懂
5. ✅ 代码必须符合所有规范

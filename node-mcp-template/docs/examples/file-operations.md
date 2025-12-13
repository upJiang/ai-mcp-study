# 示例：文件操作 MCP 工具

本示例展示如何创建一个文件处理和代码分析的 MCP 工具。

## 场景说明

**需求**：创建一个 MCP 工具，用于项目代码分析和文件处理。

**功能**：
- 搜索项目中的 TODO 注释
- 统计代码行数
- 查找特定函数或类定义
- 生成项目结构树
- 分析代码复杂度

---

## 第 1 步：告诉 AI 你的需求

在 Cursor/Claude Code 中输入：

```
创建一个 MCP 项目，用于项目代码分析：

项目信息：
- 项目名：@mytools/code-analyzer-mcp
- 功能：代码分析和文件处理
- 作者：王五 <wangwu@example.com>
- 命令名：code-analyzer

需要的工具：
1. search_todos - 搜索项目中的 TODO/FIXME 注释
   - 输入：项目目录
   - 返回：TODO 列表（文件、行号、内容）

2. count_lines - 统计代码行数
   - 输入：目录或文件
   - 返回：总行数、代码行数、注释行数、空行数
   - 按文件类型分类统计

3. find_definition - 查找函数或类定义
   - 输入：函数名/类名、搜索目录
   - 返回：定义位置列表

4. generate_tree - 生成目录结构树
   - 输入：目录路径
   - 返回：树形结构文本
   - 支持忽略 node_modules 等

5. analyze_complexity - 分析代码复杂度
   - 输入：文件路径
   - 返回：圈复杂度、函数数量等指标

默认忽略 node_modules、.git、dist 等目录。
```

---

## 第 2 步：AI 生成的项目结构

```
code-analyzer-mcp/
├── src/
│   ├── index.ts
│   ├── tools/
│   │   ├── searchTodos.ts
│   │   ├── countLines.ts
│   │   ├── findDefinition.ts
│   │   ├── generateTree.ts
│   │   └── analyzeComplexity.ts
│   └── utils/
│       ├── fileScanner.ts  # 文件扫描工具
│       └── ignorePatterns.ts  # 忽略规则
├── package.json
├── tsconfig.json
├── .gitignore
└── README.md
```

---

## 第 3 步：生成的代码示例

### package.json

```json
{
  "name": "@mytools/code-analyzer-mcp",
  "version": "1.0.0",
  "description": "MCP tool for code analysis and file operations",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "bin": {
    "code-analyzer": "./dist/index.js"
  },
  "files": ["dist"],
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["mcp", "fastmcp", "code-analysis", "file-operations"],
  "author": "王五 <wangwu@example.com>",
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

### src/utils/ignorePatterns.ts

```typescript
/**
 * 默认忽略的目录和文件模式
 */
export const DEFAULT_IGNORE_PATTERNS = [
  'node_modules',
  '.git',
  'dist',
  'build',
  '.next',
  'coverage',
  '.cache',
  '.DS_Store',
  'Thumbs.db',
  '*.log'
];

/**
 * 检查路径是否应该被忽略
 */
export function shouldIgnore(filePath: string, patterns: string[] = DEFAULT_IGNORE_PATTERNS): boolean {
  const segments = filePath.split('/');

  for (const pattern of patterns) {
    // 目录匹配
    if (segments.includes(pattern)) {
      return true;
    }

    // 通配符匹配
    if (pattern.includes('*')) {
      const regex = new RegExp(pattern.replace(/\*/g, '.*'));
      if (regex.test(filePath)) {
        return true;
      }
    }
  }

  return false;
}
```

### src/utils/fileScanner.ts

```typescript
import fs from 'fs';
import path from 'path';
import { shouldIgnore } from './ignorePatterns.js';

/**
 * 递归扫描目录
 */
export function* scanDirectory(
  dir: string,
  ignorePatterns?: string[]
): Generator<string> {
  const absoluteDir = path.resolve(dir);

  if (!fs.existsSync(absoluteDir)) {
    throw new Error(`目录不存在: ${dir}`);
  }

  const entries = fs.readdirSync(absoluteDir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(absoluteDir, entry.name);
    const relativePath = path.relative(absoluteDir, fullPath);

    // 检查是否应该忽略
    if (shouldIgnore(relativePath, ignorePatterns)) {
      continue;
    }

    if (entry.isDirectory()) {
      yield* scanDirectory(fullPath, ignorePatterns);
    } else if (entry.isFile()) {
      yield fullPath;
    }
  }
}

/**
 * 获取文件扩展名
 */
export function getFileExtension(filePath: string): string {
  return path.extname(filePath).toLowerCase();
}

/**
 * 判断是否为文本文件
 */
export function isTextFile(filePath: string): boolean {
  const textExtensions = [
    '.js', '.ts', '.jsx', '.tsx',
    '.py', '.rb', '.php', '.java', '.c', '.cpp', '.h',
    '.css', '.scss', '.less',
    '.html', '.xml', '.json', '.yaml', '.yml',
    '.md', '.txt', '.sh', '.bash'
  ];

  const ext = getFileExtension(filePath);
  return textExtensions.includes(ext);
}
```

### src/tools/searchTodos.ts

```typescript
import fs from 'fs';
import path from 'path';
import { z } from 'zod';
import { scanDirectory, isTextFile } from '../utils/fileScanner.js';

export const searchTodosTool = {
  name: 'search_todos',
  description: '搜索项目中的 TODO、FIXME、HACK 等注释',

  parameters: z.object({
    directory: z.string().describe('要搜索的目录路径'),
    keywords: z.array(z.string()).optional().describe('要搜索的关键词，默认 ["TODO", "FIXME", "HACK"]'),
    maxResults: z.number().optional().describe('最大结果数，默认 100')
  }),

  execute: async (args: {
    directory: string;
    keywords?: string[];
    maxResults?: number;
  }) => {
    try {
      const keywords = args.keywords || ['TODO', 'FIXME', 'HACK', 'XXX', 'NOTE'];
      const maxResults = args.maxResults || 100;
      const results: Array<{
        file: string;
        line: number;
        keyword: string;
        content: string;
      }> = [];

      const absoluteDir = path.resolve(args.directory);

      for (const filePath of scanDirectory(args.directory)) {
        if (results.length >= maxResults) break;

        // 只处理文本文件
        if (!isTextFile(filePath)) continue;

        try {
          const content = fs.readFileSync(filePath, 'utf8');
          const lines = content.split('\n');

          lines.forEach((line, index) => {
            if (results.length >= maxResults) return;

            for (const keyword of keywords) {
              // 匹配注释中的关键词
              const pattern = new RegExp(`//.*${keyword}|/\\*.*${keyword}|#.*${keyword}`, 'i');
              if (pattern.test(line)) {
                results.push({
                  file: path.relative(absoluteDir, filePath),
                  line: index + 1,
                  keyword: keyword,
                  content: line.trim()
                });
                break;
              }
            }
          });
        } catch (e) {
          // 跳过无法读取的文件
        }
      }

      return JSON.stringify({
        success: true,
        data: results,
        count: results.length,
        message: results.length === maxResults ? '已达到最大结果数' : undefined
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] search_todos:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### src/tools/countLines.ts

```typescript
import fs from 'fs';
import path from 'path';
import { z } from 'zod';
import { scanDirectory, getFileExtension, isTextFile } from '../utils/fileScanner.js';

export const countLinesTool = {
  name: 'count_lines',
  description: '统计代码行数，包括总行数、代码行、注释行、空行，按文件类型分类',

  parameters: z.object({
    path: z.string().describe('文件或目录路径'),
    fileTypes: z.array(z.string()).optional().describe('要统计的文件类型，如 [".js", ".ts"]，默认所有文本文件')
  }),

  execute: async (args: {
    path: string;
    fileTypes?: string[];
  }) => {
    try {
      const absolutePath = path.resolve(args.path);
      const stats = fs.statSync(absolutePath);

      let files: string[] = [];

      if (stats.isFile()) {
        files = [absolutePath];
      } else if (stats.isDirectory()) {
        files = Array.from(scanDirectory(args.path)).filter(isTextFile);
      } else {
        throw new Error('不支持的路径类型');
      }

      // 按文件类型分组统计
      const byType: Record<string, {
        files: number;
        totalLines: number;
        codeLines: number;
        commentLines: number;
        blankLines: number;
      }> = {};

      let totalStats = {
        files: 0,
        totalLines: 0,
        codeLines: 0,
        commentLines: 0,
        blankLines: 0
      };

      for (const file of files) {
        const ext = getFileExtension(file);

        // 过滤文件类型
        if (args.fileTypes && !args.fileTypes.includes(ext)) {
          continue;
        }

        try {
          const content = fs.readFileSync(file, 'utf8');
          const lines = content.split('\n');

          let codeLines = 0;
          let commentLines = 0;
          let blankLines = 0;
          let inBlockComment = false;

          for (const line of lines) {
            const trimmed = line.trim();

            if (trimmed === '') {
              blankLines++;
            } else if (trimmed.startsWith('//') || trimmed.startsWith('#')) {
              commentLines++;
            } else if (trimmed.startsWith('/*') || inBlockComment) {
              commentLines++;
              if (trimmed.includes('*/')) {
                inBlockComment = false;
              } else if (trimmed.startsWith('/*')) {
                inBlockComment = true;
              }
            } else {
              codeLines++;
            }
          }

          // 按类型统计
          if (!byType[ext]) {
            byType[ext] = {
              files: 0,
              totalLines: 0,
              codeLines: 0,
              commentLines: 0,
              blankLines: 0
            };
          }

          byType[ext].files++;
          byType[ext].totalLines += lines.length;
          byType[ext].codeLines += codeLines;
          byType[ext].commentLines += commentLines;
          byType[ext].blankLines += blankLines;

          // 总计
          totalStats.files++;
          totalStats.totalLines += lines.length;
          totalStats.codeLines += codeLines;
          totalStats.commentLines += commentLines;
          totalStats.blankLines += blankLines;
        } catch (e) {
          // 跳过无法读取的文件
        }
      }

      return JSON.stringify({
        success: true,
        data: {
          total: totalStats,
          byType: byType
        }
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] count_lines:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### src/tools/generateTree.ts

```typescript
import fs from 'fs';
import path from 'path';
import { z } from 'zod';
import { shouldIgnore, DEFAULT_IGNORE_PATTERNS } from '../utils/ignorePatterns.js';

export const generateTreeTool = {
  name: 'generate_tree',
  description: '生成目录结构树形图',

  parameters: z.object({
    directory: z.string().describe('目录路径'),
    maxDepth: z.number().optional().describe('最大深度，默认 5')
  }),

  execute: async (args: {
    directory: string;
    maxDepth?: number;
  }) => {
    try {
      const absoluteDir = path.resolve(args.directory);
      const maxDepth = args.maxDepth || 5;

      if (!fs.existsSync(absoluteDir)) {
        throw new Error(`目录不存在: ${args.directory}`);
      }

      function buildTree(
        dir: string,
        prefix: string = '',
        depth: number = 0
      ): string[] {
        if (depth >= maxDepth) return [];

        const lines: string[] = [];
        const entries = fs.readdirSync(dir, { withFileTypes: true });

        // 排序：目录在前，文件在后
        entries.sort((a, b) => {
          if (a.isDirectory() && !b.isDirectory()) return -1;
          if (!a.isDirectory() && b.isDirectory()) return 1;
          return a.name.localeCompare(b.name);
        });

        entries.forEach((entry, index) => {
          const isLast = index === entries.length - 1;
          const relativePath = path.relative(absoluteDir, path.join(dir, entry.name));

          // 检查是否忽略
          if (shouldIgnore(relativePath, DEFAULT_IGNORE_PATTERNS)) {
            return;
          }

          const connector = isLast ? '└── ' : '├── ';
          const name = entry.isDirectory() ? `${entry.name}/` : entry.name;

          lines.push(`${prefix}${connector}${name}`);

          if (entry.isDirectory()) {
            const newPrefix = prefix + (isLast ? '    ' : '│   ');
            const subTree = buildTree(
              path.join(dir, entry.name),
              newPrefix,
              depth + 1
            );
            lines.push(...subTree);
          }
        });

        return lines;
      }

      const tree = [
        path.basename(absoluteDir) + '/',
        ...buildTree(absoluteDir)
      ].join('\n');

      return JSON.stringify({
        success: true,
        data: tree
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] generate_tree:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### src/index.ts

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import * as dotenv from 'dotenv';
import { searchTodosTool } from './tools/searchTodos.js';
import { countLinesTool } from './tools/countLines.js';
import { generateTreeTool } from './tools/generateTree.js';

dotenv.config();

const server = new FastMCP({
  name: 'Code Analyzer MCP',
  version: '1.0.0',
});

// 注册工具
server.addTool(searchTodosTool);
server.addTool(countLinesTool);
server.addTool(generateTreeTool);

// 启动服务器
console.error('========================================');
console.error(`MCP Server: ${server.name}`);
console.error('========================================');

server.start({ transportType: 'stdio' });

process.on('SIGINT', () => {
  console.error('\n正在关闭服务器...');
  process.exit(0);
});
```

---

## 第 4 步：测试使用

### 4.1 安装依赖

```bash
npm install
```

### 4.2 测试运行

```bash
npm run dev
```

### 4.3 发布到 npm

```bash
./scripts/publish-npm.sh
```

### 4.4 配置 Cursor

```json
{
  "mcpServers": {
    "code-analyzer": {
      "command": "npx",
      "args": ["-y", "@mytools/code-analyzer-mcp"]
    }
  }
}
```

---

## 第 5 步：使用示例

### 示例 1：搜索 TODO

```
帮我找一下项目中所有的 TODO 注释
```

AI 调用 `search_todos`：
```json
{
  "directory": "."
}
```

返回：
```json
{
  "success": true,
  "data": [
    {
      "file": "src/index.ts",
      "line": 42,
      "keyword": "TODO",
      "content": "// TODO: 添加错误处理"
    },
    ...
  ],
  "count": 15
}
```

### 示例 2：统计代码行数

```
统计一下 src 目录的代码行数，按文件类型分类
```

AI 调用 `count_lines`：
```json
{
  "path": "./src"
}
```

返回：
```json
{
  "success": true,
  "data": {
    "total": {
      "files": 25,
      "totalLines": 3580,
      "codeLines": 2840,
      "commentLines": 420,
      "blankLines": 320
    },
    "byType": {
      ".ts": {
        "files": 20,
        "totalLines": 3200,
        "codeLines": 2600,
        "commentLines": 380,
        "blankLines": 220
      },
      ...
    }
  }
}
```

### 示例 3：生成项目结构

```
生成当前项目的目录结构树
```

AI 调用 `generate_tree`：
```json
{
  "directory": ".",
  "maxDepth": 3
}
```

---

## 扩展功能建议

### 1. 代码复杂度分析

添加圈复杂度计算、函数长度分析等。

### 2. 依赖分析

分析项目的依赖关系，检测循环依赖。

### 3. 代码质量检查

集成 ESLint、Prettier 等工具。

### 4. Git 提交分析

分析代码提交历史、贡献者统计等。

---

## 常见问题

### Q1: 如何自定义忽略规则？

**A**: 修改 `src/utils/ignorePatterns.ts`，添加自定义模式。

### Q2: 支持哪些编程语言？

**A**: 支持所有文本文件，统计逻辑会根据文件扩展名自动适配。

### Q3: 如何优化性能？

**A**:
- 限制扫描深度
- 添加文件大小限制
- 使用并发处理

---

## 总结

这个示例展示了：
- ✅ 文件系统操作
- ✅ 递归目录扫描
- ✅ 文件内容解析
- ✅ 代码统计分析
- ✅ 模式匹配和过滤

**参考这个示例可以创建各种文件处理工具！**

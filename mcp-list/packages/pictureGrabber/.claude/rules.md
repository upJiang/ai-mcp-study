# MCP 图片采集工具 - 开发规范

## 版本管理规范

### 版本号格式
采用语义化版本 (Semantic Versioning): `主版本.次版本.修订号`
- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 更新记录要求

**每次代码修改、任意文件修改，必须同步更新以下内容：**

1. **更新 `src/index.ts` 中的版本号**
   ```typescript
   const server = new Server(
     {
       name: "image-collector",
       version: "x.x.x",  // 更新此处
     },
     ...
   );
   ```

2. **更新 `CHANGELOG.md`**
   - 在文件顶部添加新版本记录
   - 格式如下：
   ```markdown
   ## [版本号] - YYYY-MM-DD

   ### 新增
   - 新功能描述

   ### 优化
   - 优化内容描述

   ### 修复
   - Bug 修复描述

   ### 变更
   - 破坏性变更描述
   ```

3. **重新编译项目**
   ```bash
   npm run build
   ```

## 代码规范

### 文件结构
- `src/index.ts` - 主入口文件，包含所有 MCP 工具实现
- `build/` - 编译输出目录
- `CHANGELOG.md` - 版本更新记录
- `.claude/rules.md` - 开发规范（本文件）
- `CLAUDE.md` - 项目说明文档

### 命名规范
- 函数名：小驼峰命名 (camelCase)
- 常量：全大写下划线分隔 (UPPER_SNAKE_CASE)
- 类型/接口：大驼峰命名 (PascalCase)

### 注释规范
- 关键函数需要添加功能注释
- 复杂逻辑需要添加行内注释
- 使用中文注释便于理解

## 功能开发规范

### 新增 MCP 工具
1. 在 `ListToolsRequestSchema` 处理器中注册工具
2. 在 `CallToolRequestSchema` 处理器中实现逻辑
3. 更新 `CLAUDE.md` 文档
4. 更新版本号和 CHANGELOG

### 错误处理
- 所有外部操作（网络请求、文件操作）必须有 try-catch
- 错误信息需要友好可读
- 单个操作失败不应影响整体流程

## 测试规范

### 修改后必须测试
1. 编译成功：`npm run build`
2. 基本功能：测试图片采集功能
3. 边界情况：无图片页面、网络错误等

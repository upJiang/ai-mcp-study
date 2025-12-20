# EventAnalyzer MCP Server (Node.js)

> 埋点事件分析工具的 MCP 服务 - Node.js 版本

## 功能特性

提供 5 个强大的 MCP Tools，帮助分析和验证埋点数据：

1. **query_event_fields** - 查询事件字段定义
2. **analyze_tracking_data** - 分析埋点数据，检测类型错误、枚举值错误等
3. **explain_field** - 解释字段含义和枚举值
4. **find_field_in_code** - 在项目代码中搜索字段使用位置
5. **compare_events** - 比较两个事件的字段差异

## 安装使用

### 方式 1: npx 直接使用（推荐）

在 Cursor 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "EventAnalyzer-Node": {
      "command": "npx",
      "args": ["-y", "@upjiang/eventanalyzer-mcp"]
    }
  }
}
```

### 方式 2: 全局安装

```bash
npm install -g @upjiang/eventanalyzer-mcp
```

然后在 Cursor 配置中：

```json
{
  "mcpServers": {
    "EventAnalyzer-Node": {
      "command": "eventanalyzer-mcp"
    }
  }
}
```

## 环境变量配置

可选：自定义埋点 API 地址

```bash
export EVENT_API_BASE_URL=https://your-api-domain.com/api/event
```

默认使用：`https://tptest-3d66.top/trans/api/event`

## 使用示例

### 1. 查询事件字段定义

```typescript
// Tool: query_event_fields
{
  "event": "LlwResExposure",
  "show_details": true
}
```

### 2. 分析埋点数据

```typescript
// Tool: analyze_tracking_data
{
  "data": "eyJldmVudCI6ICJMbHdSZXNFeHBvc3VyZSIsIC4uLn0=",  // Base64 或 JSON
  "check_required": false
}
```

### 3. 解释字段含义

```typescript
// Tool: explain_field
{
  "event": "LlwResExposure",
  "field_name": "resource_type",
  "show_enum": true
}
```

### 4. 搜索字段在代码中的位置

```typescript
// Tool: find_field_in_code
{
  "field_name": "resource_id",
  "project_path": "/path/to/your/project",
  "max_results": 50
}
```

### 5. 比较两个事件

```typescript
// Tool: compare_events
{
  "event1": "LlwResExposure",
  "event2": "LlwResDownBtnClick"
}
```

## 技术栈

- **FastMCP** - 简化的 MCP SDK 框架
- **TypeScript** - 类型安全的开发体验
- **Zod** - 运行时参数验证
- **Node.js** - >=18.0.0

## 开发

```bash
# 克隆项目
git clone https://github.com/upjiang/ai-mcp-study.git
cd ai-mcp-study/mcp-list/packages/EventAnalyzer-node

# 安装依赖
npm install

# 开发模式运行
npm run dev

# 编译
npm run build
```

## 与 Python 版本的对比

| 特性 | Python 版本 | Node.js 版本 |
|------|------------|-------------|
| 传输协议 | stdio + HTTP/SSE | stdio only |
| 部署方式 | Docker + Nginx | npm + npx |
| 功能范围 | 5 个 Tools | 5 个 Tools |
| 使用场景 | 远程服务器部署 | 本地 Cursor 使用 |

## License

MIT

## 作者

upjiang

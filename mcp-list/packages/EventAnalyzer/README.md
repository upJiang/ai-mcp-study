# EventAnalyzer MCP Service

埋点分析 MCP 服务，提供埋点事件字段查询、数据分析、代码搜索等功能。

## 功能特性

### 5 个 MCP Tools

1. **query_event_fields** - 查询事件字段定义
   - 返回事件的所有字段（约 78 个）
   - 包含字段类型、说明、枚举值等信息

2. **analyze_tracking_data** - 分析埋点数据
   - 检测字段类型错误
   - 检测未知字段（可能是拼写错误）
   - 检测枚举值错误
   - 统计字段覆盖率

3. **explain_field** - 解释字段含义
   - 显示字段类型和说明
   - 展示枚举值映射
   - 推荐相关字段

4. **find_field_in_code** - 在代码中搜索字段
   - 搜索字段的实现位置
   - 显示代码上下文
   - 支持多种文件类型（.js, .ts, .vue等）

5. **compare_events** - 比较事件差异
   - 显示两个事件的公共字段
   - 显示各自独有的字段
   - 统计差异数量

## 安装

### 1. 安装依赖

```bash
cd mcp-list/packages/EventAnalyzer
pip install -r requirements.txt
```

### 2. 注册 MCP 服务

#### 方式 1: 使用 Claude Code CLI（推荐）

```bash
claude mcp add --scope user EventAnalyzer python /Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer/server.py
```

#### 方式 2: 手动配置

编辑 `~/.config/Cursor/User/mcp.json`（或 Claude Code 配置文件）：

```json
{
  "mcpServers": {
    "EventAnalyzer": {
      "command": "python",
      "args": [
        "/Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer/server.py"
      ]
    }
  }
}
```

## 使用示例

### 1. 查询事件字段定义

```
查询 LlwResExposure 事件的所有字段定义
```

MCP 会调用 `query_event_fields` 工具并返回 78 个字段的详细信息。

### 2. 分析埋点数据

```
分析这个埋点数据：
eyJpZGVudGl0aWVzIjp7IiRpZGVudGl0eV9jb29raWVfaWQiOiIxOWIwYzIwYjdmNDMzYzctMGY1ZTg4YWM3ZTIzODk4LTFkNTI1NjMxLTIwNzM2MDAtMTliMGMyMGI3ZjUzYmExIiwiJGlkZW50aXR5X2xvZ2luX2lkIjoiMTgwMDE5ODgwIn0sImRpc3RpbmN0X2lkIjoiMTgwMDE5ODgwIiwibGliIjp7IiRsaWIiOiJqcyIsIiRsaWJfbWV0aG9kIjoiY29kZSIsIiRsaWJfdmVyc2lvbiI6IjEuMjYuMyJ9LCJwcm9wZXJ0aWVzIjp7IiR0aW1lem9uZV9vZmZzZXQiOi00ODAsIiRzY3JlZW5faGVpZ2h0IjoxMDgwLCIkc2NyZWVuX3dpZHRoIjoxOTIwLCIkdmlld3BvcnRfaGVpZ2h0Ijo5NTgsIiR2aWV3cG9ydF93aWR0aCI6MTE3NCwiJGxpYiI6ImpzIiwiJGxpYl92ZXJzaW9uIjoiMS4yNi4zIiwiJGxhdGVzdF90cmFmZmljX3NvdXJjZV90eXBlIjoi55u05o6l5rWB6YePIiwiJGxhdGVzdF9zZWFyY2hfa2V5d29yZCI6IuacquWPluWIsOWAvF%2Fnm7TmjqXmiZPlvIAiLCIkbGF0ZXN0X3JlZmVycmVyIjoiIiwicGxhdGZvcm1fdHlwZSI6MiwicHJvZHVjdF9uYW1lIjowLCJpc19sb2dpbiI6dHJ1ZSwibGFzdF9sb2dpbl91c2VyX2lkIjoiMTgwMDE5ODgwIiwic2l0ZSI6MSwicGFnZV90eXBlIjo1LCJhY2Nlc3Nfc291cmNlX3NpdGUiOjAsImFjY2Vzc19zb3VyY2VfcGFnZSI6MCwibGxfaWQiOiIxNDY3NjM0OCIsInBhcmVudF9wYXlfdHlwZSI6OTk5LCJsc29mIjoiSEFHODQ4MjQxNDk5MiIsImFjdGlvbl9pZCI6IkZGQjU3N0EzODFEOTE3M0IxODgyOTIyRjQ4RDAzQUFGIiwiaXNfc2F2ZWQiOmZhbHNlLCJwYXlfdHlwZSI6MSwiaXNfc2FtZV91c2VyIjp0cnVlLCJzb2ZfdXNlcl9pZCI6IiIsIm9jY3VwYXRpb25fdHlwZSI6MCwiYWJfdGVzdCI6WyJUUFdMLTgzMjAtMCJdLCJyZXNfcHJpY2UiOjI4LCJyZXNfcHJlcGF5X3ByaWNlIjowLCJyZXNfYWN0dWFsZGlzY291bnRfdHlwZSI6MjUsImRvd25fdHlwZSI6MCwidm91Y2hlcl90eXBlIjowLCJpc19jb21tZXJjaWFsIjp0cnVlLCJyZXNfdHlwZSI6MSwiYWxnb3JpdGhtX3R5cGUiOjAsImFsZ29yaXRobV92ZXJzaW9uIjowLCJhYiI6MCwicmVxdWVzdF9pZCI6IiIsInBhcmVudF9pZCI6IiIsInNvdXJjZV9hbGciOjAsInBvc2l0aW9uIjowLCJsaXN0X2xheW91dF90eXBlIjowLCJsbHdfc291cmNlX3NjZW5lIjoyMSwic2VhcmNoX3dvcmQiOiIxNDY3NjM0OCIsIiRyZWZlcnJlciI6Imh0dHA6Ly8zZC5kZXYuM2Q2Ni5jb20vcmVzaHRtbGEvbW9kZWwvaXRlbXMvcnovcnpqcldqZ2M3RzNSa0pjb1l3WHouaHRtbD9rdz0xNDY3NjM0OCZhY3Rpb25faWQ9RkZCNTc3QTM4MUQ5MTczQjE4ODI5MjJGNDhEMDNBQUYmc29mPUFBRzE0OTkyJnNpZ249Y2RiM2IxYjFkMjVjNzdhZCZsc3M9MjEiLCJpbWdfaWQiOiIiLCIkaXNfZmlyc3RfZGF5IjpmYWxzZSwiJHJlZmVycmVyX2hvc3QiOiIzZC5kZXYuM2Q2Ni5jb20iLCIkdXJsIjoiaHR0cDovLzNkLmRldi4zZDY2LmNvbS9yZXNodG1sYS9tb2RlbC9pdGVtcy9yei9yempyV2pnYzdHM1JrSmNvWXdYei5odG1sP2t3PTE0Njc2MzQ4JmFjdGlvbl9pZD1GRkI1NzdBMzgxRDkxNzNCMTg4MjkyMkY0OEQwM0FBRiZzb2Y9QUFHMTQ5OTImc2lnbj1jZGIzYjFiMWQyNWM3N2FkJmxzcz0yMSIsIiR0aXRsZSI6IuOAkDNE5qih5Z6L5LiL6L2944CRM2RtYXjkuJPnlKjlu7rmqKHntKDmnZAr6LS05Zu%2B5p2Q6LSoLTNE5rqc5rqc572RKDNkNjYpIn0sImxvZ2luX2lkIjoiMTgwMDE5ODgwIiwiYW5vbnltb3VzX2lkIjoiMTliMGMyMGI3ZjQzM2M3LTBmNWU4OGFjN2UyMzg5OC0xZDUyNTYzMS0yMDczNjAwLTE5YjBjMjBiN2Y1M2JhMSIsInR5cGUiOiJ0cmFjayIsImV2ZW50IjoiTGx3UmVzRG93bkJ0bkNsaWNrIiwidGltZSI6MTc2NTUzMTM4OTk1OSwiX3RyYWNrX2lkIjo0NjIyMDk5NTksIl9mbHVzaF90aW1lIjoxNzY1NTMxMzg5OTU5fQ==
```

MCP 会自动解析 Base64 数据并检测问题。

### 3. 解释字段含义

```
platform_type 字段是什么意思？
```

### 4. 在代码中搜索字段

```
在项目中搜索 ll_id 字段的实现位置
```

### 5. 比较事件差异

```
比较 LlwResExposure 和 LlwResDownBtnClick 两个事件的差异
```

## Chrome 插件

配套的 Chrome 插件位于 `chrome-extension/` 目录，用于监听和捕获浏览器中的埋点请求。

### 安装插件

1. 打开 Chrome 浏览器，访问 `chrome://extensions/`
2. 开启"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 `chrome-extension/` 目录

### 使用插件

1. 访问包含埋点的网页
2. 点击浏览器工具栏的插件图标
3. 查看捕获到的埋点列表
4. 复制埋点数据或事件名称
5. 在 Claude Code/Cursor 中使用 MCP 工具分析

## API 接口

埋点字段定义接口：`https://tptest-3d66.top/trans/api/event?event=事件名称`

## 技术栈

- **Python 3.11+**
- **MCP SDK** - Model Context Protocol
- **Requests** - HTTP 客户端

## 项目结构

```
EventAnalyzer/
├── server.py                    # MCP 服务入口
├── requirements.txt             # Python 依赖
├── README.md                    # 使用文档
├── chrome-extension/            # Chrome 插件
│   ├── manifest.json
│   ├── background.js
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   └── utils/
│       └── decoder.js
└── src/
    ├── __init__.py
    ├── api_client.py            # API 客户端
    ├── event_analyzer.py        # 事件分析器
    ├── field_explainer.py       # 字段解释器
    ├── code_searcher.py         # 代码搜索器
    └── utils/
        ├── __init__.py
        ├── base64_decoder.py    # Base64 解码器
        └── type_checker.py      # 类型检查器
```

## 作者

Generated with Claude Code

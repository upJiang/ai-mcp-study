# 在 Cursor 中使用远程 EventAnalyzer MCP 服务

## 🌐 远程 HTTPS 访问方式

服务已部署到：`https://junfeng530.xyz/mcp/eventanalyzer`

---

## 📋 Cursor 配置（HTTP/SSE 方式）

### 配置文件位置

```bash
~/.cursor/mcp.json
```

### 配置内容

```json
{
  "mcpServers": {
    "EventAnalyzer": {
      "transport": {
        "type": "sse",
        "url": "https://junfeng530.xyz/mcp/eventanalyzer/sse"
      }
    }
  }
}
```

---

## 🔧 完整配置步骤

### 步骤 1：创建或编辑配置文件

```bash
# 创建目录（如果不存在）
mkdir -p ~/.cursor

# 编辑配置文件
code ~/.cursor/mcp.json
```

### 步骤 2：添加配置

如果文件不存在或为空，添加：

```json
{
  "mcpServers": {
    "EventAnalyzer": {
      "transport": {
        "type": "sse",
        "url": "https://junfeng530.xyz/mcp/eventanalyzer/sse"
      }
    }
  }
}
```

如果已有其他 MCP 服务，添加到现有配置中：

```json
{
  "mcpServers": {
    "existing-service": {
      "command": "node",
      "args": ["/path/to/service.js"]
    },
    "EventAnalyzer": {
      "transport": {
        "type": "sse",
        "url": "https://junfeng530.xyz/mcp/eventanalyzer/sse"
      }
    }
  }
}
```

### 步骤 3：保存并重启 Cursor

1. 保存文件：`Cmd+S`
2. 完全退出 Cursor：`Cmd+Q`
3. 重新打开 Cursor

---

## ✅ 验证配置

### 1. 检查工具列表

打开 Cursor 聊天窗口（`Cmd+L`），输入：

```
列出所有可用的 MCP 工具
```

应该能看到 EventAnalyzer 的 5 个工具：
- query_event_fields
- analyze_tracking_data
- explain_field
- find_field_in_code
- compare_events

### 2. 测试工具调用

```
使用 query_event_fields 查询 LlwResExposure 事件的字段定义
```

成功返回 78 个字段就说明配置正确！

---

## 🧪 测试用例

### 测试 1：查询事件字段

```
查询 LlwResExposure 事件的所有字段
```

### 测试 2：分析埋点数据

```
分析这个埋点数据：
eyJwcm9wZXJ0aWVzIjp7InBsYXRmb3JtX3R5cGUiOjIsInByb2R1Y3RfbmFtZSI6MCwiaXNfbG9naW4iOnRydWV9fQ==

事件名称：LlwResExposure
```

### 测试 3：解释字段

```
platform_type 字段是什么意思？
```

---

## 🔍 故障排查

### 问题 1：连接失败

**检查服务是否正常运行**：

```bash
# 方法 1：直接访问
curl https://junfeng530.xyz/mcp/eventanalyzer/sse

# 方法 2：SSH 到服务器检查
ssh root@junfeng530.xyz
cd /opt/mcp-services/ai-mcp-study/mcp-list
docker-compose ps
docker-compose logs eventanalyzer
```

### 问题 2：看不到工具

**可能原因**：
- Cursor 配置文件格式错误
- 没有完全重启 Cursor
- 服务端未正常启动

**解决方法**：

1. 验证 JSON 格式：
   ```bash
   python -c "import json; print(json.load(open('/Users/mac/.cursor/mcp.json')))"
   ```

2. 检查服务状态（服务器上）：
   ```bash
   docker-compose logs --tail=50 eventanalyzer
   ```

3. 完全退出并重启 Cursor

---

## 🚀 使用流程

### 方式 1：直接对话

```
帮我查一下 LlwResExposure 事件有哪些字段
```

Cursor 会自动调用远程 MCP 服务。

### 方式 2：配合 Chrome 扩展

1. 使用 Chrome 扩展捕获埋点
2. 复制 MCP 命令
3. 粘贴到 Cursor
4. 获得分析结果

---

## 💡 优势

使用远程 MCP 服务的好处：

✅ **无需本地安装依赖** - 不需要在本地安装 Python 和依赖包
✅ **多设备共享** - 任何设备的 Cursor 都能使用
✅ **集中管理** - 服务统一部署，方便维护
✅ **高可用** - 服务器 24/7 运行，随时可用

---

## 📊 网络架构

```
Cursor (本地)
    ↓ HTTPS/SSE
https://junfeng530.xyz/mcp/eventanalyzer/sse
    ↓ Nginx 反向代理
mcp-eventanalyzer 容器:8000
    ↓ 调用
https://tptest-3d66.top/trans/api/event
```

---

## ⚙️ 高级配置

### 添加认证（可选）

如果需要添加访问控制，可以在配置中添加 headers：

```json
{
  "mcpServers": {
    "EventAnalyzer": {
      "transport": {
        "type": "sse",
        "url": "https://junfeng530.xyz/mcp/eventanalyzer/sse",
        "headers": {
          "Authorization": "Bearer your-token-here"
        }
      }
    }
  }
}
```

（需要在服务端添加相应的认证逻辑）

---

## 🎉 完成！

配置成功后，您就可以：

1. ✅ 在 Cursor 中通过 HTTPS 使用 EventAnalyzer
2. ✅ 无需本地安装 Python 依赖
3. ✅ 多设备共享同一个 MCP 服务
4. ✅ 随时随地分析埋点数据

**开始使用吧！** 🚀

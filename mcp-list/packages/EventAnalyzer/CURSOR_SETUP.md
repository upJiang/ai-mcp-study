# 在 Cursor 中使用 EventAnalyzer MCP 服务

## 📋 快速配置（5 分钟）

### 步骤 1：安装 Python 依赖

```bash
cd /Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer
pip install -r requirements.txt
```

**验证安装**：
```bash
python -c "import mcp; print('✓ MCP SDK 已安装')"
python -c "import requests; print('✓ Requests 已安装')"
```

---

### 步骤 2：找到 Cursor MCP 配置文件

**macOS 配置文件位置**：
```bash
~/.cursor/mcp.json
```

**如果文件不存在，创建它**：
```bash
mkdir -p ~/.cursor
touch ~/.cursor/mcp.json
```

**打开配置文件**：
```bash
# 使用 VSCode 打开
code ~/.cursor/mcp.json

# 或者使用 vim
vim ~/.cursor/mcp.json

# 或者使用系统默认编辑器
open ~/.cursor/mcp.json
```

---

### 步骤 3：添加 MCP 服务器配置

在 `~/.cursor/mcp.json` 中添加以下内容：

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

**如果已有其他 MCP 服务**，添加到现有配置中：

```json
{
  "mcpServers": {
    "existing-service": {
      "command": "node",
      "args": ["/path/to/existing/service.js"]
    },
    "EventAnalyzer": {
      "command": "python",
      "args": [
        "/Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer/server.py"
      ]
    }
  }
}
```

**保存文件**：`Cmd+S`

---

### 步骤 4：重启 Cursor

**完全退出并重新打开 Cursor**（重要！）

- macOS: `Cmd+Q` 退出，然后重新打开
- 不要只是重新加载窗口，必须完全退出

---

### 步骤 5：验证 MCP 工具已加载

#### 方法 1：查看工具列表

1. 打开 Cursor 聊天窗口（`Cmd+L`）
2. 在输入框中输入 `@`
3. 应该能看到 EventAnalyzer 的工具：
   - `query_event_fields`
   - `analyze_tracking_data`
   - `explain_field`
   - `find_field_in_code`
   - `compare_events`

#### 方法 2：直接调用工具

在聊天中输入：
```
列出所有可用的 MCP 工具
```

应该能看到 EventAnalyzer 的 5 个工具。

---

## 🧪 功能测试

### 测试 1：查询事件字段定义

**在 Cursor 聊天中输入**：
```
使用 query_event_fields 查询 LlwResExposure 事件的字段定义
```

**期望结果**：
```
✓ 调用 query_event_fields 工具
✓ 返回 78 个字段
✓ 包含字段类型、说明、枚举值
```

**示例输出**：
```json
{
  "event": "LlwResExposure",
  "total_fields": 78,
  "fields": {
    "platform_type": {
      "type": "NUMBER",
      "tips": "平台类型",
      "desc": "平台类型说明",
      "trans": "{\"1\":\"PC\",\"2\":\"H5\",\"3\":\"小程序\"}"
    },
    "product_name": {
      "type": "NUMBER",
      "tips": "产品名称",
      ...
    }
  }
}
```

---

### 测试 2：分析埋点数据

**在 Cursor 聊天中输入**：
```
使用 analyze_tracking_data 分析这个埋点数据：
eyJwcm9wZXJ0aWVzIjp7InBsYXRmb3JtX3R5cGUiOjIsInByb2R1Y3RfbmFtZSI6MCwiaXNfbG9naW4iOnRydWUsImxhc3RfbG9naW5fdXNlcl9pZCI6IjE4MDAxOTg4MCIsInNpdGUiOjEsInBhZ2VfdHlwZSI6NSwibGxfaWQiOiIxNDY3NjM0OCJ9LCJldmVudCI6Ikxsd1Jlc0V4cG9zdXJlIn0=

事件名称：LlwResExposure
```

**期望结果**：
```
✓ 自动解码 Base64 数据
✓ 检测字段类型错误
✓ 检测未知字段
✓ 显示字段覆盖率
```

---

### 测试 3：解释字段含义

**在 Cursor 聊天中输入**：
```
使用 explain_field 解释 platform_type 字段的含义
```

**期望结果**：
```
字段名：platform_type
类型：NUMBER
说明：平台类型
枚举值：
  1 = PC
  2 = H5
  3 = 小程序
```

---

### 测试 4：搜索字段实现

**在 Cursor 聊天中输入**：
```
使用 find_field_in_code 在项目中搜索 ll_id 字段的实现
```

**需要提供**：
- 项目路径（可选，默认当前工作目录）
- 搜索深度（可选，默认递归搜索）

**期望结果**：
```
✓ 显示包含该字段的文件列表
✓ 显示代码片段和上下文
✓ 显示匹配的行号
```

---

### 测试 5：比较事件差异

**在 Cursor 聊天中输入**：
```
使用 compare_events 比较 LlwResExposure 和 LlwResDownBtnClick 两个事件的差异
```

**期望结果**：
```
✓ 显示公共字段
✓ 显示各自独有的字段
✓ 统计差异数量
```

---

## 🔧 故障排查

### 问题 1：看不到 EventAnalyzer 工具

**可能原因**：
- Cursor 没有完全重启
- 配置文件路径错误
- JSON 格式错误

**解决方法**：

1. **检查配置文件是否存在**：
   ```bash
   cat ~/.cursor/mcp.json
   ```

2. **验证 JSON 格式**：
   ```bash
   python -c "import json; json.load(open('/Users/mac/.cursor/mcp.json'))"
   ```

3. **检查 Python 路径**：
   ```bash
   which python
   # 应该输出：/usr/local/bin/python 或 /opt/homebrew/bin/python3
   ```

4. **测试 MCP 服务器**：
   ```bash
   cd /Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer
   python server.py
   # 应该启动并等待输入，按 Ctrl+C 退出
   ```

5. **完全退出并重启 Cursor**：
   - macOS: `Cmd+Q` 退出
   - 重新打开 Cursor
   - 打开新的聊天窗口

---

### 问题 2：工具调用失败

**可能原因**：
- Python 依赖未安装
- API 接口不可访问
- 参数格式错误

**解决方法**：

1. **检查依赖**：
   ```bash
   pip list | grep -E "(mcp|requests)"
   ```

2. **测试 API 接口**：
   ```bash
   curl "https://tptest-3d66.top/trans/api/event?event=LlwResExposure"
   ```

3. **查看 Cursor 日志**：
   - macOS: `~/Library/Logs/Cursor/`
   - 查找 MCP 相关错误

4. **手动测试工具**：
   ```bash
   cd /Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer
   python -c "
   from src.api_client import EventAPIClient
   client = EventAPIClient()
   print(client.get_event_fields('LlwResExposure'))
   "
   ```

---

### 问题 3：中文显示乱码

**可能原因**：
- 终端编码问题

**解决方法**：

在配置中添加环境变量：
```json
{
  "mcpServers": {
    "EventAnalyzer": {
      "command": "python",
      "args": [
        "/Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer/server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "LANG": "zh_CN.UTF-8"
      }
    }
  }
}
```

---

## 💡 使用技巧

### 技巧 1：自然语言调用

不需要精确输入工具名称，可以用自然语言：

```
帮我查一下 LlwResExposure 事件有哪些字段
```

Cursor 会自动识别并调用 `query_event_fields` 工具。

---

### 技巧 2：配合 Chrome 扩展使用

1. 使用 Chrome 扩展捕获埋点数据
2. 点击"复制 MCP 命令"
3. 粘贴到 Cursor 聊天窗口
4. 立即获得分析结果

**示例**：
```
使用 analyze_tracking_data 分析以下数据：
eyJwcm9wZXJ0aWVzIjp7Li4ufX0=
事件：LlwResExposure
```

---

### 技巧 3：组合使用多个工具

```
1. 先查询 LlwResExposure 事件的字段定义
2. 然后分析这个埋点数据：eyJwcm9wZXJ0aWVzIjp7Li4ufX0=
3. 最后在项目中搜索有问题的字段
```

Cursor 会按顺序调用：
1. `query_event_fields`
2. `analyze_tracking_data`
3. `find_field_in_code`

---

### 技巧 4：保存常用查询

创建一个 `埋点分析.md` 文件：

```markdown
# 常用埋点分析

## 查询事件字段
使用 query_event_fields 查询 LlwResExposure 事件

## 分析测试数据
使用 analyze_tracking_data 分析：
eyJ...base64_data...
事件：LlwResExposure

## 字段说明查询
- platform_type: 平台类型
- product_name: 产品名称
- ll_id: 资源 ID
```

在 Cursor 中打开这个文件，可以快速复制粘贴使用。

---

## ✅ 验证清单

配置成功后，应该能够：

- [ ] 在 Cursor 聊天中看到 EventAnalyzer 工具
- [ ] 成功调用 `query_event_fields` 查询字段
- [ ] 成功调用 `analyze_tracking_data` 分析数据
- [ ] 成功调用 `explain_field` 解释字段
- [ ] 成功调用 `find_field_in_code` 搜索代码
- [ ] 成功调用 `compare_events` 比较事件

---

## 🎉 完成！

现在您可以在 Cursor 中直接使用 EventAnalyzer 进行埋点分析了！

**工作流程**：
1. Chrome 扩展捕获埋点 →
2. 复制数据 →
3. Cursor 中分析 →
4. 快速定位问题！

---

## 📚 相关文档

- [完整功能文档](./README.md)
- [验证指南](./VERIFICATION_GUIDE.md)
- [Chrome 扩展使用](./chrome-extension/README.md)

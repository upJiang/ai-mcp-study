# OpenAPI Generator 使用指南

## 📦 步骤 1：确认依赖已安装

确保所有 Python 依赖已经安装：

```bash
cd src\OpenAPIGenerator
pip install -r requirements.txt
```

## ⚙️ 步骤 2：配置 MCP 服务器

### 选项 A：使用 Claude Code CLI（推荐）

打开命令行，执行：

```bash
claude mcp add --scope user OpenAPIGenerator python {项目绝对路径}/src/OpenAPIGenerator/server.py
```

**验证配置**：

```bash
claude mcp list
```

你应该能看到 `OpenAPIGenerator` 在列表中。

### 选项 B：手动编辑配置文件

1. 打开配置文件：
   - **Trae 编辑器**：`C:\Users\Administrator\AppData\Roaming\Trae\User\mcp.json`
   - **Cursor 编辑器**：`~/.config/Cursor/User/mcp.json`

2. 添加以下配置：

```json
{
  "mcpServers": {
    "OpenAPIGenerator": {
      "command": "python",
      "args": ["{项目绝对路径}\\src\\OpenAPIGenerator\\server.py"],
      "env": {}
    }
  }
}
```

3. **重启编辑器**（重要！）

## 🔥 步骤 3：开始使用

重启编辑器后，在 Claude Code 对话中，你就可以使用 OpenAPI 生成器了！

### 使用示例


#### 1️⃣ 为控制器生成 OpenAPI 文档

```
为 D:/www/my-laravel-project 的 UserController 生成 OpenAPI 文档
```

**Claude 会：**
1. 读取控制器代码
2. 查找路由定义
3. 查找相关的 Model、FormRequest、Resource
4. 自动分析代码，推断参数和返回值
5. 生成并保存 OpenAPI 文档

**文档保存位置：**
```
D:/www/my-laravel-project/storage/api-docs/UserController.openapi.json
```

#### 2️⃣ 只生成特定方法的文档

```
为 UserController 的 index 和 store 方法生成文档
```

**Claude 会：**
- 只分析指定的方法
- 生成部分文档


## 🎯 实际使用流程

### 场景 1：为控制器生成完整文档

```
1.  逐个生成文档
   "为 UserController 生成文档"
   "为 ProductController 生成文档"
   ...
```


### 场景 3：只关注核心接口

```
"为 UserController 的 login, register, logout 方法生成文档"
```

只生成关键接口，减少不必要的文档。

## 📋 生成的文档格式

生成的文档符合 **OpenAPI 3.0** 规范，可以：

1. **导入 Postman**：
   - 打开 Postman
   - 选择 Import → 选择生成的 JSON 文件
   - 自动生成所有接口请求

2. **使用 Swagger UI**：
   ```bash
   # 启动 Swagger UI
   docker run -p 8080:8080 -e SWAGGER_JSON=/openapi.json -v D:/www/my-project/storage/api-docs:/usr/share/nginx/html swaggerapi/swagger-ui
   ```

   访问：`http://localhost:8080`

3. **生成客户端 SDK**：
   ```bash
   # 使用 OpenAPI Generator 生成 TypeScript SDK
   openapi-generator-cli generate -i openapi.json -g typescript-axios -o ./client
   ```

## 🔍 验证文档准确性

生成文档后，建议：

1. **人工审查**：检查参数和响应是否准确
2. **实际测试**：导入 Postman 实际调用接口验证
3. **团队评审**：让团队成员审查文档完整性

## ❗ 常见问题

### Q1: MCP 服务器未出现在工具列表中？

**解决方法**：
1. 确认配置文件路径正确
2. **重启编辑器**（必须重启！）
3. 检查 Python 路径是否正确

### Q2: 提示"不是有效的 Laravel 项目"？

**解决方法**：
- 确保项目根目录包含 `artisan` 文件
- 确保 `app/Http/Controllers` 目录存在

### Q3: 找不到控制器？

**解决方法**：
- 检查控制器名称是否正确（区分大小写）
- 确保控制器文件在 `app/Http/Controllers` 目录中
- 控制器必须继承 `Controller` 类

### Q4: 生成的文档不准确？

**原因**：
- AI 分析基于代码逻辑推断，复杂逻辑可能无法完全准确
- 动态路由、复杂验证规则可能识别不准

**建议**：
- 生成后手动修正
- 结合实际测试验证

## 🎓 高级技巧

### 1. 自定义输出目录

```
为 UserController 生成文档，输出到 docs/api 目录
```


**祝你使用愉快！** 🎉

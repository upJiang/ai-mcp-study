# 发布前检查清单

在运行 `./scripts/publish-npm.sh` 之前，请确认以下所有项：

## ✅ package.json 配置

- [ ] **name** 字段已修改（确保全网唯一）
  - 格式：`@your-org/your-package` 或 `your-package`
  - 不能与已有包重名
  - 建议：使用自己的用户名或组织名作为前缀

- [ ] **description** 已填写
  - 简短描述功能（一句话）
  - 示例：`"MCP tool for querying MySQL database"`

- [ ] **author** 已填写
  - 格式：`"Your Name <your.email@example.com>"`
  - 或：`"Your Name"`

- [ ] **bin** 命令名称合适
  - 简短易记
  - 不与常用命令冲突（如 `ls`, `cd`, `npm` 等）
  - 全小写，使用连字符（如 `my-tool`）

- [ ] **keywords** 已添加
  - 至少包含：`"mcp"`, `"fastmcp"`, `"claude"`
  - 添加功能相关关键词（如 `"database"`, `"api"` 等）

- [ ] **version** 版本号正确
  - 首次发布：`"1.0.0"`
  - 更新发布：按规范递增（patch/minor/major）

- [ ] **license** 许可证已设置
  - 推荐：`"MIT"`（最宽松）
  - 或其他开源许可证

## ✅ 代码质量

- [ ] **代码可以正常构建**
  ```bash
  npm run build
  ```
  - 无 TypeScript 编译错误
  - `dist/` 目录生成成功
  - `dist/index.js` 存在

- [ ] **代码可以正常运行**
  ```bash
  npm run dev
  ```
  - 服务器成功启动
  - 无运行时错误
  - 所有工具可以正常调用

- [ ] **所有工具都有清晰的 description**
  - description 准确描述功能
  - AI 能根据 description 判断何时调用
  - 包含使用场景说明

- [ ] **所有工具都有错误处理**
  - 所有 async 函数有 try-catch
  - 返回结构化错误信息
  - 错误信息清晰易懂

- [ ] **代码遵循规范**
  - 使用 TypeScript
  - 使用 ES Modules (`type: "module"`)
  - 所有导入使用 `.js` 扩展名
  - 入口文件第一行是 `#!/usr/bin/env node`

## ✅ npm 准备

- [ ] **已创建 npm 账号**
  - 访问 https://www.npmjs.com/signup 注册
  - 记住用户名、密码、邮箱

- [ ] **已在终端登录 npm**
  ```bash
  npm login
  # 输入用户名、密码、邮箱

  npm whoami  # 检查登录状态
  ```

- [ ] **包名在 npm 上可用**
  - 访问 `https://www.npmjs.com/package/你的包名`
  - 如果显示 404，说明包名可用
  - 如果已存在，修改 package.json 中的 name

## ✅ 文档完整

- [ ] **有 README.md 说明如何使用**
  - 包含安装方法
  - 包含使用示例
  - 包含配置说明（如果需要）

- [ ] **敏感配置已添加到 .gitignore**
  - `.env` 文件
  - `config/*.json` 配置文件（保留 `example.*` 模板）
  - 不要提交 API 密钥、数据库密码等

- [ ] **有配置文件模板**（如果需要）
  - 提供 `config/example.*.json` 或 `.env.example`
  - 注释清楚每个配置项的作用
  - 不包含真实的敏感信息

## ✅ 安全检查

- [ ] **没有硬编码的密钥或密码**
  - 检查代码中是否有 API Key
  - 检查是否有数据库密码
  - 使用环境变量或配置文件

- [ ] **输入验证完整**
  - 所有工具使用 Zod schema 验证参数
  - 危险操作（如数据库修改）有额外验证
  - SQL 注入防护（使用参数化查询）

- [ ] **权限控制合理**
  - 文件操作限制在特定目录
  - 数据库操作限制权限（如只读）
  - 不允许执行系统命令（除非明确需要）

## ✅ 依赖管理

- [ ] **依赖版本固定**
  - 核心依赖使用固定版本或小版本范围
  - 避免使用 `*` 或过大的版本范围

- [ ] **没有不必要的依赖**
  - 检查 `package.json` 的 dependencies
  - 删除未使用的包
  - devDependencies 不会被发布

- [ ] **package-lock.json 存在**
  - 确保依赖版本一致
  - 提交到 git（如果使用 git）

## ✅ 测试

- [ ] **手动测试所有工具**
  - 在 Cursor/Claude Code 中测试
  - 测试正常情况
  - 测试错误情况（如无效参数、网络错误等）

- [ ] **测试配置场景**（如果适用）
  - 配置文件缺失时的错误提示
  - 配置格式错误时的错误提示
  - 环境变量缺失时的错误提示

## 检查完成？

如果以上**所有项**都打勾 ✅，可以运行发布脚本：

```bash
./scripts/publish-npm.sh
```

## 常见问题

### Q1: 包名已被占用怎么办？

**A**: 修改 `package.json` 中的 `name` 字段，建议格式：
- `@your-username/package-name`（推荐）
- `your-company-package-name`

### Q2: 构建失败怎么办？

**A**: 检查 TypeScript 错误：
1. 查看终端错误信息
2. 修复代码错误
3. 重新运行 `npm run build`

### Q3: 登录 npm 失败？

**A**: 常见原因：
1. 用户名、密码错误 → 重置密码
2. 邮箱未验证 → 检查邮箱验证链接
3. 网络问题 → 检查网络连接

### Q4: 发布后想撤回？

**A**:
- 24 小时内可以删除：`npm unpublish package-name --force`
- 超过 24 小时需要联系 npm 支持
- 建议：发布前仔细检查

---

**提示**：首次发布建议先使用测试包名，确认流程无误后再发布正式包。

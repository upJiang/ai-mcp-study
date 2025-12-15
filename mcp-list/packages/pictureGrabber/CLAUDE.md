# pictureGrabber - MCP 图片采集工具

## 项目概述

这是一个基于 MCP (Model Context Protocol) 的图片采集工具。当用户输入网址时，工具会自动打开浏览器访问网页，采集页面上所有 jpg/png 格式的图片（过滤 50x50 以下的小图），并保存到本地桌面。

当前版本：**v1.2.1**

## 技术栈

- **语言**: TypeScript
- **运行时**: Node.js (ESM)
- **MCP SDK**: @modelcontextprotocol/sdk ^1.0.0
- **浏览器自动化**: Playwright ^1.40.0 (Chromium)

---

## 项目结构

```
pictureGrabber/
├── src/                      # 源代码目录
│   ├── index.ts              # MCP 服务器入口点
│   ├── collector.ts          # 图片采集核心逻辑
│   ├── download.ts           # 图片下载功能
│   ├── overlay.ts            # 页面弹窗模板
│   └── utils.ts              # 工具函数
├── build/                    # 编译输出目录
│   ├── index.js              # 编译后的入口
│   ├── collector.js
│   ├── download.js
│   ├── overlay.js
│   └── utils.js
├── .claude/                  # Claude Code 配置
│   ├── rules.md              # 开发规范
│   └── settings.local.json   # 本地设置
├── package.json              # 项目配置和依赖
├── tsconfig.json             # TypeScript 编译配置
├── CHANGELOG.md              # 版本更新记录
├── CLAUDE.md                 # 项目说明文档（本文件）
└── node_modules/             # 依赖包
```

---

## 架构

### 核心模块

**[src/index.ts](src/index.ts)** - MCP 服务器入口点 (86 行)
- 创建 MCP 服务器实例
- 定义 `collect_images` 工具
- 注册请求处理器：`ListToolsRequestSchema`、`CallToolRequestSchema`
- 使用 stdio 传输层与 Claude 通信

**[src/collector.ts](src/collector.ts)** - 图片采集核心逻辑 (182 行)
- `collectImages()`: 主采集函数，协调整个采集流程
- `extractImageUrls()`: 从页面提取所有符合条件的图片 URL
- `downloadAllImages()`: 批量下载图片到指定目录
- `formatResult()`: 生成采集结果文本
- 管理浏览器生命周期和弹窗状态

**[src/download.ts](src/download.ts)** - 图片下载功能 (74 行)
- `downloadImage()`: 下载单个图片到指定路径
- 支持 HTTP/HTTPS 协议自动识别
- 支持 HTTP 重定向处理
- 10 秒超时保护

**[src/overlay.ts](src/overlay.ts)** - 页面弹窗模板 (226 行)
- `getOverlayInitScript()`: 预注入脚本，页面加载时显示弹窗
- `getEnsureOverlayScript()`: 确保弹窗存在的后备脚本
- `getNoImagesFoundScript()`: 更新弹窗为"未找到图片"
- `getSuccessScript()`: 更新弹窗为"采集成功"
- 包含样式常量和 CSS 动画定义

**[src/utils.ts](src/utils.ts)** - 工具函数 (48 行)
- `getDesktopPath()`: 获取当前用户桌面路径
- `extractDomain()`: 从 URL 提取域名并转换为安全的文件夹名
- `getTimestamp()`: 生成时间戳字符串 (YYYYMMDD_HHMMSS)
- `getImageExtension()`: 获取图片扩展名

### 数据流

```
用户请求 → index.ts (MCP Server)
                ↓
         collector.ts (启动浏览器、访问页面)
                ↓
         overlay.ts (注入采集中弹窗)
                ↓
         collector.ts (提取图片 URL)
                ↓
         download.ts (下载图片到桌面)
                ↓
         overlay.ts (更新弹窗为成功/失败)
                ↓
         返回结果给用户
```

---

## MCP Tool

### collect_images

采集指定网页上的所有 jpg/png 图片并保存到桌面。

**参数**:
| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| url | string | 是 | 要采集图片的网页地址 |

**功能流程**:
1. 在桌面创建 `图片采集_域名_时间戳` 目录
2. 启动 Chromium 浏览器（可见窗口模式）
3. 预注入弹窗脚本（页面加载时立即显示"采集中"）
4. 访问目标 URL，等待网络空闲
5. 提取所有 `<img>` 标签的 src 属性
6. 过滤条件：
   - 仅保留 jpg/jpeg/png 格式
   - 排除 50x50 像素以下的小图
   - URL 去重
7. 下载所有符合条件的图片（超时 10 秒/张）
8. 更新弹窗显示结果，2 秒后关闭浏览器
9. 返回采集结果

**返回示例**:
```
图片采集完成！

网页地址：https://example.com/gallery
发现图片：25 张
成功下载：23 张
下载失败：2 张
保存位置：C:\Users\WIN7\Desktop\图片采集_example_com_20241204_143052
```

---

## 开发命令

```bash
# 安装依赖
cd src/pictureGrabber
npm install

# 安装 Playwright 浏览器
npx playwright install chromium

# 编译 TypeScript
npm run build

# 运行服务（测试用）
npm start
```

---

## MCP 服务器配置

### Claude Code CLI（推荐）

**Windows:**
```bash
claude mcp add --scope user pictureGrabber node e:/mcp/3d66.mcp/src/pictureGrabber/build/index.js
```

**验证配置:**
```bash
claude mcp list
claude mcp get pictureGrabber
```

### 手动配置（Trae/Cursor 编辑器）

**Windows (Trae):**
编辑 `C:\Users\Administrator\AppData\Roaming\Trae\User\mcp.json`:

```json
{
  "mcpServers": {
    "pictureGrabber": {
      "command": "node",
      "args": ["E:\\mcp\\3d66.mcp\\src\\pictureGrabber\\build\\index.js"],
      "env": {}
    }
  }
}
```

**Claude Desktop:**
编辑 `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pictureGrabber": {
      "command": "node",
      "args": ["e:\\mcp\\3d66.mcp\\src\\pictureGrabber\\build\\index.js"]
    }
  }
}
```

配置更改后，需要重启 Claude Code/编辑器以使更改生效。

---

## 使用示例

对 Claude 说：
- "请采集这个网页的图片：https://software.3d66.com/"
- "帮我下载这个页面的所有图片 https://example.com/gallery"

---

## 关键设计决策

- **可见浏览器**：使用 `headless: false`，用户可以看到采集过程
- **预注入弹窗**：使用 `page.addInitScript()` 在页面加载时立即显示弹窗，提升用户体验
- **多重弹窗保障**：DOMContentLoaded 事件 + 延时注入 + 后备注入，确保弹窗正确显示
- **图片过滤**：自动过滤 50x50 以下的小图（通常是图标、tracking pixels）
- **URL 去重**：避免重复下载同一图片
- **错误隔离**：单个图片下载失败不影响其他图片
- **超时保护**：每张图片下载超时 10 秒，页面加载超时 30 秒
- **重定向支持**：自动处理 HTTP 3xx 重定向
- **模块化架构**：代码拆分为 5 个独立模块，职责单一，便于维护和测试

---

## 开发规范

**重要**：在进行任何代码修改之前，必须先阅读 [.claude/rules.md](.claude/rules.md) 文件，该文件包含：
- 版本管理规范（语义化版本号）
- 更新记录要求（每次修改必须更新版本号和 CHANGELOG）
- 代码规范（命名、注释等）
- 功能开发规范
- 测试规范

**每次代码修改、任意文件修改，必须同步更新版本号和 CHANGELOG.md。**

### 版本号位置

需要同步更新的版本号：
1. `src/index.ts` 中的 `version` 字段
2. `CHANGELOG.md` 中添加新版本记录

---

## 修改配置

要修改采集行为：
- **图片尺寸过滤**：编辑 [src/collector.ts](src/collector.ts) 中的 `width > 50 && height > 50`
- **支持的图片格式**：编辑 [src/collector.ts](src/collector.ts) 中的正则表达式
- **下载超时**：编辑 [src/download.ts](src/download.ts) 中的 `timeout: 10000`
- **页面加载超时**：编辑 [src/collector.ts](src/collector.ts) 中的 `timeout: 30000`
- **弹窗样式**：编辑 [src/overlay.ts](src/overlay.ts) 中的样式常量

修改后需要重新编译：`npm run build`

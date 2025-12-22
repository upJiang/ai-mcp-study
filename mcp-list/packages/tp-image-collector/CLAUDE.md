# tp-image-collector

基于 MCP (Model Context Protocol) 的网页图片采集工具，自动采集页面上所有图片并保存到本地桌面。

## 技术栈

- **语言**: TypeScript / Node.js
- **MCP SDK**: @modelcontextprotocol/sdk
- **浏览器自动化**: Playwright (Chromium)

## 项目结构

```
tp-image-collector/
├── src/
│   ├── index.ts          # MCP 服务入口，工具定义
│   ├── collector.ts      # 图片采集核心逻辑
│   ├── download.ts       # 图片下载功能（并发控制）
│   ├── overlay.ts        # 页面弹窗模板
│   └── utils.ts          # 工具函数
├── build/                # 编译输出目录
├── package.json          # 项目配置（版本号 2.5.0）
├── tsconfig.json         # TypeScript 配置
├── CHANGELOG.md          # 版本更新日志
└── .claude/rules.md      # 开发规范
```

## MCP 工具

### collect_images

采集指定网页上的图片并保存到桌面。

**参数**:
- `url` (string, required): 目标网页地址

**支持的图片来源**:
- `<img>` 标签的 src 属性
- Lazy Loading 属性：`data-src`、`data-lazy-src`、`data-original`、`data-lazy`、`data-url`、`data-image`、`data-srcset`
- CSS 背景图：`background-image`、`data-background`、`data-bg`
- `<picture>` 标签中的 `<source>` 元素

**支持的格式**: jpg/jpeg/png/webp/avif/gif

**过滤规则**: 自动过滤 50×50 像素以下的小图

**采集流程**:
1. 启动 Chromium 浏览器（可见窗口）
2. 访问目标 URL，显示"采集中"弹窗
3. 提取页面中所有图片链接和尺寸
4. 按类型分类并发下载（5 张同时下载）
5. 实时显示下载进度
6. 采集完成后显示明细列表
7. 自动打开保存的文件夹

**保存位置**: `{用户桌面}/图片采集_域名_时间戳/`

**目录结构**:
```
图片采集_www_example_com_20251216_120000/
├── jpg/
├── png/
├── webp/
├── avif/
└── gif/
```

## 安装和配置

### 依赖安装

```bash
cd src/tp-image-collector
npm install
npx playwright install chromium
npm run build
```

### MCP 配置

#### Claude Code CLI（推荐）

```bash
claude mcp add --scope user tp-image-collector node E:/mcp/3d66.mcp/src/tp-image-collector/build/index.js
```

验证配置：
```bash
claude mcp list
claude mcp get tp-image-collector
```

#### 手动配置

**Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tp-image-collector": {
      "command": "node",
      "args": ["E:/mcp/3d66.mcp/src/tp-image-collector/build/index.js"]
    }
  }
}
```

**Trae/Cursor** (`%APPDATA%\Trae\User\mcp.json`):

```json
{
  "mcpServers": {
    "tp-image-collector": {
      "command": "node",
      "args": ["E:\\mcp\\3d66.mcp\\src\\tp-image-collector\\build\\index.js"]
    }
  }
}
```

## 使用示例

```
采集图片 https://www.3d66.com/
```

## 开发命令

```bash
npm run build    # 编译 TypeScript
npm start        # 运行服务
```

## 开发规范

修改代码前请阅读 [.claude/rules.md](.claude/rules.md)。

**每次代码修改必须同步更新版本号和 CHANGELOG.md。**

# tp-image-collector

基于 MCP (Model Context Protocol) 的网页图片采集工具。

## 功能特点

- 🌐 **一键采集** - 输入网址即可自动采集页面所有图片
- 🖼️ **多格式支持** - 支持 JPG、PNG、WEBP、AVIF、GIF 五种格式
- 📁 **自动分类** - 图片按格式自动分类存放到子目录
- 🔍 **智能过滤** - 自动过滤 50x50 以下的小图（图标、占位符等）
- 📊 **实时预览** - 采集完成后弹窗显示明细列表，支持按类型筛选
- 📂 **自动打开** - 采集完成自动打开保存目录

## 快速开始

### 安装依赖

```bash
cd src/tp-image-collector
npm install
npx playwright install chromium
```

### 编译运行

```bash
npm run build
npm start
```

## 配置

### Claude Desktop

编辑 `%APPDATA%\Claude\claude_desktop_config.json`：

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

### Claude Code CLI

```bash
claude mcp add --scope user tp-image-collector node E:/mcp/3d66.mcp/src/tp-image-collector/build/index.js
```

> 注意：将路径替换为你的实际项目路径

## 使用方法

对 Claude 说：

```
采集图片 https://example.com/gallery
```

或

```
请打开这个网址，采集图片：https://example.com/
```

## 采集流程

1. 启动浏览器访问目标网页
2. 显示"采集中"弹窗
3. 提取页面所有图片链接和尺寸
4. 过滤小图，保留有效图片
5. 在桌面创建 `图片采集_域名_时间戳` 目录
6. 按类型分类下载到子目录（jpg/、png/、webp/、avif/、gif/）
7. 显示采集结果明细（支持 Tab 筛选）
8. 自动打开保存目录

## 项目结构

```
tp-image-collector/
├── src/
│   ├── index.ts      # MCP 服务入口
│   ├── collector.ts  # 采集核心逻辑
│   ├── download.ts   # 下载功能
│   ├── overlay.ts    # 页面弹窗模板
│   └── utils.ts      # 工具函数
├── build/            # 编译输出
├── package.json
└── tsconfig.json
```

## 技术栈

- TypeScript
- Node.js
- [MCP SDK](https://github.com/modelcontextprotocol/sdk) - Model Context Protocol
- [Playwright](https://playwright.dev/) - 浏览器自动化

## 注意事项

- 浏览器以可见窗口模式运行，采集完成后不会自动关闭
- 图片保留原始文件名，重名文件自动添加后缀
- 单张图片下载超时 10 秒，失败不影响整体流程
- 保存路径：`{用户桌面}/图片采集_域名_时间戳/`

## 许可证

MIT

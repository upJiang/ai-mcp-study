# wfw-tool-1-map

[![npm version](https://img.shields.io/npm/v/wfw-tool-1-map.svg)](https://www.npmjs.com/package/wfw-tool-1-map)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP 图片采集工具 - 自动采集网页上的 jpg/png 图片并保存到桌面

## 功能特性

- 🖼️ **自动采集图片** - 智能提取网页中的所有 jpg/png 图片
- 🌐 **浏览器自动化** - 基于 Playwright，真实浏览器环境访问网页
- 💾 **一键保存** - 自动下载图片到桌面，无需手动操作
- 🔧 **MCP 集成** - 完美集成到 Cursor 和 Claude Code 中使用

## 快速开始

### 方式一：使用 npx 直接运行

```bash
npx wfw-tool-1-map
```

### 方式二：在 Cursor 中使用

1. 打开 Cursor 设置（Mac: `Cmd + Shift + J`，Windows/Linux: `Ctrl + Shift + J`）
2. 选择 "MCP Settings"
3. 添加以下配置：

```json
{
  "mcpServers": {
    "image-collector": {
      "command": "npx",
      "args": ["-y", "wfw-tool-1-map"]
    }
  }
}
```

4. 重启 Cursor

### 方式三：在 Claude Code 中使用

1. 打开 Claude Code 配置文件：`~/.claude/claude_desktop_config.json`
2. 添加以下配置：

```json
{
  "mcpServers": {
    "image-collector": {
      "command": "npx",
      "args": ["-y", "wfw-tool-1-map"]
    }
  }
}
```

3. 重启 Claude Code

## 使用示例

配置完成后，在 Cursor 或 Claude Code 中可以这样使用：

```
采集这个网页的图片：https://example.com/gallery
```

AI 会自动调用 `collect_images` 工具，访问指定网页并下载所有图片。

## 工具说明

### collect_images

采集指定网页上的所有 jpg/png 图片并保存到桌面。

**参数：**

- `url` (必需) - 要采集图片的网页地址
  - 类型：`string`
  - 示例：`"https://example.com/gallery"`

**返回：**

工具会返回采集结果，包括：
- 成功采集的图片数量
- 图片保存位置（桌面）
- 失败的图片（如果有）

**示例调用：**

```json
{
  "url": "https://example.com/gallery"
}
```

## 工作原理

1. 🌐 使用 Playwright 打开无头浏览器
2. 📄 访问指定的网页地址
3. 🔍 扫描页面中的所有 `<img>` 标签
4. 🎯 筛选出 jpg 和 png 格式的图片
5. ⬇️ 并行下载图片到桌面
6. ✅ 返回采集结果报告

## 系统要求

- **Node.js** >= 18.0.0
- **操作系统**：macOS / Windows / Linux

## 注意事项

⚠️ **首次运行**：第一次使用时，Playwright 会自动下载浏览器（约 300MB），请确保网络连接稳定。

⚠️ **访问限制**：某些网站可能有反爬虫机制，如遇到问题请检查：
- 网站是否允许自动化访问
- 网络连接是否正常
- 图片链接是否有效

⚠️ **存储空间**：请确保桌面有足够的存储空间来保存图片。

## 常见问题

### Q: 为什么图片没有下载？

A: 可能的原因：
1. 网页加载失败（检查网络连接）
2. 页面没有 jpg/png 图片
3. 图片链接失效或需要登录
4. 桌面权限不足

### Q: 支持哪些图片格式？

A: 目前支持 `.jpg`、`.jpeg` 和 `.png` 格式的图片。

### Q: 图片保存在哪里？

A: 所有图片都保存在用户的桌面目录下。

### Q: 可以采集需要登录的网页吗？

A: 目前不支持需要登录的网页，工具以访客身份访问页面。

## 开发

```bash
# 克隆仓库
git clone <repo-url>
cd pictureGrabber

# 安装依赖
npm install

# 编译 TypeScript
npm run build

# 运行
npm start
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [npm 包地址](https://www.npmjs.com/package/wfw-tool-1-map)
- [MCP 官方文档](https://modelcontextprotocol.io)
- [Playwright 文档](https://playwright.dev)

---

**让图片采集变得简单！** 🎉

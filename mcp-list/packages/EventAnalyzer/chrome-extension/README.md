# 埋点数据捕获 Chrome 插件

配合 EventAnalyzer MCP 服务使用的 Chrome 浏览器插件，用于监听和捕获网页中的埋点请求。

## 功能特性

1. **自动捕获埋点** - 监听所有包含 `tpdi` 的网络请求
2. **数据解析** - 自动解析 URL 编码 + Base64 双重编码的数据
3. **可视化展示** - 在弹窗中展示埋点列表
4. **快速复制** - 一键复制事件名称、JSON 数据、Base64 数据
5. **MCP 集成** - 生成 MCP 调用命令，直接在 Claude Code/Cursor 中使用

## 安装步骤

### 1. 准备图标（可选）

将以下尺寸的图标文件放入 `icons/` 目录：
- `icon16.png` - 16x16 像素
- `icon48.png` - 48x48 像素
- `icon128.png` - 128x128 像素

如果没有图标，可以使用任意 PNG 图片，或者注释掉 manifest.json 中的 icons 配置。

### 2. 加载插件

1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/`
3. 开启右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `chrome-extension` 目录

### 3. 验证安装

安装成功后，浏览器工具栏会出现插件图标（如果配置了图标）。

## 使用方法

### 1. 捕获埋点数据

1. 访问包含埋点的网页（如 3d66.com）
2. 插件会自动监听并捕获 tpdi 请求
3. 图标右上角的徽章会显示捕获数量

### 2. 查看数据

1. 点击插件图标打开弹窗
2. 查看捕获的埋点列表
3. 点击任意埋点查看详情

### 3. 使用 MCP 分析

**方式 1：复制 MCP 命令**
1. 在详情弹窗中点击"复制 MCP 命令"
2. 打开 Claude Code 或 Cursor
3. 粘贴并发送

**方式 2：手动调用**
1. 复制事件名称或 JSON 数据
2. 在 Claude Code/Cursor 中使用 MCP 工具：
   - `query_event_fields` - 查询字段定义
   - `analyze_tracking_data` - 分析数据
   - `explain_field` - 解释字段

## 技术实现

### Manifest V3

使用 Chrome Extension Manifest V3 规范：
- Service Worker 后台运行
- webRequest API 监听网络请求
- chrome.storage.local 存储数据

### 网络监听

```javascript
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    if (details.url.includes('tpdi')) {
      // 处理请求
    }
  },
  { urls: ["<all_urls>"] }
);
```

### Base64 解码

支持 URL 编码 + Base64 双重编码：
```javascript
decodeURIComponent(data) → atob() → JSON.parse()
```

## 文件结构

```
chrome-extension/
├── manifest.json           # Manifest V3 配置
├── background.js           # Service Worker（网络监听）
├── popup/
│   ├── popup.html         # 弹窗界面
│   ├── popup.js           # 弹窗逻辑
│   └── popup.css          # 样式
├── utils/
│   └── decoder.js         # Base64 解码工具
└── icons/                 # 图标（需自行添加）
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## 注意事项

1. **权限要求** - 插件需要访问所有网站的权限以监听网络请求
2. **数据存储** - 最多存储 100 条埋点数据，超过会自动删除最旧的
3. **性能影响** - 监听网络请求可能有轻微性能影响
4. **隐私保护** - 所有数据仅存储在本地，不会上传到任何服务器

## 故障排除

### 插件无法加载
- 检查 manifest.json 语法是否正确
- 确保所有引用的文件都存在

### 无法捕获埋点
- 确认网页确实发送了包含 `tpdi` 的请求
- 检查浏览器控制台是否有错误
- 尝试刷新网页重新触发埋点

### 图标不显示
- 确保 icons 目录下有对应的图标文件
- 或者注释掉 manifest.json 中的 icons 配置

## 开发调试

1. 打开 `chrome://extensions/`
2. 找到插件，点击"检查视图：Service Worker"
3. 在控制台查看日志

## 更新日志

### v1.0.0 (2025-01-16)
- 初始版本
- 支持 tpdi 请求监听
- Base64 数据解码
- 可视化界面
- MCP 集成

## 作者

Generated with Claude Code

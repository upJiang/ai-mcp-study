#!/usr/bin/env node
// 关于 IDE 显示的 Server 弃用警告：这只是一个提示（Hint），不影响功能。MCP SDK 可能在新版本中推荐了其他 API，但当前代码完全可以正常工作。如果后续需要升级，可以查看 MCP SDK 文档了解新的推荐用法。
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { collectImages } from "./collector.js";

// 创建 MCP 服务器
const server = new Server(
  {
    name: "image-collector",
    version: "1.2.1",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 定义工具列表
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "collect_images",
        description:
          "采集指定网页上的所有 jpg/png 图片并保存到桌面。打开浏览器访问网页，提取所有图片链接，下载到本地。",
        inputSchema: {
          type: "object" as const,
          properties: {
            url: {
              type: "string",
              description: "要采集图片的网页地址",
            },
          },
          required: ["url"],
        },
      },
    ],
  };
});

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "collect_images") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const args = request.params.arguments as { url: string };
  const targetUrl = args.url;

  if (!targetUrl) {
    return {
      content: [
        {
          type: "text" as const,
          text: "错误：请提供要采集图片的网页地址",
        },
      ],
    };
  }

  const result = await collectImages(targetUrl);

  return {
    content: [
      {
        type: "text" as const,
        text: result.message,
      },
    ],
  };
});

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Image Collector MCP Server running on stdio");
}

main().catch(console.error);

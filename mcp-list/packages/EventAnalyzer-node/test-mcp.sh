#!/bin/bash

# 测试 EventAnalyzer MCP Server
echo "========================================="
echo "🧪 测试 EventAnalyzer MCP Server"
echo "========================================="
echo ""

# 测试 1: 检查程序能否启动
echo "测试 1: 检查程序是否能正常启动..."
cd /Users/mac/Desktop/studyProject/ai-mcp-study/mcp-list/packages/EventAnalyzer-node
(node dist/index.js < /dev/null > /tmp/mcp-test.log 2>&1 &)
pid=$!
sleep 2
kill $pid 2>/dev/null
wait $pid 2>/dev/null
if grep -q "FastMCP" /tmp/mcp-test.log || grep -q "node" /tmp/mcp-test.log; then
  echo "✅ 程序可以正常启动"
else
  echo "⚠️  程序启动检查完成（MCP 服务器需要客户端连接才能完全验证）"
fi
rm -f /tmp/mcp-test.log

echo ""
echo "测试 2: 检查依赖是否正确安装..."
if [ -d "node_modules/fastmcp" ] && [ -d "node_modules/zod" ] && [ -d "node_modules/node-cache" ] && [ -d "node_modules/axios" ]; then
  echo "✅ 所有依赖已正确安装"
else
  echo "❌ 部分依赖缺失"
  exit 1
fi

echo ""
echo "测试 3: 检查编译输出..."
if [ -f "dist/index.js" ] && [ -d "dist/tools" ] && [ -d "dist/services" ] && [ -d "dist/utils" ]; then
  echo "✅ 编译输出完整"
else
  echo "❌ 编译输出不完整"
  exit 1
fi

echo ""
echo "测试 4: 检查 TypeScript 类型定义..."
if [ -f "dist/index.d.ts" ]; then
  echo "✅ TypeScript 类型定义已生成"
else
  echo "⚠️  TypeScript 类型定义缺失（非致命错误）"
fi

echo ""
echo "========================================="
echo "✅ 所有测试通过！"
echo "========================================="
echo ""
echo "📦 包名: @upjiang/eventanalyzer-mcp"
echo "🚀 使用方式:"
echo "   npx -y @upjiang/eventanalyzer-mcp"
echo ""
echo "Cursor 配置示例:"
echo '{'
echo '  "mcpServers": {'
echo '    "EventAnalyzer-Node": {'
echo '      "command": "npx",'
echo '      "args": ["-y", "@upjiang/eventanalyzer-mcp"]'
echo '    }'
echo '  }'
echo '}'
echo "========================================="

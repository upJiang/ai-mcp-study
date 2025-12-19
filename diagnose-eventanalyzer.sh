#!/bin/bash
# EventAnalyzer MCP 服务诊断和修复脚本

set -e

echo "========================================="
echo "🔍 EventAnalyzer MCP 服务诊断"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查 Docker 容器状态
echo "步骤 1/6: 检查 Docker 容器状态..."
if docker ps | grep -q "mcp-eventanalyzer"; then
    echo -e "${GREEN}✓ EventAnalyzer 容器正在运行${NC}"
    docker ps | grep "mcp-eventanalyzer"
else
    echo -e "${RED}✗ EventAnalyzer 容器未运行${NC}"
    echo "尝试查找已停止的容器..."
    docker ps -a | grep "eventanalyzer" || echo "未找到任何 eventanalyzer 容器"
fi
echo ""

# 2. 检查端口监听
echo "步骤 2/6: 检查端口 8100 监听状态..."
if ss -tlnp 2>/dev/null | grep -q ":8100"; then
    echo -e "${GREEN}✓ 端口 8100 正在监听${NC}"
    ss -tlnp | grep ":8100"
else
    echo -e "${RED}✗ 端口 8100 未监听${NC}"
fi
echo ""

# 3. 测试容器直接访问
echo "步骤 3/6: 测试容器直接访问..."
echo "GET http://127.0.0.1:8100/sse"
if curl -s -I http://127.0.0.1:8100/sse 2>&1 | head -1; then
    response=$(curl -s -I http://127.0.0.1:8100/sse 2>&1 | head -5)
    if echo "$response" | grep -q "200\|404"; then
        echo -e "${GREEN}✓ 容器可访问${NC}"
        echo "$response"
    else
        echo -e "${YELLOW}⚠️  容器返回异常响应${NC}"
        echo "$response"
    fi
else
    echo -e "${RED}✗ 无法访问容器${NC}"
fi
echo ""

# 4. 检查 Nginx 配置
echo "步骤 4/6: 检查 Nginx 配置..."
echo "查找 eventanalyzer 相关配置..."

found_config=false

# 检查 /etc/nginx/
if grep -r "location /mcp/eventanalyzer" /etc/nginx/ 2>/dev/null; then
    echo -e "${GREEN}✓ 在 /etc/nginx/ 中找到配置${NC}"
    found_config=true
fi

# 检查宝塔面板路径
if grep -r "location /mcp/eventanalyzer" /www/server/nginx/ 2>/dev/null; then
    echo -e "${GREEN}✓ 在 /www/server/nginx/ 中找到配置${NC}"
    found_config=true
fi

if [ "$found_config" = false ]; then
    echo -e "${RED}✗ 未找到 eventanalyzer nginx 配置${NC}"
fi
echo ""

# 5. 测试 Nginx 代理
echo "步骤 5/6: 测试 Nginx 代理..."
echo "GET https://junfeng530.xyz/mcp/eventanalyzer/sse"
response=$(curl -s -I https://junfeng530.xyz/mcp/eventanalyzer/sse 2>&1 | head -5)
if echo "$response" | grep -q "200"; then
    echo -e "${GREEN}✓ Nginx 代理工作正常${NC}"
elif echo "$response" | grep -q "404"; then
    echo -e "${RED}✗ Nginx 返回 404 错误${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx 返回异常响应${NC}"
fi
echo "$response"
echo ""

# 6. 查看最近的错误日志
echo "步骤 6/6: 查看最近的错误日志..."

# Docker 容器日志
echo "--- Docker 容器日志（最近 20 行）---"
if docker ps | grep -q "mcp-eventanalyzer"; then
    docker logs --tail=20 mcp-eventanalyzer 2>&1 || echo "无法获取容器日志"
else
    echo "容器未运行，无法查看日志"
fi
echo ""

# Nginx 错误日志
echo "--- Nginx 错误日志（最近 10 行）---"
if [ -f /var/log/nginx/error.log ]; then
    tail -10 /var/log/nginx/error.log
elif [ -f /www/wwwlogs/junfeng530.xyz.error.log ]; then
    tail -10 /www/wwwlogs/junfeng530.xyz.error.log
else
    echo "未找到 Nginx 错误日志"
fi
echo ""

# 诊断总结
echo "========================================="
echo "📊 诊断总结"
echo "========================================="

problems=()
solutions=()

# 检查容器状态
if ! docker ps | grep -q "mcp-eventanalyzer"; then
    problems+=("Docker 容器未运行")
    solutions+=("重启容器：cd /opt/mcp-services/ai-mcp-study/mcp-list && docker-compose up -d eventanalyzer")
fi

# 检查端口
if ! ss -tlnp 2>/dev/null | grep -q ":8100"; then
    problems+=("端口 8100 未监听")
    solutions+=("检查容器端口映射或重启容器")
fi

# 检查 Nginx 配置
if [ "$found_config" = false ]; then
    problems+=("Nginx 配置缺失")
    solutions+=("运行 nginx 配置更新脚本：bash fix-nginx-mcp.sh")
fi

# 检查公网访问
if echo "$response" | grep -q "404"; then
    problems+=("Nginx 返回 404")
    solutions+=("重载 Nginx 配置：sudo nginx -t && sudo nginx -s reload")
fi

if [ ${#problems[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ 没有发现明显问题${NC}"
    echo ""
    echo "如果 Cursor 仍无法连接，请检查："
    echo "1. Cursor 配置文件 ~/.cursor/mcp.json"
    echo "2. 确保 URL 为: https://junfeng530.xyz/mcp/eventanalyzer/sse"
    echo "3. 完全重启 Cursor (Cmd+Q 然后重新打开)"
else
    echo -e "${YELLOW}⚠️  发现以下问题：${NC}"
    echo ""
    for i in "${!problems[@]}"; do
        echo "  ${problems[$i]}"
    done
    echo ""
    echo -e "${GREEN}💡 建议的修复步骤：${NC}"
    echo ""
    for i in "${!solutions[@]}"; do
        echo "  $((i+1)). ${solutions[$i]}"
    done
fi

echo ""
echo "========================================="
echo "结束诊断"
echo "========================================="

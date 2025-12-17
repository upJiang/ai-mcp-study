#!/bin/bash
# Nginx 配置诊断脚本

NGINX_CONF="/www/server/nginx/conf/nginx.conf"

echo "========================================="
echo "🔍 Nginx 配置诊断"
echo "========================================="
echo ""

# 1. 检查 nginx.conf 是否存在
echo "1️⃣ 检查配置文件..."
if [ -f "$NGINX_CONF" ]; then
    echo "✓ 配置文件存在: $NGINX_CONF"
    echo "  文件大小: $(wc -c < "$NGINX_CONF") 字节"
    echo "  总行数: $(wc -l < "$NGINX_CONF") 行"
else
    echo "❌ 配置文件不存在!"
    exit 1
fi
echo ""

# 2. 检查 http 块结构
echo "2️⃣ 检查 http 块结构..."
http_start=$(grep -n "^http" "$NGINX_CONF" | head -1 | cut -d: -f1)
http_bracket=$(grep -n "^    {" "$NGINX_CONF" | head -1 | cut -d: -f1)

if [ -n "$http_start" ]; then
    echo "✓ http 块开始于第 $http_start 行"
else
    echo "❌ 未找到 http 块!"
fi
echo ""

# 3. 检查 server 块
echo "3️⃣ 检查 server 块..."
echo "找到的 server 块："
grep -n "server_name" "$NGINX_CONF" | head -5
echo ""

# 4. 检查 MCP 配置
echo "4️⃣ 检查 MCP EventAnalyzer 配置..."
if grep -q "/mcp/eventanalyzer" "$NGINX_CONF"; then
    echo "✓ 找到 MCP EventAnalyzer 路由"
    echo ""
    echo "配置详情："
    grep -A 5 "/mcp/eventanalyzer" "$NGINX_CONF" | head -10
    echo ""

    # 检查使用的是容器名还是 localhost
    if grep -q "proxy_pass http://mcp-eventanalyzer:8000" "$NGINX_CONF"; then
        echo "⚠️  当前使用容器名: mcp-eventanalyzer:8000"
        echo "   需要改为: 127.0.0.1:8100"
    elif grep -q "proxy_pass http://127.0.0.1:8100" "$NGINX_CONF"; then
        echo "✓ 已使用 localhost: 127.0.0.1:8100"
    else
        echo "⚠️  使用了其他代理地址"
        grep "proxy_pass" "$NGINX_CONF" | grep eventanalyzer
    fi
else
    echo "❌ 未找到 MCP EventAnalyzer 配置"
fi
echo ""

# 5. 检查第 222 行（报错位置）
echo "5️⃣ 检查第 222 行（nginx 报错位置）..."
if [ $(wc -l < "$NGINX_CONF") -ge 222 ]; then
    echo "第 220-225 行内容："
    sed -n '220,225p' "$NGINX_CONF" | cat -n
    echo ""

    # 检查第 222 行的上下文
    echo "检查第 222 行所在的块..."

    # 向上查找最近的 server { 或 http { 或 location {
    context=$(sed -n '1,222p' "$NGINX_CONF" | tac | grep -m 1 -E "(server|http|location)" | head -1)
    echo "最近的块声明: $context"
else
    echo "⚠️  文件只有 $(wc -l < "$NGINX_CONF") 行，第 222 行不存在"
fi
echo ""

# 6. 检查大括号配对
echo "6️⃣ 检查大括号配对..."
open_braces=$(grep -o "{" "$NGINX_CONF" | wc -l)
close_braces=$(grep -o "}" "$NGINX_CONF" | wc -l)
echo "开括号数量: $open_braces"
echo "闭括号数量: $close_braces"

if [ "$open_braces" -eq "$close_braces" ]; then
    echo "✓ 括号配对正确"
else
    echo "❌ 括号配对不匹配!"
fi
echo ""

# 7. 运行 nginx -t 查看具体错误
echo "7️⃣ 运行 nginx -t 检查语法..."
echo "----------------------------------------"
sudo nginx -t 2>&1 || true
echo "----------------------------------------"
echo ""

echo "========================================="
echo "诊断完成"
echo "========================================="
echo ""
echo "💡 建议："
echo ""
echo "如果看到 'host not found in upstream' 错误："
echo "  → 运行: bash fix-nginx-minimal.sh"
echo ""
echo "如果看到 'location directive is not allowed' 错误："
echo "  → 检查 location 块是否在 server 块内部"
echo "  → 可能需要手动编辑 nginx.conf"
echo ""
echo "如果看到 'conflicting server name' 警告："
echo "  → 检查是否有重复的 server_name 配置"
echo "  → 需要合并或删除重复的 server 块"
echo ""

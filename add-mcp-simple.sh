#!/bin/bash
# 简单直接地在 location / 之前添加 MCP location 块

set -e

NGINX_CONF="/www/server/nginx/conf/nginx.conf"
BACKUP_CONF="/www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)"

echo "========================================="
echo "📝 添加 MCP EventAnalyzer 配置（简化版）"
echo "========================================="
echo ""

# 1. 备份
echo "步骤 1/3: 备份现有配置..."
sudo cp "$NGINX_CONF" "$BACKUP_CONF"
echo "✓ 备份完成: $BACKUP_CONF"
echo ""

# 2. 检查是否已存在
echo "步骤 2/3: 检查是否已存在 MCP 配置..."
if grep -q "location /mcp/eventanalyzer" "$NGINX_CONF"; then
    echo "⚠️  MCP EventAnalyzer 配置已存在"
    exit 0
fi
echo "✓ 确认未找到重复配置"
echo ""

# 3. 使用 sed 直接在 "location /" 之前插入配置
echo "步骤 3/3: 在 server 块中添加 MCP location..."

# 创建插入内容
cat > /tmp/mcp-insert.txt << 'EOF'

    # MCP EventAnalyzer 服务 ✨ 新增\
    location /mcp/eventanalyzer {\
        rewrite ^/mcp/eventanalyzer$ /sse break;\
        rewrite ^/mcp/eventanalyzer(/.*)?$ $1 break;\
        proxy_pass http://127.0.0.1:8100;\
\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
\
        proxy_buffering off;\
        proxy_cache off;\
        proxy_set_header Connection '';\
        proxy_http_version 1.1;\
        chunked_transfer_encoding on;\
\
        proxy_connect_timeout 300s;\
        proxy_send_timeout 300s;\
        proxy_read_timeout 300s;\
\
        add_header Access-Control-Allow-Origin * always;\
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS' always;\
        add_header Access-Control-Allow-Headers 'Content-Type, Authorization' always;\
\
        if ($request_method = 'OPTIONS') {\
            return 204;\
        }\
    }\
\
EOF

# 找到包含 "location /" 且在 server_name junfeng530.xyz 之后的第一个匹配
# 在它之前插入 MCP location 块
sudo sed -i.sedback '/server_name junfeng530.xyz/,/location \/ {/s|location / {|    # MCP EventAnalyzer 服务 ✨ 新增\n    location /mcp/eventanalyzer {\n        rewrite ^/mcp/eventanalyzer$ /sse break;\n        rewrite ^/mcp/eventanalyzer(/.*)?$ $1 break;\n        proxy_pass http://127.0.0.1:8100;\n\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        proxy_set_header X-Forwarded-Proto $scheme;\n\n        proxy_buffering off;\n        proxy_cache off;\n        proxy_set_header Connection '\'''\'';\n        proxy_http_version 1.1;\n        chunked_transfer_encoding on;\n\n        proxy_connect_timeout 300s;\n        proxy_send_timeout 300s;\n        proxy_read_timeout 300s;\n\n        add_header Access-Control-Allow-Origin * always;\n        add_header Access-Control-Allow-Methods '\''GET, POST, OPTIONS'\'' always;\n        add_header Access-Control-Allow-Headers '\''Content-Type, Authorization'\'' always;\n\n        if ($request_method = '\''OPTIONS'\'') {\n            return 204;\n        }\n    }\n\n    location / {|' "$NGINX_CONF"

rm -f /tmp/mcp-insert.txt

echo "✓ MCP location 块已添加"
echo ""

# 4. 验证修改
echo "验证修改..."
if grep -q "location /mcp/eventanalyzer" "$NGINX_CONF"; then
    echo "✓ 确认 MCP location 块已添加"
    echo ""
    echo "新增配置预览："
    grep -A 10 "location /mcp/eventanalyzer" "$NGINX_CONF" | head -15
else
    echo "❌ 未能添加配置"
    sudo cp "$BACKUP_CONF" "$NGINX_CONF"
    echo "已恢复备份"
    exit 1
fi
echo ""

# 5. 测试配置
echo "========================================="
echo "测试 Nginx 配置..."
echo "========================================="
if sudo nginx -t; then
    echo ""
    echo "✅ Nginx 配置测试通过！"
    echo ""
    echo "下一步："
    echo "1. 重载 Nginx: sudo systemctl reload nginx"
    echo "2. 测试访问: curl -I https://junfeng530.xyz/mcp/eventanalyzer"
else
    echo ""
    echo "❌ Nginx 配置测试失败"
    echo ""
    echo "正在恢复备份..."
    sudo cp "$BACKUP_CONF" "$NGINX_CONF"
    echo "✓ 已恢复到备份版本"
    exit 1
fi

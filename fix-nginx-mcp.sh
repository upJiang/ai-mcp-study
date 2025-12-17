#!/bin/bash
# 修复 MCP EventAnalyzer 的 Nginx 配置
# 使 GET /mcp/eventanalyzer 路由到 /sse
# 使 POST /mcp/eventanalyzer 路由到 /messages

set -e

NGINX_CONF="/www/server/nginx/conf/nginx.conf"
BACKUP_CONF="/www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)"

echo "========================================="
echo "📝 修复 MCP EventAnalyzer Nginx 配置"
echo "========================================="
echo ""

# 1. 备份
echo "步骤 1/4: 备份现有配置..."
sudo cp "$NGINX_CONF" "$BACKUP_CONF"
echo "✓ 备份完成: $BACKUP_CONF"
echo ""

# 2. 删除旧的 MCP location 块
echo "步骤 2/4: 删除旧的 MCP location 块..."
sudo sed -i.bak '/# MCP EventAnalyzer 服务/,/^    }/d' "$NGINX_CONF"
echo "✓ 旧配置已删除"
echo ""

# 3. 创建新的 MCP location 块（支持 GET 和 POST 到同一路径）
echo "步骤 3/4: 添加新的 MCP location 块..."

cat > /tmp/mcp-eventanalyzer-fixed.conf << 'EOF'

    # MCP EventAnalyzer 服务 ✨ 修复版
    location /mcp/eventanalyzer {
        # GET 请求路由到 /sse (SSE 连接)
        # POST 请求路由到 /messages (发送消息)
        set $target_path "/sse";
        if ($request_method = POST) {
            set $target_path "/messages";
        }

        rewrite ^ $target_path break;
        proxy_pass http://127.0.0.1:8100;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 特定配置
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;

        # 超时配置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # CORS 配置
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS' always;
        add_header Access-Control-Allow-Headers 'Content-Type, Authorization' always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
EOF

# 在 server_name junfeng530.xyz 的 server 块中，在第一个 location / 之前插入
awk '
BEGIN { in_target_server=0; inserted=0 }
{
    # 检测到目标 server 块
    if ($0 ~ /server_name junfeng530.xyz/) {
        in_target_server = 1
    }

    # 在目标 server 块内找到第一个 location /
    if (in_target_server && !inserted && $0 ~ /location \/ \{/) {
        # 在 location / 之前插入 MCP location 块
        system("cat /tmp/mcp-eventanalyzer-fixed.conf")
        inserted = 1
        in_target_server = 0
    }

    # 输出原始行
    print
}
' "$NGINX_CONF" > /tmp/nginx.conf.new

sudo cp /tmp/nginx.conf.new "$NGINX_CONF"
rm -f /tmp/nginx.conf.new /tmp/mcp-eventanalyzer-fixed.conf

echo "✓ 新配置已添加"
echo ""

# 4. 测试配置
echo "步骤 4/4: 测试 Nginx 配置..."
echo "========================================="
if sudo nginx -t; then
    echo ""
    echo "✅ Nginx 配置测试通过！"
    echo ""
    echo "下一步："
    echo "1. 重载 Nginx: sudo systemctl reload nginx"
    echo "2. 重启容器: cd /opt/mcp-services/ai-mcp-study/mcp-list && docker-compose restart eventanalyzer"
    echo "3. 测试连接: curl -v https://junfeng530.xyz/mcp/eventanalyzer"
else
    echo ""
    echo "❌ Nginx 配置测试失败"
    echo ""
    echo "正在恢复备份..."
    sudo cp "$BACKUP_CONF" "$NGINX_CONF"
    echo "✓ 已恢复到备份版本"
    exit 1
fi

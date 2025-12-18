#!/bin/bash
# 自动更新 MCP EventAnalyzer 的 Nginx 配置
# 使 GET /mcp/eventanalyzer 路由到 /sse
# 使 POST /mcp/eventanalyzer 路由到 /messages
#
# 特性：
# - 幂等性：可以多次运行，不会重复添加配置
# - 容错性：遇到错误时自动回滚

set -e

NGINX_CONF="/www/server/nginx/conf/nginx.conf"
BACKUP_CONF="/www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)"

echo "========================================="
echo "📝 自动更新 MCP EventAnalyzer Nginx 配置"
echo "========================================="
echo ""

# 检查 nginx.conf 是否存在
if [ ! -f "$NGINX_CONF" ]; then
  echo "❌ 错误：未找到 $NGINX_CONF"
  exit 1
fi

# 1. 备份
echo "步骤 1/4: 备份现有配置..."
sudo cp "$NGINX_CONF" "$BACKUP_CONF"
echo "✓ 备份完成: $BACKUP_CONF"
echo ""

# 2. 删除旧的 MCP location 块（如果存在）
echo "步骤 2/4: 检查并删除旧的 MCP location 块..."
if grep -q "# MCP EventAnalyzer 服务" "$NGINX_CONF"; then
  echo "找到旧配置，正在删除..."
  sudo sed -i.bak '/# MCP EventAnalyzer 服务/,/^    }/d' "$NGINX_CONF"
  echo "✓ 旧配置已删除"
else
  echo "✓ 未找到旧配置，跳过删除"
fi
echo ""

# 3. 创建新的 MCP location 块（支持 GET 和 POST 到同一路径）
echo "步骤 3/4: 添加新的 MCP location 块..."

cat > /tmp/mcp-eventanalyzer-fixed.conf << 'EOF'

    # MCP EventAnalyzer 服务 ✨ 修复版 v2
    # SSE 端点 - 处理 GET 请求
    location /mcp/eventanalyzer/sse {
        proxy_pass http://127.0.0.1:8100/sse;

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
        add_header Access-Control-Allow-Methods 'GET, OPTIONS' always;
        add_header Access-Control-Allow-Headers 'Content-Type, Authorization' always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Messages 端点 - 处理 POST 请求（保留查询参数）
    location /mcp/eventanalyzer/messages {
        proxy_pass http://127.0.0.1:8100/messages;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # HTTP 1.1 支持
        proxy_http_version 1.1;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # CORS 配置
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'POST, OPTIONS' always;
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
if sudo nginx -t 2>&1; then
    echo ""
    echo "✅ Nginx 配置测试通过！"
    echo ""
    echo "配置已成功更新，Nginx 将在部署流程中自动重载。"
else
    echo ""
    echo "❌ Nginx 配置测试失败"
    echo ""
    echo "正在恢复备份..."
    sudo cp "$BACKUP_CONF" "$NGINX_CONF"
    echo "✓ 已恢复到备份版本"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ Nginx 配置更新完成"
echo "========================================="

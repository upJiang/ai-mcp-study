#!/bin/bash
# 在 junfeng530.xyz server 块内部添加 MCP EventAnalyzer location 块

set -e

NGINX_CONF="/www/server/nginx/conf/nginx.conf"
BACKUP_CONF="/www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)"

echo "========================================="
echo "📝 添加 MCP EventAnalyzer 配置"
echo "========================================="
echo ""

# 1. 备份
echo "步骤 1/4: 备份现有配置..."
sudo cp "$NGINX_CONF" "$BACKUP_CONF"
echo "✓ 备份完成: $BACKUP_CONF"
echo ""

# 2. 检查是否已存在 MCP 配置
echo "步骤 2/4: 检查是否已存在 MCP 配置..."
if grep -q "location /mcp/eventanalyzer" "$NGINX_CONF"; then
    echo "⚠️  MCP EventAnalyzer 配置已存在，跳过添加"
    echo ""
    echo "如需重新添加，请先手动删除现有配置"
    exit 0
fi
echo "✓ 确认未找到重复配置"
echo ""

# 3. 创建 MCP location 块配置
echo "步骤 3/4: 准备 MCP location 块..."
cat > /tmp/mcp-eventanalyzer-location.conf << 'EOF'

    # MCP EventAnalyzer 服务 ✨ 新增
    location /mcp/eventanalyzer {
        rewrite ^/mcp/eventanalyzer$ /sse break;
        rewrite ^/mcp/eventanalyzer(/.*)?$ $1 break;
        proxy_pass http://127.0.0.1:8100;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS' always;
        add_header Access-Control-Allow-Headers 'Content-Type, Authorization' always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
EOF
echo "✓ MCP location 块已准备"
echo ""

# 4. 添加到 server 块内部（在最后一个 location 块之后、server 块结束之前）
echo "步骤 4/4: 添加到 server_name junfeng530.xyz 的 server 块..."

# 使用 awk 在 server 块内的最后一个 } 之前插入配置
awk '
BEGIN { in_target_server=0; brace_count=0; inserted=0 }
{
    # 检测到目标 server 块
    if ($0 ~ /server_name junfeng530.xyz/) {
        in_target_server = 1
        brace_count = 0
    }

    # 在目标 server 块内部
    if (in_target_server) {
        # 统计大括号
        for (i=1; i<=length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") brace_count++
            if (c == "}") brace_count--
        }

        # 如果遇到 server 块的闭括号（brace_count 回到 0）
        if (brace_count == 0 && $0 ~ /^}/ && !inserted) {
            # 在闭括号之前插入 MCP location 块
            system("cat /tmp/mcp-eventanalyzer-location.conf")
            inserted = 1
            in_target_server = 0
        }
    }

    # 输出原始行
    print
}
' "$NGINX_CONF" > /tmp/nginx.conf.new

# 替换原文件
sudo cp /tmp/nginx.conf.new "$NGINX_CONF"
rm -f /tmp/nginx.conf.new /tmp/mcp-eventanalyzer-location.conf

echo "✓ MCP location 块已添加到 server 块"
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
    echo ""
    echo "如需回滚："
    echo "sudo cp $BACKUP_CONF $NGINX_CONF"
    echo "sudo systemctl reload nginx"
else
    echo ""
    echo "❌ Nginx 配置测试失败"
    echo ""
    echo "正在恢复备份..."
    sudo cp "$BACKUP_CONF" "$NGINX_CONF"
    echo "✓ 已恢复到备份版本"
    echo ""
    echo "请查看上方错误信息"
    exit 1
fi

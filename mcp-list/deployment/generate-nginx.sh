#!/bin/bash
# 自动生成 Nginx 配置（支持动态服务发现）

set -e

TEMPLATE_FILE="./deployment/nginx/mcp-services.conf.template"
OUTPUT_FILE="./deployment/nginx/mcp-services.conf"
DOCKER_COMPOSE_FILE="./docker-compose.yml"

echo "========================================="
echo "自动生成 Nginx 配置"
echo "========================================="

# 检查文件是否存在
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ 错误: 模板文件不存在: $TEMPLATE_FILE"
    exit 1
fi

if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "❌ 错误: docker-compose.yml 不存在"
    echo "提示: 请先运行 generate-compose.sh 生成 docker-compose.yml"
    exit 1
fi

# 获取所有服务名称
echo "扫描 docker-compose.yml 中的服务..."
services=$(grep "container_name: mcp-" "$DOCKER_COMPOSE_FILE" | sed 's/.*mcp-//' || echo "")

if [ -z "$services" ]; then
    echo "⚠️  警告: 未找到任何 Python MCP 服务"
    services=""
fi

# 生成 location 块
locations=""
SERVICE_COUNT=0

for service in $services; do
    echo "✓ 发现服务: $service"
    SERVICE_COUNT=$((SERVICE_COUNT + 1))

    # 将服务名转换为 URL 路径
    url_path="/mcp/$service"
    container_name="mcp-$service"

    # 从 docker-compose.yml 中读取端口映射（格式：XXXX:8000）
    host_port=$(grep -A 20 "container_name: $container_name" "$DOCKER_COMPOSE_FILE" | grep -m 1 "ports:" -A 1 | grep -oE '[0-9]+:8000' | cut -d':' -f1 || echo "8000")

    if [ -z "$host_port" ]; then
        host_port="8000"
    fi

    # 生成 location 块（支持 SSE，使用 localhost）
    location_block="
    # $service
    location $url_path {
        # 默认访问根路径时，代理到 /sse
        rewrite ^$url_path\$ /sse break;
        rewrite ^$url_path(/.*)?\$ \$1 break;
        proxy_pass http://127.0.0.1:$host_port;

        # 基础代理头
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # SSE 支持（Server-Sent Events）
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;

        # 长连接超时（SSE 需要）
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # CORS 支持（如果需要跨域）
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS' always;
        add_header Access-Control-Allow-Headers 'Content-Type, Authorization' always;

        if (\$request_method = 'OPTIONS') {
            return 204;
        }
    }
"

    locations="$locations$location_block"
done

# 读取模板并替换占位符
echo ""
echo "生成最终配置文件..."
template_content=$(cat "$TEMPLATE_FILE")

# 替换占位符
final_config="${template_content//%%MCP_LOCATIONS%%/$locations}"

# 写入输出文件
echo "$final_config" > "$OUTPUT_FILE"

echo "✓ Nginx 配置生成完成"
echo ""
echo "📊 统计："
echo "  - 服务数量: $SERVICE_COUNT"
echo "  - 输出文件: $OUTPUT_FILE"
echo ""
echo "生成的服务路由："
for service in $services; do
    container_name="mcp-$service"
    host_port=$(grep -A 20 "container_name: $container_name" "$DOCKER_COMPOSE_FILE" | grep -m 1 "ports:" -A 1 | grep -oE '[0-9]+:8000' | cut -d':' -f1 || echo "8000")
    echo "  - https://junfeng530.xyz/mcp/$service → 127.0.0.1:$host_port"
done
echo ""
echo "========================================="
echo ""
echo "下一步："
echo "1. 复制配置到 Nginx: sudo cp $OUTPUT_FILE /etc/nginx/conf.d/"
echo "2. 测试配置: sudo nginx -t"
echo "3. 重载 Nginx: sudo systemctl reload nginx"

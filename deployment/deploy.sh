#!/bin/bash
# MCP 服务部署脚本

set -e

DEPLOY_DIR="/opt/mcp-services/ai-mcp-study"
MCP_DIR="$DEPLOY_DIR/mcp-list"

echo "========================================="
echo "开始部署 MCP 服务"
echo "========================================="

# 1. 进入工作目录
cd $DEPLOY_DIR

# 2. 拉取最新代码
echo "步骤 1/7: 拉取最新代码..."
git pull origin main
echo "✓ 代码更新完成"

# 3. 自动生成 docker-compose.yml
echo "步骤 2/7: 自动生成 docker-compose.yml..."
cd $MCP_DIR
chmod +x deployment/generate-compose.sh
./deployment/generate-compose.sh
echo "✓ docker-compose.yml 生成完成"

# 4. 自动生成 Nginx 配置
echo "步骤 3/7: 自动生成 Nginx 配置..."
chmod +x deployment/generate-nginx.sh
./deployment/generate-nginx.sh
echo "✓ Nginx 配置生成完成"

# 5. 部署 Nginx 配置并重载
echo "步骤 4/7: 更新 Nginx 配置..."
sudo cp deployment/nginx/mcp-services.conf /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl reload nginx
echo "✓ Nginx 配置已更新"

# 6. 跳过环境变量检查（各包自己管理）
echo "步骤 5/7: 跳过环境变量检查..."
echo "ℹ️  如果包需要配置，请在包目录下创建 .env 文件"
echo "✓ 继续部署"

# 7. 停止旧容器
echo "步骤 6/7: 停止旧容器..."
docker-compose down || true
echo "✓ 旧容器已停止"

# 8. 构建并启动新容器（带容错）
echo "步骤 7/7: 构建并启动新容器..."

# 获取所有服务
services=$(docker-compose config --services 2>/dev/null || echo "")

if [ -z "$services" ]; then
    echo "⚠️  警告: 未找到任何服务"
    echo "提示: 检查 docker-compose.yml 是否正确生成"
    exit 1
fi

SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_SERVICES=""

# 逐个处理服务（容错）
for service in $services; do
    echo ""
    echo "🔨 处理服务: $service"

    # 构建
    if docker-compose build --no-cache "$service" 2>&1; then
        echo "✓ $service 构建成功"

        # 启动
        if docker-compose up -d "$service" 2>&1; then
            echo "✓ $service 启动成功"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "✗ $service 启动失败"
            FAILED_COUNT=$((FAILED_COUNT + 1))
            FAILED_SERVICES="$FAILED_SERVICES $service"
        fi
    else
        echo "✗ $service 构建失败，跳过启动"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_SERVICES="$FAILED_SERVICES $service"
    fi
done

echo ""
echo "📊 部署统计："
echo "  ✓ 成功: $SUCCESS_COUNT"
echo "  ✗ 失败: $FAILED_COUNT"

if [ $FAILED_COUNT -gt 0 ]; then
    echo "  ⚠️  失败的服务:$FAILED_SERVICES"
fi

# 9. 验证服务（容错版本）
echo ""
echo "验证服务健康状态..."
sleep 5

check_service() {
    local name=$1
    local container=$2

    # 检查容器是否存在并运行
    if ! docker ps | grep -q "$container"; then
        echo "✗ $name - 容器未运行"
        return 1
    fi

    # 健康检查
    if docker exec "$container" curl -sf http://localhost:8000 > /dev/null 2>&1; then
        echo "✓ $name - 运行正常"
        return 0
    else
        echo "⚠️  $name - 健康检查失败（可能仍在启动中）"
        return 1
    fi
}

# 检查所有服务（不中断）
HEALTHY=0
UNHEALTHY=0

for service in $services; do
    container="mcp-$service"
    if check_service "$service" "$container"; then
        HEALTHY=$((HEALTHY + 1))
    else
        UNHEALTHY=$((UNHEALTHY + 1))
    fi
done

echo ""
echo "健康检查统计："
echo "  ✓ 健康: $HEALTHY"
echo "  ✗ 异常: $UNHEALTHY"

echo ""
echo "========================================="
if [ $FAILED_COUNT -eq 0 ] && [ $UNHEALTHY -eq 0 ]; then
    echo "✓ 部署完成！所有服务运行正常"
elif [ $SUCCESS_COUNT -gt 0 ]; then
    echo "⚠️  部署完成，但部分服务失败"
    echo "建议检查失败的服务日志"
else
    echo "❌ 部署失败！所有服务都失败了"
    exit 1
fi
echo "========================================="
echo ""
echo "服务访问地址："
for service in $services; do
    echo "  - $service: https://junfeng530.xyz/mcp/$service"
done
echo ""
echo "查看日志: docker-compose logs -f [service-name]"
echo "查看状态: docker-compose ps"

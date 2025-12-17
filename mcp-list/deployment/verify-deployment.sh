#!/bin/bash
# 快速验证部署脚本

echo "========================================="
echo "🔍 EventAnalyzer 部署验证"
echo "========================================="
echo ""

# 1. 检查容器状态
echo "1️⃣ 检查 Docker 容器状态..."
docker-compose ps | grep eventanalyzer
echo ""

# 2. 检查容器日志
echo "2️⃣ 最近 20 行容器日志..."
docker-compose logs --tail=20 eventanalyzer
echo ""

# 3. 检查容器内部端口
echo "3️⃣ 测试容器内部端点..."
docker exec mcp-eventanalyzer curl -s http://localhost:8000/sse || echo "❌ 容器内部端点不可访问"
echo ""

# 4. 检查 Nginx 配置
echo "4️⃣ 检查 Nginx 配置..."
grep -A 20 "eventanalyzer" /etc/nginx/conf.d/mcp-services.conf || echo "❌ Nginx 配置不存在"
echo ""

# 5. 测试 Nginx 配置语法
echo "5️⃣ 测试 Nginx 配置..."
sudo nginx -t
echo ""

# 6. 测试外部访问
echo "6️⃣ 测试外部 HTTPS 访问..."
curl -I https://junfeng530.xyz/mcp/eventanalyzer 2>&1 | head -5
echo ""

echo "========================================="
echo "🔧 如果有问题，运行以下命令修复："
echo "========================================="
echo ""
echo "# 重新生成 Nginx 配置"
echo "cd /opt/mcp-services/ai-mcp-study/mcp-list"
echo "./deployment/generate-nginx.sh"
echo "sudo cp deployment/nginx/mcp-services.conf /etc/nginx/conf.d/"
echo "sudo nginx -t && sudo systemctl reload nginx"
echo ""
echo "# 重启容器"
echo "docker-compose restart eventanalyzer"
echo ""
echo "# 查看详细日志"
echo "docker-compose logs -f eventanalyzer"
echo ""

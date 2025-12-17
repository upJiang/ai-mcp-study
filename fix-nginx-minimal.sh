#!/bin/bash
# 最小化修复脚本 - 只修改 MCP EventAnalyzer 配置中的容器名为 localhost

set -e

NGINX_CONF="/www/server/nginx/conf/nginx.conf"
BACKUP_CONF="/www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)"

echo "========================================="
echo "🔧 最小化 Nginx 配置修复"
echo "========================================="
echo ""

# 1. 备份当前配置
echo "步骤 1/4: 备份现有配置..."
sudo cp "$NGINX_CONF" "$BACKUP_CONF"
echo "✓ 备份完成: $BACKUP_CONF"
echo ""

# 2. 检查是否存在容器名配置
echo "步骤 2/4: 检查现有配置..."
if grep -q "proxy_pass http://mcp-eventanalyzer:8000" "$NGINX_CONF"; then
    echo "✓ 找到需要修复的配置"
else
    echo "⚠️  未找到容器名配置，可能已经修复或配置不存在"
    exit 0
fi
echo ""

# 3. 替换容器名为 localhost
echo "步骤 3/4: 替换容器名为 localhost..."
sudo sed -i.bak 's|proxy_pass http://mcp-eventanalyzer:8000|proxy_pass http://127.0.0.1:8100|g' "$NGINX_CONF"
echo "✓ 替换完成"
echo ""

# 4. 测试配置
echo "步骤 4/4: 测试 Nginx 配置..."
if sudo nginx -t; then
    echo "✓ Nginx 配置测试通过"
    echo ""
    echo "========================================="
    echo "✅ 修复成功！"
    echo "========================================="
    echo ""
    echo "下一步："
    echo "1. 重载 Nginx: sudo systemctl reload nginx"
    echo "2. 测试访问: curl -I https://junfeng530.xyz/mcp/eventanalyzer"
    echo ""
    echo "如需回滚，执行："
    echo "sudo cp $BACKUP_CONF $NGINX_CONF"
    echo "sudo systemctl reload nginx"
else
    echo "❌ Nginx 配置测试失败"
    echo ""
    echo "正在恢复备份..."
    sudo cp "$BACKUP_CONF" "$NGINX_CONF"
    echo "✓ 已恢复到备份版本"
    echo ""
    echo "请检查错误信息并手动修复"
    exit 1
fi

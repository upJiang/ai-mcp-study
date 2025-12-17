#!/bin/bash
# 彻底清理所有在 http 块之外的 MCP 配置

set -e

NGINX_CONF="/www/server/nginx/conf/nginx.conf"
BACKUP_CONF="/www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)"

echo "========================================="
echo "🧹 彻底清理 Nginx 配置"
echo "========================================="
echo ""

# 1. 备份
echo "步骤 1/4: 备份现有配置..."
sudo cp "$NGINX_CONF" "$BACKUP_CONF"
echo "✓ 备份完成: $BACKUP_CONF"
echo ""

# 2. 查找所有重复块
echo "步骤 2/4: 查找所有 location /mcp/eventanalyzer 块..."
grep -n "location /mcp/eventanalyzer" "$NGINX_CONF" || echo "未找到"
echo ""

# 3. 找到 http 块的结束行
echo "步骤 3/4: 查找 http 块的结束位置..."
http_end=$(grep -n "^include /www/server/panel/vhost/nginx/\*\.conf;" "$NGINX_CONF" | tail -1 | cut -d: -f1)
echo "✓ http 块在第 $http_end 行之后的 } 处结束"
http_end=$((http_end + 1))  # } 在 include 的下一行
echo "  http 块闭括号预计在第 $http_end 行"
echo ""

# 4. 删除 http 块之后的所有内容，只保留到 http 块结束
echo "步骤 4/4: 删除 http 块之后的所有内容..."

# 创建临时文件，只保留到 http 块结束
TMP_FILE=$(mktemp)
head -n $http_end "$NGINX_CONF" > "$TMP_FILE"

# 替换容器名为 localhost
sed -i.bak 's|proxy_pass http://mcp-eventanalyzer:8000|proxy_pass http://127.0.0.1:8100|g' "$TMP_FILE"

# 复制回原文件
sudo cp "$TMP_FILE" "$NGINX_CONF"
rm "$TMP_FILE"

echo "✓ 已删除所有重复配置并替换容器名"
echo ""

# 5. 测试配置
echo "========================================="
echo "测试 Nginx 配置..."
echo "========================================="
if sudo nginx -t; then
    echo ""
    echo "✅ Nginx 配置测试通过！"
    echo ""
    echo "配置修复完成："
    echo "  ✓ 删除了所有在 http 块之外的配置"
    echo "  ✓ 替换容器名为 127.0.0.1:8100"
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

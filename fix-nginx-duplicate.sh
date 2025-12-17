#!/bin/bash
# 删除重复的 MCP EventAnalyzer location 块并修复容器名

set -e

NGINX_CONF="/www/server/nginx/conf/nginx.conf"
BACKUP_CONF="/www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)"

echo "========================================="
echo "🔧 修复重复的 MCP EventAnalyzer 配置"
echo "========================================="
echo ""

# 1. 备份
echo "步骤 1/5: 备份现有配置..."
sudo cp "$NGINX_CONF" "$BACKUP_CONF"
echo "✓ 备份完成: $BACKUP_CONF"
echo ""

# 2. 显示问题位置
echo "步骤 2/5: 查看问题区域（第 215-245 行）..."
echo "----------------------------------------"
sed -n '215,245p' "$NGINX_CONF" | cat -n
echo "----------------------------------------"
echo ""

# 3. 查找重复的 location 块
echo "步骤 3/5: 查找所有 'location /mcp/eventanalyzer' 出现的行号..."
grep -n "location /mcp/eventanalyzer" "$NGINX_CONF" || echo "未找到"
echo ""

# 4. 删除第 221-236 行（重复的 location 块，根据典型配置长度估计）
echo "步骤 4/5: 删除重复的配置块..."
echo "⚠️  准备删除第 221 行到第一个匹配闭括号的范围"
echo ""

# 创建临时文件
TMP_FILE=$(mktemp)

# 使用 awk 删除从第 221 行开始的 location 块
awk '
BEGIN { delete_mode=0; brace_count=0 }
{
    # 如果是第 221 行，开始删除模式
    if (NR == 221) {
        delete_mode = 1
        brace_count = 0
    }

    # 在删除模式中，计算大括号
    if (delete_mode) {
        # 统计这一行的开括号和闭括号
        for (i=1; i<=length($0); i++) {
            c = substr($0, i, 1)
            if (c == "{") brace_count++
            if (c == "}") brace_count--
        }

        # 如果找到匹配的闭括号（brace_count 回到 0 或负数），结束删除
        if (brace_count <= 0) {
            delete_mode = 0
            next  # 跳过这一行（删除闭括号行）
        }
        next  # 跳过当前行
    }

    # 不在删除模式，正常输出
    print
}
' "$NGINX_CONF" > "$TMP_FILE"

# 将临时文件复制回原文件
sudo cp "$TMP_FILE" "$NGINX_CONF"
rm "$TMP_FILE"

echo "✓ 已删除重复的 location 块"
echo ""

# 5. 替换容器名为 localhost
echo "步骤 5/5: 将容器名替换为 localhost..."
sudo sed -i.bak2 's|proxy_pass http://mcp-eventanalyzer:8000|proxy_pass http://127.0.0.1:8100|g' "$NGINX_CONF"
echo "✓ 已替换容器名"
echo ""

# 6. 测试配置
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

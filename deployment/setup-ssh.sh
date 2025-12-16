#!/bin/bash
# 服务器 SSH 密钥一键配置脚本

set -e

echo "========================================="
echo "🔑 服务器 SSH 密钥配置向导"
echo "========================================="
echo ""

# 1. 检查是否已有 SSH 密钥
echo "步骤 1/3: 检查 SSH 密钥..."
if [ -f ~/.ssh/id_rsa.pub ]; then
    echo "✓ 检测到现有 SSH 密钥"
    EXISTING_KEY=true
else
    echo "未检测到 SSH 密钥，将生成新密钥"
    EXISTING_KEY=false
fi
echo ""

# 2. 生成 SSH 密钥（如果不存在）
if [ "$EXISTING_KEY" = false ]; then
    echo "步骤 2/3: 生成 SSH 密钥..."
    read -p "请输入您的邮箱地址: " EMAIL

    if [ -z "$EMAIL" ]; then
        EMAIL="deploy@server"
        echo "使用默认邮箱: $EMAIL"
    fi

    ssh-keygen -t rsa -b 4096 -C "$EMAIL" -f ~/.ssh/id_rsa -N ""
    echo "✓ SSH 密钥已生成"
else
    echo "步骤 2/3: 跳过密钥生成（已存在）"
fi
echo ""

# 3. 显示公钥
echo "步骤 3/3: 获取公钥..."
echo ""
echo "========================================="
echo "📋 您的 SSH 公钥如下："
echo "========================================="
cat ~/.ssh/id_rsa.pub
echo "========================================="
echo ""

# 4. 添加 GitHub 到 known_hosts
echo "添加 GitHub 到 known_hosts..."
mkdir -p ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts 2>/dev/null
echo "✓ GitHub 主机密钥已添加"
echo ""

# 5. 提供下一步指引
echo "========================================="
echo "✅ 配置完成！下一步操作："
echo "========================================="
echo ""
echo "1️⃣  复制上面的 SSH 公钥（从 ssh-rsa 到邮箱结束）"
echo ""
echo "2️⃣  添加到 GitHub："
echo "   • 打开: https://github.com/settings/keys"
echo "   • 点击 'New SSH key'"
echo "   • Title: 输入 'MCP-Server' 或其他名称"
echo "   • Key: 粘贴刚才复制的公钥"
echo "   • 点击 'Add SSH key'"
echo ""
echo "3️⃣  测试连接："
echo "   ssh -T git@github.com"
echo "   应该看到: Hi upJiang! You've successfully authenticated..."
echo ""
echo "4️⃣  切换仓库 URL（如果需要）："
echo "   cd /opt/mcp-services/ai-mcp-study"
echo "   git remote set-url origin git@github.com:upJiang/ai-mcp-study.git"
echo ""
echo "5️⃣  测试拉取代码："
echo "   cd /opt/mcp-services/ai-mcp-study"
echo "   git fetch origin main"
echo ""
echo "========================================="
echo "完成后，推送代码就能自动部署了！🎉"
echo "========================================="

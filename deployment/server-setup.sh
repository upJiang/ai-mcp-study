#!/bin/bash
# 服务器初始化脚本 - CentOS 7.9

set -e

echo "========================================="
echo "MCP 服务器环境初始化"
echo "========================================="

# 1. 安装 Docker
echo "步骤 1/5: 安装 Docker..."
sudo yum update -y
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
echo "✓ Docker 安装完成"

# 2. 安装 Docker Compose
echo "步骤 2/5: 安装 Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
echo "✓ Docker Compose 安装完成"

# 3. 安装 Nginx
echo "步骤 3/5: 安装 Nginx..."
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
echo "✓ Nginx 安装完成"

# 4. 创建工作目录
echo "步骤 4/5: 创建工作目录..."
sudo mkdir -p /opt/mcp-services
sudo chown $USER:$USER /opt/mcp-services
echo "✓ 工作目录创建完成"

# 5. 配置防火墙
echo "步骤 5/5: 配置防火墙..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
echo "✓ 防火墙配置完成"

echo ""
echo "========================================="
echo "✓ 服务器初始化完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 配置 SSL 证书（如果还没有）"
echo "2. 克隆代码仓库到 /opt/mcp-services/"
echo "3. 首次生成 Nginx 配置并部署"
echo "4. 运行 deploy.sh 启动服务"

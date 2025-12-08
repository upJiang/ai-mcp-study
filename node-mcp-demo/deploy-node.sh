#!/bin/bash

# Claude Stats MCP - Node.js 部署脚本

set -e

echo "========================================"
echo "Claude Stats MCP - 部署脚本"
echo "========================================"

# 检查Node.js版本
if ! command -v node &> /dev/null; then
    echo "错误: Node.js未安装"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "错误: Node.js版本需要 >= 18.0.0"
    exit 1
fi

echo "✓ Node.js版本检查通过: $(node -v)"

# 安装依赖
echo ""
echo "正在安装依赖..."
npm ci --only=production

# 构建项目
echo ""
echo "正在构建项目..."
npm run build

# 检查配置文件
if [ ! -f "../ccReport/config/keys.json" ] && [ ! -f "./config/keys.json" ]; then
    echo ""
    echo "警告: 未找到配置文件 keys.json"
    echo "请确保在以下位置之一存在配置文件:"
    echo "  - ../ccReport/config/keys.json"
    echo "  - ./config/keys.json"
    read -p "是否继续部署？ (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 选择部署方式
echo ""
echo "请选择部署方式:"
echo "1) PM2 (推荐)"
echo "2) Docker"
echo "3) Systemd"
read -p "请选择 (1-3): " deploy_choice

case $deploy_choice in
    1)
        # PM2部署
        if ! command -v pm2 &> /dev/null; then
            echo "正在安装PM2..."
            npm install -g pm2
        fi

        echo ""
        echo "正在启动PM2服务..."
        pm2 delete claude-stats-mcp 2>/dev/null || true
        pm2 start ecosystem.config.js --env production
        pm2 save
        
        echo ""
        echo "✓ PM2部署完成！"
        echo ""
        echo "管理命令:"
        echo "  pm2 status                - 查看状态"
        echo "  pm2 logs claude-stats-mcp - 查看日志"
        echo "  pm2 restart claude-stats-mcp - 重启服务"
        echo "  pm2 stop claude-stats-mcp - 停止服务"
        ;;
        
    2)
        # Docker部署
        if ! command -v docker &> /dev/null; then
            echo "错误: Docker未安装"
            exit 1
        fi

        echo ""
        echo "正在构建Docker镜像..."
        docker build -t claude-stats-mcp:latest .

        echo ""
        echo "正在启动Docker容器..."
        docker-compose up -d

        echo ""
        echo "✓ Docker部署完成！"
        echo ""
        echo "管理命令:"
        echo "  docker-compose ps      - 查看状态"
        echo "  docker-compose logs -f - 查看日志"
        echo "  docker-compose restart - 重启服务"
        echo "  docker-compose down    - 停止服务"
        ;;
        
    3)
        # Systemd部署
        echo ""
        echo "正在创建Systemd服务..."
        
        SERVICE_FILE="/etc/systemd/system/claude-stats-mcp.service"
        WORK_DIR=$(pwd)
        
        sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Claude Stats MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="NODE_ENV=production"
Environment="MCP_TRANSPORT=httpStream"
Environment="MCP_PORT=8000"
ExecStart=/usr/bin/node $WORK_DIR/dist/index.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

        sudo systemctl daemon-reload
        sudo systemctl enable claude-stats-mcp
        sudo systemctl start claude-stats-mcp

        echo ""
        echo "✓ Systemd部署完成！"
        echo ""
        echo "管理命令:"
        echo "  sudo systemctl status claude-stats-mcp  - 查看状态"
        echo "  sudo journalctl -u claude-stats-mcp -f  - 查看日志"
        echo "  sudo systemctl restart claude-stats-mcp - 重启服务"
        echo "  sudo systemctl stop claude-stats-mcp    - 停止服务"
        ;;
        
    *)
        echo "无效的选择"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "服务地址: http://localhost:8000/mcp"
echo ""
echo "在Cursor中配置:"
echo '{
  "mcpServers": {
    "claude-stats": {
      "url": "http://localhost:8000/mcp"
    }
  }
}'


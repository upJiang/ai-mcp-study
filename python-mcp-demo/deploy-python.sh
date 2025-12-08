#!/bin/bash

# Claude Stats MCP - Python 部署脚本

set -e

echo "========================================"
echo "Claude Stats MCP (Python) - 部署脚本"
echo "========================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "错误: Python 3未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "错误: Python版本需要 >= 3.8，当前版本: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python版本检查通过: $PYTHON_VERSION"

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
echo "1) Docker (推荐)"
echo "2) Supervisor"
echo "3) Systemd"
echo "4) 仅创建虚拟环境和安装依赖"
read -p "请选择 (1-4): " deploy_choice

case $deploy_choice in
    1)
        # Docker部署
        if ! command -v docker &> /dev/null; then
            echo "错误: Docker未安装"
            exit 1
        fi

        echo ""
        echo "正在构建Docker镜像..."
        docker build -t claude-stats-mcp-python:latest .

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
        
    2)
        # Supervisor部署
        echo ""
        echo "正在创建虚拟环境..."
        python3 -m venv venv
        
        echo ""
        echo "正在安装依赖..."
        ./venv/bin/pip install -r requirements.txt

        WORK_DIR=$(pwd)
        
        echo ""
        echo "请手动配置Supervisor:"
        echo ""
        echo "1. 编辑 supervisor.conf 文件，修改路径:"
        echo "   - command: $WORK_DIR/venv/bin/python $WORK_DIR/server.py"
        echo "   - directory: $WORK_DIR"
        echo ""
        echo "2. 复制配置到Supervisor:"
        echo "   sudo cp supervisor.conf /etc/supervisor/conf.d/claude-stats-mcp.conf"
        echo ""
        echo "3. 重启Supervisor:"
        echo "   sudo supervisorctl reread"
        echo "   sudo supervisorctl update"
        echo "   sudo supervisorctl start claude-stats-mcp"
        ;;
        
    3)
        # Systemd部署
        echo ""
        echo "正在创建虚拟环境..."
        python3 -m venv venv
        
        echo ""
        echo "正在安装依赖..."
        ./venv/bin/pip install -r requirements.txt

        WORK_DIR=$(pwd)
        SERVICE_FILE="/etc/systemd/system/claude-stats-mcp.service"
        
        echo ""
        echo "正在创建Systemd服务..."
        
        sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Claude Stats MCP Server (Python)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="PYTHONUNBUFFERED=1"
Environment="MCP_TRANSPORT=http"
Environment="MCP_PORT=8000"
Environment="KEYS_CONFIG_PATH=$WORK_DIR/../ccReport/config/keys.json"
ExecStart=$WORK_DIR/venv/bin/python $WORK_DIR/server.py
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
        
    4)
        # 仅安装依赖
        echo ""
        echo "正在创建虚拟环境..."
        python3 -m venv venv
        
        echo ""
        echo "正在安装依赖..."
        ./venv/bin/pip install -r requirements.txt

        echo ""
        echo "✓ 虚拟环境创建完成！"
        echo ""
        echo "启动服务:"
        echo "  source venv/bin/activate"
        echo "  python server.py"
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


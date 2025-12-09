#!/bin/bash

# Python MCP Demo 快速启动脚本
# 用途: 快速启动 Python 版本的 Claude Stats MCP 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DEMO_DIR="${PROJECT_ROOT}/python-mcp-demo"
KEYS_FILE="${PROJECT_ROOT}/keys.json"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Python MCP Demo 快速启动${NC}"
echo -e "${BLUE}======================================${NC}\n"

# 检查 Python 版本
echo -e "${YELLOW}📋 检查环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3，请先安装 Python (>= 3.8)${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ Python 版本过低 (需要 >= 3.8)，当前版本: $(python3 --version)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 版本: $(python3 --version)${NC}"

# 检查配置文件
if [ ! -f "$KEYS_FILE" ]; then
    echo -e "${RED}❌ 配置文件不存在: ${KEYS_FILE}${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 配置文件: ${KEYS_FILE}${NC}"

# 进入 python-mcp-demo 目录
cd "$PYTHON_DEMO_DIR"

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}📦 首次运行，正在创建虚拟环境...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ 虚拟环境创建完成${NC}"
fi

# 激活虚拟环境
echo -e "${YELLOW}🔄 激活虚拟环境...${NC}"
source venv/bin/activate

# 检查并安装依赖
if [ ! -f "venv/.deps_installed" ]; then
    echo -e "\n${YELLOW}📦 正在安装依赖...${NC}"
    pip install -r requirements.txt
    touch venv/.deps_installed
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖已安装${NC}"
fi

# 询问运行模式
echo -e "\n${MAGENTA}🔧 选择运行模式:${NC}"
echo -e "  ${GREEN}1)${NC} STDIO 模式 (本地开发，用于 Cursor 本地配置)"
echo -e "  ${GREEN}2)${NC} HTTP 模式 (远程访问，端口 8000)"
echo -e ""
read -p "请选择 [1/2] (默认: 1): " MODE_CHOICE
MODE_CHOICE=${MODE_CHOICE:-1}

# 设置环境变量并启动服务
export KEYS_CONFIG_PATH="$KEYS_FILE"

echo -e "\n${GREEN}🚀 启动 Python MCP Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ "$MODE_CHOICE" = "2" ]; then
    echo -e "${YELLOW}📡 HTTP 模式启动中...${NC}"
    echo -e "${YELLOW}🌐 服务地址: http://localhost:8000/mcp${NC}\n"
    export MCP_TRANSPORT=http
    export MCP_PORT=8000
    python server.py
else
    echo -e "${YELLOW}📟 STDIO 模式启动中...${NC}\n"
    python server.py
fi

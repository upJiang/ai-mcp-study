#!/bin/bash

# Node.js MCP Demo 快速启动脚本
# 用途: 快速启动 Node.js 版本的 Claude Stats MCP 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_DEMO_DIR="${PROJECT_ROOT}/node-mcp-demo"
KEYS_FILE="${PROJECT_ROOT}/keys.json"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Node.js MCP Demo 快速启动${NC}"
echo -e "${BLUE}======================================${NC}\n"

# 检查 Node.js 版本
echo -e "${YELLOW}📋 检查环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 未找到 Node.js，请先安装 Node.js (>= 18)${NC}"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js 版本过低 (需要 >= 18)，当前版本: $(node -v)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js 版本: $(node -v)${NC}"

# 检查配置文件
if [ ! -f "$KEYS_FILE" ]; then
    echo -e "${RED}❌ 配置文件不存在: ${KEYS_FILE}${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 配置文件: ${KEYS_FILE}${NC}"

# 进入 node-mcp-demo 目录
cd "$NODE_DEMO_DIR"

# 检查并安装依赖
if [ ! -d "node_modules" ]; then
    echo -e "\n${YELLOW}📦 首次运行，正在安装依赖...${NC}"
    npm install
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖已安装${NC}"
fi

# 设置环境变量并启动服务
echo -e "\n${GREEN}🚀 启动 Node.js MCP Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

export KEYS_CONFIG_PATH="$KEYS_FILE"
npm run dev

#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🔍 MCP 开发环境检查${NC}"
echo -e "${CYAN}========================================${NC}\n"

# 检查结果统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 检查函数
check_command() {
    local cmd=$1
    local name=$2
    local required_version=$3

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -n 1)
        echo -e "${GREEN}✅ ${name}${NC}"
        echo -e "   版本: ${version}"

        # 检查版本号（如果提供）
        if [ -n "$required_version" ]; then
            local current_version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)
            if [ -n "$current_version" ]; then
                echo -e "   要求: >= ${required_version}"
                # 简单的版本比较（仅比较主版本号）
                local current_major=$(echo "$current_version" | cut -d. -f1)
                local required_major=$(echo "$required_version" | cut -d. -f1)
                if [ "$current_major" -lt "$required_major" ]; then
                    echo -e "   ${YELLOW}⚠️  版本过低，建议升级${NC}"
                fi
            fi
        fi

        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}❌ ${name}${NC}"
        echo -e "   ${YELLOW}未安装${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# 1. 检查 Node.js
echo -e "${CYAN}📦 Node.js 环境${NC}\n"
if check_command "node" "Node.js" "18.0.0"; then
    echo ""
else
    echo -e "   ${YELLOW}安装方法：${NC}"
    echo -e "   - Mac: ${YELLOW}brew install node${NC}"
    echo -e "   - Windows: 从 ${YELLOW}https://nodejs.org${NC} 下载安装包"
    echo -e "   - Linux: ${YELLOW}sudo apt install nodejs${NC} 或 ${YELLOW}sudo yum install nodejs${NC}\n"
fi

# 2. 检查 npm
if check_command "npm" "npm" "9.0.0"; then
    echo ""
else
    echo -e "   ${YELLOW}npm 通常随 Node.js 一起安装${NC}\n"
fi

# 3. 检查 npm 登录状态
echo -e "${CYAN}🔐 npm 账号${NC}\n"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if npm whoami > /dev/null 2>&1; then
    NPM_USER=$(npm whoami)
    echo -e "${GREEN}✅ npm 已登录${NC}"
    echo -e "   用户: ${NPM_USER}\n"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${YELLOW}⚠️  npm 未登录${NC}"
    echo -e "   ${YELLOW}登录方法：${NC}"
    echo -e "   1. 运行 ${YELLOW}npm login${NC}"
    echo -e "   2. 输入用户名、密码、邮箱"
    echo -e "   3. 没有账号？去 ${YELLOW}https://www.npmjs.com/signup${NC} 注册\n"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# 4. 检查 TypeScript 编译器（可选，项目依赖会安装）
echo -e "${CYAN}🔧 开发工具${NC}\n"
if command -v tsc &> /dev/null; then
    check_command "tsc" "TypeScript 编译器"
    echo ""
else
    echo -e "${YELLOW}ℹ️  TypeScript 编译器${NC}"
    echo -e "   ${YELLOW}项目依赖会自动安装，无需全局安装${NC}\n"
fi

# 5. 检查 Git（可选）
if check_command "git" "Git"; then
    echo ""
else
    echo -e "   ${YELLOW}Git 不是必需的，但推荐安装用于版本管理${NC}"
    echo -e "   ${YELLOW}安装方法：${NC}"
    echo -e "   - Mac: ${YELLOW}brew install git${NC}"
    echo -e "   - Windows: 从 ${YELLOW}https://git-scm.com${NC} 下载安装包"
    echo -e "   - Linux: ${YELLOW}sudo apt install git${NC} 或 ${YELLOW}sudo yum install git${NC}\n"
fi

# 6. 检查当前目录是否有 package.json
echo -e "${CYAN}📁 项目检查${NC}\n"
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if [ -f "package.json" ]; then
    echo -e "${GREEN}✅ 找到 package.json${NC}"

    # 读取项目信息
    if command -v node &> /dev/null; then
        PROJECT_NAME=$(node -p "require('./package.json').name" 2>/dev/null)
        PROJECT_VERSION=$(node -p "require('./package.json').version" 2>/dev/null)

        if [ -n "$PROJECT_NAME" ]; then
            echo -e "   名称: ${PROJECT_NAME}"
            echo -e "   版本: ${PROJECT_VERSION}"
        fi
    fi

    # 检查是否已安装依赖
    if [ -d "node_modules" ]; then
        echo -e "${GREEN}   ✅ 依赖已安装${NC}"
    else
        echo -e "${YELLOW}   ⚠️  依赖未安装${NC}"
        echo -e "   ${YELLOW}运行: npm install${NC}"
    fi

    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo ""
else
    echo -e "${YELLOW}ℹ️  未找到 package.json${NC}"
    echo -e "   ${YELLOW}这不是 Node.js 项目，或者你不在项目根目录${NC}\n"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

# 7. 检查 Cursor/Claude Code（可选）
echo -e "${CYAN}🤖 AI 工具${NC}\n"
AI_TOOL_FOUND=false

if command -v cursor &> /dev/null; then
    echo -e "${GREEN}✅ Cursor 已安装${NC}\n"
    AI_TOOL_FOUND=true
fi

if command -v claude &> /dev/null; then
    echo -e "${GREEN}✅ Claude Code 已安装${NC}\n"
    AI_TOOL_FOUND=true
fi

if [ "$AI_TOOL_FOUND" = false ]; then
    echo -e "${YELLOW}ℹ️  未检测到 Cursor 或 Claude Code${NC}"
    echo -e "   ${YELLOW}这些工具不是必需的，但强烈推荐用于 MCP 开发${NC}"
    echo -e "   ${YELLOW}下载地址：${NC}"
    echo -e "   - Cursor: ${YELLOW}https://cursor.sh${NC}"
    echo -e "   - Claude Code: ${YELLOW}https://claude.ai/code${NC}\n"
fi

# 8. 总结
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}📊 检查结果${NC}"
echo -e "${CYAN}========================================${NC}\n"

echo -e "总检查项: ${TOTAL_CHECKS}"
echo -e "${GREEN}通过: ${PASSED_CHECKS}${NC}"
if [ $FAILED_CHECKS -gt 0 ]; then
    echo -e "${RED}失败: ${FAILED_CHECKS}${NC}\n"
else
    echo -e "${YELLOW}警告: ${FAILED_CHECKS}${NC}\n"
fi

# 9. 建议
if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}🎉 恭喜！你的环境已准备就绪${NC}\n"
    echo -e "${CYAN}下一步：${NC}"
    echo -e "   1. 在此目录打开 Cursor 或 Claude Code"
    echo -e "   2. 告诉 AI 你要开发的 MCP 工具"
    echo -e "   3. AI 会自动生成所有代码！\n"
else
    echo -e "${YELLOW}⚠️  请先解决上述问题${NC}\n"
    echo -e "${CYAN}必需项：${NC}"
    echo -e "   ✅ Node.js (>= 18.0.0)"
    echo -e "   ✅ npm (>= 9.0.0)"
    echo -e "   ✅ npm 账号（用于发布）\n"

    echo -e "${CYAN}推荐项：${NC}"
    echo -e "   📝 Git（版本管理）"
    echo -e "   🤖 Cursor 或 Claude Code（AI 辅助开发）\n"
fi

# 10. 额外提示
echo -e "${CYAN}💡 提示${NC}"
echo -e "   - 查看详细文档: ${YELLOW}cat README.md${NC}"
echo -e "   - 5分钟快速开始: ${YELLOW}cat QUICKSTART.md${NC}"
echo -e "   - 查看示例: ${YELLOW}ls docs/examples/${NC}\n"

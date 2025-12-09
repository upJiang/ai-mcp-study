#!/bin/bash

# NPM 包发布脚本
# 用途: 一键发布 Node.js 版本的 MCP 服务到 npm

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 项目目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NODE_DEMO_DIR="${PROJECT_ROOT}/node-mcp-demo"

printf "${BLUE}======================================${NC}\n"
printf "${BLUE}  NPM 包发布工具${NC}\n"
printf "${BLUE}======================================${NC}\n\n"

# 进入 node-mcp-demo 目录
cd "$NODE_DEMO_DIR"

# 1. 检查并切换到官方 npm registry
printf "${YELLOW}📋 检查 npm registry...${NC}\n"
CURRENT_REGISTRY=$(npm config get registry)
OFFICIAL_REGISTRY="https://registry.npmjs.org/"

if [ "$CURRENT_REGISTRY" != "$OFFICIAL_REGISTRY" ]; then
    printf "${YELLOW}⚠️  当前 registry: ${CURRENT_REGISTRY}${NC}\n"
    printf "${CYAN}💡 发布到 npm 需要使用官方源${NC}\n\n"
    printf "${CYAN}是否自动切换到官方源？${NC}\n"
    printf "   官方源: ${GREEN}${OFFICIAL_REGISTRY}${NC}\n\n"

    read -p "切换到官方源? [Y/n]: " SWITCH_REGISTRY
    if [[ ! $SWITCH_REGISTRY =~ ^[Nn]$ ]]; then
        printf "${YELLOW}正在切换 registry...${NC}\n"
        npm config set registry "$OFFICIAL_REGISTRY"
        printf "${GREEN}✅ 已切换到官方源${NC}\n\n"

        # 记住需要恢复
        NEED_RESTORE_REGISTRY=true
        OLD_REGISTRY="$CURRENT_REGISTRY"
    else
        printf "${RED}❌ 未切换源，可能导致发布失败${NC}\n"
        printf "${CYAN}💡 你可以手动切换: ${GREEN}npm config set registry ${OFFICIAL_REGISTRY}${NC}\n\n"
        read -p "确认继续? [y/N]: " CONTINUE
        if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
            printf "${YELLOW}已取消发布${NC}\n"
            exit 0
        fi
    fi
else
    printf "${GREEN}✅ 当前使用官方源${NC}\n"
fi

# 2. 检查 npm 登录状态
printf "${YELLOW}📋 检查 npm 登录状态...${NC}\n"
if ! npm whoami &> /dev/null; then
    printf "${RED}❌ 未登录 npm${NC}\n\n"
    printf "${CYAN}📌 请先登录 npm:${NC}\n"
    printf "   ${GREEN}npm login${NC}\n\n"
    printf "${CYAN}💡 如果没有 npm 账号:${NC}\n"
    printf "   1. 访问 ${BLUE}https://www.npmjs.com/signup${NC}\n"
    printf "   2. 注册账号\n"
    printf "   3. 运行 ${GREEN}npm login${NC} 登录\n\n"

    read -p "是否现在登录? [y/N]: " LOGIN_NOW
    if [[ $LOGIN_NOW =~ ^[Yy]$ ]]; then
        npm login
        if ! npm whoami &> /dev/null; then
            printf "${RED}登录失败，退出发布流程${NC}\n"
            exit 1
        fi
        printf "${GREEN}✅ 登录成功！${NC}\n"
    else
        printf "${YELLOW}已取消发布${NC}\n"
        exit 0
    fi
fi
printf "${GREEN}✅ 已登录 npm ($(npm whoami))${NC}\n"

# 3. 读取包名和版本
PACKAGE_NAME=$(node -p "require('./package.json').name")
CURRENT_VERSION=$(node -p "require('./package.json').version")

printf "${GREEN}✅ 包名: ${PACKAGE_NAME}${NC}\n"
printf "${GREEN}✅ 当前版本: ${CURRENT_VERSION}${NC}\n"

# 4. 检查包名是否可用
printf "\n${YELLOW}🔍 检查包名是否可用...${NC}\n"
if npm view "$PACKAGE_NAME" &> /dev/null; then
    printf "${YELLOW}⚠️  包名 ${PACKAGE_NAME} 已被使用${NC}\n\n"
    printf "${CYAN}📌 解决方案:${NC}\n"
    printf "   ${YELLOW}方案 1:${NC} 使用作用域包名\n"
    printf "      修改 package.json 中的 name 为: ${GREEN}@your-org/${PACKAGE_NAME}${NC}\n"
    printf "      需要 npm 组织账号，免费创建：https://www.npmjs.com/org/create\n\n"
    printf "   ${YELLOW}方案 2:${NC} 修改包名\n"
    printf "      编辑 package.json，将 name 改为其他名称\n"
    printf "      例如: ${GREEN}${PACKAGE_NAME}-cli${NC} 或 ${GREEN}my-${PACKAGE_NAME}${NC}\n\n"
    printf "   ${YELLOW}方案 3:${NC} 查看已发布的包\n"
    printf "      访问: ${BLUE}https://www.npmjs.com/package/${PACKAGE_NAME}${NC}\n\n"

    read -p "是否继续发布（可能会失败）? [y/N]: " CONTINUE
    if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
        printf "${YELLOW}已取消发布${NC}\n"
        printf "\n${CYAN}💡 修改包名后，再次运行此脚本即可${NC}\n"
        exit 0
    fi
else
    printf "${GREEN}✅ 包名可用${NC}\n"
fi

# 5. 检查 git 状态
printf "\n${YELLOW}📋 检查 Git 状态...${NC}\n"
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        printf "${YELLOW}⚠️  工作区有未提交的更改${NC}\n\n"
        git status --short
        printf "\n${CYAN}💡 建议先提交更改:${NC}\n"
        printf "   ${GREEN}git add .${NC}\n"
        printf "   ${GREEN}git commit -m \"准备发布 v${CURRENT_VERSION}\"${NC}\n\n"

        read -p "是否继续? [y/N]: " CONTINUE
        if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
            printf "${YELLOW}已取消发布${NC}\n"
            exit 0
        fi
    else
        printf "${GREEN}✅ 工作区干净${NC}\n"
    fi
else
    printf "${YELLOW}⚠️  不是 Git 仓库${NC}\n"
fi

# 6. 检查依赖
printf "\n${YELLOW}📦 检查项目依赖...${NC}\n"
if [ ! -d "node_modules" ]; then
    printf "${YELLOW}⚠️  node_modules 目录不存在${NC}\n"
    printf "${CYAN}💡 需要先安装依赖${NC}\n\n"

    # 检查是否有 yarn
    if command -v yarn &> /dev/null; then
        printf "${CYAN}选择包管理器:${NC}\n"
        printf "   ${GREEN}1)${NC} yarn (推荐，速度更快)\n"
        printf "   ${GREEN}2)${NC} npm\n\n"
        read -p "请选择 [1/2]: " PKG_MANAGER

        case $PKG_MANAGER in
            1)
                printf "${YELLOW}正在使用 yarn 安装依赖...${NC}\n"
                if yarn install; then
                    printf "${GREEN}✅ 依赖安装成功${NC}\n"
                else
                    printf "${RED}❌ 依赖安装失败${NC}\n\n"
                    printf "${CYAN}💡 请手动运行: ${GREEN}yarn install${NC}\n"
                    exit 1
                fi
                ;;
            2)
                printf "${YELLOW}正在使用 npm 安装依赖...${NC}\n"
                if npm install; then
                    printf "${GREEN}✅ 依赖安装成功${NC}\n"
                else
                    printf "${RED}❌ 依赖安装失败${NC}\n\n"
                    printf "${CYAN}💡 请手动运行: ${GREEN}npm install${NC}\n"
                    exit 1
                fi
                ;;
            *)
                printf "${RED}无效选择，使用 npm${NC}\n"
                npm install
                ;;
        esac
    else
        read -p "是否自动安装依赖 (npm)? [Y/n]: " INSTALL_DEPS
        if [[ ! $INSTALL_DEPS =~ ^[Nn]$ ]]; then
            printf "${YELLOW}正在使用 npm 安装依赖...${NC}\n"
            if npm install; then
                printf "${GREEN}✅ 依赖安装成功${NC}\n"
            else
                printf "${RED}❌ 依赖安装失败${NC}\n\n"
                printf "${CYAN}💡 请手动运行: ${GREEN}npm install${NC}\n"
                exit 1
            fi
        else
            printf "${RED}❌ 未安装依赖，无法继续${NC}\n"
            exit 1
        fi
    fi
else
    printf "${GREEN}✅ 依赖已安装${NC}\n"
fi

# 7. 运行构建
printf "\n${YELLOW}🔨 运行构建...${NC}\n"
if ! npm run build; then
    printf "${RED}❌ 构建失败${NC}\n\n"
    printf "${CYAN}💡 常见问题:${NC}\n"
    printf "   1. 检查 TypeScript 语法错误\n"
    printf "   2. 检查依赖版本冲突: ${GREEN}rm -rf node_modules package-lock.json && npm install${NC}\n"
    printf "   3. 查看详细错误信息修复问题\n\n"

    read -p "是否重新安装依赖再试? [y/N]: " REINSTALL
    if [[ $REINSTALL =~ ^[Yy]$ ]]; then
        printf "${YELLOW}正在重新安装依赖...${NC}\n"
        rm -rf node_modules package-lock.json
        npm install
        printf "\n${YELLOW}重新构建...${NC}\n"
        if npm run build; then
            printf "${GREEN}✅ 构建成功${NC}\n"
        else
            printf "${RED}❌ 仍然失败，请检查代码错误${NC}\n"
            exit 1
        fi
    else
        exit 1
    fi
fi

if [ ! -d "dist" ]; then
    printf "${RED}❌ 构建失败，dist 目录不存在${NC}\n"
    exit 1
fi

printf "${GREEN}✅ 构建成功${NC}\n"

# 8. 选择版本类型
printf "\n${YELLOW}📦 选择版本更新类型:${NC}\n"
printf "   当前版本: ${CYAN}${CURRENT_VERSION}${NC}\n\n"
printf "   ${GREEN}1)${NC} patch (修复版本，如 1.0.0 → 1.0.1)\n"
printf "      适用于: bug 修复、小改进\n\n"
printf "   ${GREEN}2)${NC} minor (次版本，如 1.0.0 → 1.1.0)\n"
printf "      适用于: 新功能、向下兼容的更新\n\n"
printf "   ${GREEN}3)${NC} major (主版本，如 1.0.0 → 2.0.0)\n"
printf "      适用于: 破坏性更新、大版本升级\n\n"
printf "   ${GREEN}4)${NC} 跳过版本更新（使用当前版本 ${CURRENT_VERSION}）\n\n"

read -p "请选择 [1/2/3/4]: " VERSION_CHOICE

case $VERSION_CHOICE in
    1)
        printf "${YELLOW}更新 patch 版本...${NC}\n"
        npm version patch
        ;;
    2)
        printf "${YELLOW}更新 minor 版本...${NC}\n"
        npm version minor
        ;;
    3)
        printf "${YELLOW}更新 major 版本...${NC}\n"
        npm version major
        ;;
    4)
        printf "${YELLOW}跳过版本更新${NC}\n"
        ;;
    *)
        printf "${RED}无效选择，已取消${NC}\n"
        exit 0
        ;;
esac

NEW_VERSION=$(node -p "require('./package.json').version")
printf "${GREEN}✅ 当前版本: ${NEW_VERSION}${NC}\n"

# 9. 确认发布
printf "\n${CYAN}╔════════════════════════════════════════════╗${NC}\n"
printf "${CYAN}║          准备发布到 NPM                     ║${NC}\n"
printf "${CYAN}╚════════════════════════════════════════════╝${NC}\n\n"
printf "   包名: ${GREEN}${PACKAGE_NAME}${NC}\n"
printf "   版本: ${GREEN}${NEW_VERSION}${NC}\n"
printf "   访问: ${BLUE}public${NC}\n\n"

read -p "确认发布? [y/N]: " CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    printf "${YELLOW}已取消发布${NC}\n"
    exit 0
fi

# 10. 发布到 npm
printf "\n${YELLOW}🚀 发布到 npm...${NC}\n"
if npm publish --access public; then
    printf "${GREEN}✅ 发布成功！${NC}\n"
else
    printf "${RED}❌ 发布失败${NC}\n\n"
    printf "${CYAN}💡 常见问题:${NC}\n"
    printf "   1. 包名冲突: 修改 package.json 中的 name\n"
    printf "   2. 权限问题: 检查 npm 账号权限\n"
    printf "   3. 版本已存在: 更新版本号后重试\n"
    printf "   4. 网络问题: 检查网络连接或使用 VPN\n"
    exit 1
fi

# 11. 推送 git tags（如果在 git 仓库中）
if [ -d ".git" ] && [ "$VERSION_CHOICE" != "4" ]; then
    printf "\n${YELLOW}📌 推送 git tags...${NC}\n"
    if git push --tags 2>/dev/null; then
        printf "${GREEN}✅ Tags 已推送${NC}\n"
    else
        printf "${YELLOW}⚠️  无法推送 tags${NC}\n"
        printf "${CYAN}💡 可能原因:${NC}\n"
        printf "   1. 没有配置远程仓库\n"
        printf "   2. 没有推送权限\n"
        printf "   手动推送: ${GREEN}git push origin --tags${NC}\n"
    fi
fi

# 10. 显示使用说明
printf "\n${GREEN}╔════════════════════════════════════════════╗${NC}\n"
printf "${GREEN}║                                            ║${NC}\n"
printf "${GREEN}║     ${CYAN}🎉 发布完成！${GREEN}                        ║${NC}\n"
printf "${GREEN}║                                            ║${NC}\n"
printf "${GREEN}╚════════════════════════════════════════════╝${NC}\n\n"

printf "${CYAN}📦 包信息:${NC}\n"
printf "   包名: ${GREEN}${PACKAGE_NAME}${NC}\n"
printf "   版本: ${GREEN}${NEW_VERSION}${NC}\n"
printf "   查看: ${BLUE}https://www.npmjs.com/package/${PACKAGE_NAME}${NC}\n"

printf "\n${CYAN}⏰ 等待 NPM 同步...${NC}\n"
printf "   通常需要 ${YELLOW}2-5 分钟${NC}，请稍后使用\n"

printf "\n${CYAN}🚀 使用方式:${NC}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "# 一次性运行（推荐）\n"
printf "${GREEN}npx ${PACKAGE_NAME}${NC}\n\n"
printf "# 全局安装\n"
printf "${GREEN}npm install -g ${PACKAGE_NAME}${NC}\n"
printf "${GREEN}${PACKAGE_NAME}${NC}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

printf "\n${CYAN}🔧 Cursor 配置:${NC}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "{\n"
printf "  \"mcpServers\": {\n"
printf "    \"claude-stats\": {\n"
printf "      \"command\": \"npx\",\n"
printf "      \"args\": [\"-y\", \"${PACKAGE_NAME}\"],\n"
printf "      \"env\": {\n"
printf "        \"KEYS_CONFIG_PATH\": \"/path/to/keys.json\"\n"
printf "      }\n"
printf "    }\n"
printf "  }\n"
printf "}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

printf "\n${GREEN}发布成功！${NC} 🎉\n\n"
printf "${CYAN}💡 下一步:${NC}\n"
printf "   1. 等待 2-5 分钟让 NPM 同步\n"
printf "   2. 测试: ${GREEN}npx ${PACKAGE_NAME}${NC}\n"
printf "   3. 分享给其他人使用\n\n"

# 询问是否恢复原 registry
if [ "$NEED_RESTORE_REGISTRY" = true ]; then
    printf "${CYAN}🔄 是否恢复原来的 npm registry？${NC}\n"
    printf "   原始源: ${YELLOW}${OLD_REGISTRY}${NC}\n"
    printf "   当前源: ${GREEN}${OFFICIAL_REGISTRY}${NC}\n\n"
    printf "${CYAN}💡 说明:${NC}\n"
    printf "   - 保持官方源: 后续发布更方便\n"
    printf "   - 恢复镜像源: 国内下载包更快\n\n"

    read -p "恢复到原始源? [y/N]: " RESTORE
    if [[ $RESTORE =~ ^[Yy]$ ]]; then
        npm config set registry "$OLD_REGISTRY"
        printf "${GREEN}✅ 已恢复到: ${OLD_REGISTRY}${NC}\n\n"
    else
        printf "${GREEN}✅ 保持官方源${NC}\n"
        printf "${CYAN}💡 如需切回镜像源: ${GREEN}npm config set registry ${OLD_REGISTRY}${NC}\n\n"
    fi
fi

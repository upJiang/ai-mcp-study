#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}📦 MCP 项目发布助手${NC}"
echo -e "${CYAN}========================================${NC}\n"

# 1. 检查是否在项目根目录
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ 错误：未找到 package.json${NC}"
    echo -e "${YELLOW}请确保在项目根目录运行此脚本${NC}"
    exit 1
fi

# 2. 读取包名和当前版本
PACKAGE_NAME=$(node -p "require('./package.json').name" 2>/dev/null)
CURRENT_VERSION=$(node -p "require('./package.json').version" 2>/dev/null)

if [ -z "$PACKAGE_NAME" ]; then
    echo -e "${RED}❌ 错误：无法读取包名${NC}"
    exit 1
fi

echo -e "${CYAN}📦 包名: ${PACKAGE_NAME}${NC}"
echo -e "${CYAN}📌 当前版本: ${CURRENT_VERSION}${NC}\n"

# 3. 发布前检查
echo -e "${CYAN}💡 发布前检查清单：${NC}"
echo -e "   ${YELLOW}请确认以下配置已完成：${NC}"
echo -e "   - name: 包名（必须全网唯一）"
echo -e "   - description: 功能描述"
echo -e "   - author: 作者信息"
echo -e "   - bin: 命令名称\n"

read -p "$(echo -e ${GREEN}是否已完成上述配置? [y/N]: ${NC})" CONFIG_DONE
if [[ ! $CONFIG_DONE =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  请先完成配置修改，再运行此脚本${NC}"
    exit 0
fi

# 4. 检查 npm 登录
echo -e "\n${CYAN}🔐 检查 npm 登录状态...${NC}"
if ! npm whoami > /dev/null 2>&1; then
    echo -e "${RED}❌ 未登录 npm${NC}"
    echo -e "${YELLOW}请先运行: npm login${NC}"
    exit 1
fi
NPM_USER=$(npm whoami)
echo -e "${GREEN}✅ 已登录：${NPM_USER}${NC}\n"

# 5. 检查包名是否已存在（仅对新包）
echo -e "${CYAN}🔍 检查包名可用性...${NC}"
if npm view "$PACKAGE_NAME" version > /dev/null 2>&1; then
    PUBLISHED_VERSION=$(npm view "$PACKAGE_NAME" version)
    echo -e "${GREEN}✅ 包已存在，当前发布版本: ${PUBLISHED_VERSION}${NC}"

    # 检查本地版本是否大于已发布版本
    if [ "$CURRENT_VERSION" = "$PUBLISHED_VERSION" ]; then
        echo -e "${YELLOW}⚠️  警告：本地版本与已发布版本相同${NC}"
        echo -e "${YELLOW}   需要更新版本号才能发布${NC}\n"
    else
        echo -e "${GREEN}✅ 本地版本 ${CURRENT_VERSION} 大于已发布版本 ${PUBLISHED_VERSION}${NC}\n"
    fi
else
    echo -e "${GREEN}✅ 包名可用（首次发布）${NC}\n"
fi

# 6. 运行发布前检查清单（如果存在）
if [ -f "checklists/before-publish.md" ]; then
    echo -e "${CYAN}📋 发布前检查清单：${NC}\n"
    cat checklists/before-publish.md
    echo ""
    read -p "$(echo -e ${GREEN}是否通过所有检查? [y/N]: ${NC})" CHECKS_PASSED
    if [[ ! $CHECKS_PASSED =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⚠️  请解决问题后再发布${NC}"
        exit 0
    fi
fi

# 7. 构建项目
echo -e "\n${CYAN}🔨 构建项目...${NC}"
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败${NC}"
    echo -e "${YELLOW}请检查代码错误后重试${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 构建成功${NC}\n"

# 8. 检查 dist 目录
if [ ! -d "dist" ]; then
    echo -e "${RED}❌ 错误：dist 目录不存在${NC}"
    exit 1
fi

if [ ! -f "dist/index.js" ]; then
    echo -e "${RED}❌ 错误：dist/index.js 不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 构建产物检查通过${NC}\n"

# 9. 选择版本更新类型
echo -e "${CYAN}📌 当前版本：${CURRENT_VERSION}${NC}\n"
echo -e "${CYAN}请选择版本更新类型：${NC}"
echo -e "   ${YELLOW}1)${NC} patch (${CURRENT_VERSION} → $(node -p "require('semver').inc('${CURRENT_VERSION}', 'patch')")) - 小修复"
echo -e "   ${YELLOW}2)${NC} minor (${CURRENT_VERSION} → $(node -p "require('semver').inc('${CURRENT_VERSION}', 'minor')")) - 新功能"
echo -e "   ${YELLOW}3)${NC} major (${CURRENT_VERSION} → $(node -p "require('semver').inc('${CURRENT_VERSION}', 'major')")) - 重大更新"
echo -e "   ${YELLOW}4)${NC} 跳过版本更新（使用当前版本）"
echo ""

read -p "$(echo -e ${GREEN}选择 (1/2/3/4): ${NC})" version_type

case $version_type in
  1)
    echo -e "${CYAN}更新版本号为 patch...${NC}"
    npm version patch --no-git-tag-version
    ;;
  2)
    echo -e "${CYAN}更新版本号为 minor...${NC}"
    npm version minor --no-git-tag-version
    ;;
  3)
    echo -e "${CYAN}更新版本号为 major...${NC}"
    npm version major --no-git-tag-version
    ;;
  4)
    echo -e "${YELLOW}跳过版本更新${NC}"
    ;;
  *)
    echo -e "${RED}❌ 无效选择${NC}"
    exit 1
    ;;
esac

# 读取更新后的版本号
NEW_VERSION=$(node -p "require('./package.json').version")
echo -e "${GREEN}✅ 版本号：${NEW_VERSION}${NC}\n"

# 10. 确认发布
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}📦 准备发布${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "包名：${YELLOW}${PACKAGE_NAME}${NC}"
echo -e "版本：${YELLOW}${NEW_VERSION}${NC}"
echo -e "用户：${YELLOW}${NPM_USER}${NC}\n"

read -p "$(echo -e ${GREEN}确认发布? [y/N]: ${NC})" CONFIRM_PUBLISH
if [[ ! $CONFIRM_PUBLISH =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  已取消发布${NC}"
    exit 0
fi

# 11. 发布到 npm
echo -e "\n${CYAN}🚀 发布到 npm...${NC}"
npm publish --access public

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ 发布成功！${NC}"
    echo -e "${GREEN}========================================${NC}\n"

    echo -e "${CYAN}📝 包信息：${NC}"
    echo -e "   📦 名称：${YELLOW}${PACKAGE_NAME}${NC}"
    echo -e "   📌 版本：${YELLOW}${NEW_VERSION}${NC}"
    echo -e "   🔗 链接：${YELLOW}https://www.npmjs.com/package/${PACKAGE_NAME}${NC}\n"

    echo -e "${CYAN}🎯 用户可以通过以下方式使用：${NC}"
    echo -e "   ${YELLOW}npx -y ${PACKAGE_NAME}${NC}\n"

    echo -e "${CYAN}🔧 在 Cursor/Claude Code 配置：${NC}"
    echo -e "${YELLOW}{"
    echo -e "  \"mcpServers\": {"
    echo -e "    \"my-tool\": {"
    echo -e "      \"command\": \"npx\","
    echo -e "      \"args\": [\"-y\", \"${PACKAGE_NAME}\"]"
    echo -e "    }"
    echo -e "  }"
    echo -e "}${NC}\n"

    echo -e "${CYAN}📚 下一步：${NC}"
    echo -e "   1. 等待 1-2 分钟让 npm 完成索引"
    echo -e "   2. 在 Cursor/Claude Code 配置文件中添加上述配置"
    echo -e "   3. 重启 AI 工具"
    echo -e "   4. 开始使用你的 MCP 工具！\n"

else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}❌ 发布失败${NC}"
    echo -e "${RED}========================================${NC}\n"

    echo -e "${YELLOW}常见原因：${NC}"
    echo -e "   ${RED}1.${NC} 包名已被占用"
    echo -e "      ${YELLOW}解决方法：${NC}修改 package.json 中的 name 字段"
    echo -e "      ${YELLOW}建议格式：${NC}@your-username/package-name\n"

    echo -e "   ${RED}2.${NC} 版本号已存在"
    echo -e "      ${YELLOW}解决方法：${NC}重新运行脚本并选择更新版本号\n"

    echo -e "   ${RED}3.${NC} 网络问题"
    echo -e "      ${YELLOW}解决方法：${NC}检查网络连接，或稍后重试\n"

    echo -e "   ${RED}4.${NC} 权限问题"
    echo -e "      ${YELLOW}解决方法：${NC}确认 npm 账号有发布权限\n"

    echo -e "${CYAN}💡 查看详细错误信息请向上滚动终端${NC}\n"

    exit 1
fi

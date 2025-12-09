#!/bin/bash

# PyPI 包发布脚本
# 用途: 一键发布 Python 版本的 MCP 服务到 PyPI

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 项目目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DEMO_DIR="${PROJECT_ROOT}/python-mcp-demo"

printf "${BLUE}======================================${NC}\n"
printf "${BLUE}  PyPI 包发布工具${NC}\n"
printf "${BLUE}======================================${NC}\n\n"

# 进入 python-mcp-demo 目录
cd "$PYTHON_DEMO_DIR"

# 1. 检查 Python 版本
printf "${YELLOW}📋 检查 Python 环境...${NC}\n"
if ! command -v python3 &> /dev/null; then
    printf "${RED}❌ 未找到 Python3${NC}\n\n"
    printf "${CYAN}💡 请安装 Python 3.8 或更高版本:${NC}\n"
    printf "   macOS: ${GREEN}brew install python3${NC}\n"
    printf "   Ubuntu: ${GREEN}sudo apt install python3${NC}\n"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
printf "${GREEN}✅ Python 版本: ${PYTHON_VERSION}${NC}\n"

# 2. 检查必要的包
printf "\n${YELLOW}📋 检查发布工具...${NC}\n"

if ! python3 -m pip show build &> /dev/null; then
    printf "${YELLOW}⚠️  缺少 build 包${NC}\n"
    printf "${CYAN}💡 正在自动安装...${NC}\n"
    if python3 -m pip install build; then
        printf "${GREEN}✅ build 安装成功${NC}\n"
    else
        printf "${RED}❌ build 安装失败${NC}\n"
        printf "${CYAN}💡 手动安装: ${GREEN}pip install build${NC}\n"
        exit 1
    fi
fi

if ! python3 -m pip show twine &> /dev/null; then
    printf "${YELLOW}⚠️  缺少 twine 包${NC}\n"
    printf "${CYAN}💡 正在自动安装...${NC}\n"
    if python3 -m pip install twine; then
        printf "${GREEN}✅ twine 安装成功${NC}\n"
    else
        printf "${RED}❌ twine 安装失败${NC}\n"
        printf "${CYAN}💡 手动安装: ${GREEN}pip install twine${NC}\n"
        exit 1
    fi
fi

printf "${GREEN}✅ 发布工具已就绪${NC}\n"

# 3. 读取包信息
PACKAGE_NAME=$(python3 -c "import ast; setup_code = open('setup.py').read(); tree = ast.parse(setup_code); setup_call = next((node for node in ast.walk(tree) if isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == 'setup'), None); name_arg = next((kw.value.s for kw in setup_call.keywords if kw.arg == 'name'), 'claude-stats-mcp')" 2>/dev/null || echo "claude-stats-mcp")
CURRENT_VERSION=$(python3 -c "import ast; setup_code = open('setup.py').read(); tree = ast.parse(setup_code); setup_call = next((node for node in ast.walk(tree) if isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == 'setup'), None); version_arg = next((kw.value.s for kw in setup_call.keywords if kw.arg == 'version'), '1.0.0')" 2>/dev/null || echo "1.0.0")

printf "\n${GREEN}✅ 包名: ${PACKAGE_NAME}${NC}\n"
printf "${GREEN}✅ 当前版本: ${CURRENT_VERSION}${NC}\n"

# 4. 清理旧构建
printf "\n${YELLOW}🧹 清理旧构建...${NC}\n"
rm -rf dist/ build/ *.egg-info
printf "${GREEN}✅ 清理完成${NC}\n"

# 5. 构建包
printf "\n${YELLOW}🔨 构建包...${NC}\n"
if python3 -m build; then
    printf "${GREEN}✅ 构建成功${NC}\n"
else
    printf "${RED}❌ 构建失败${NC}\n\n"
    printf "${CYAN}💡 常见问题:${NC}\n"
    printf "   1. 检查 setup.py 语法错误\n"
    printf "   2. 检查依赖是否正确\n"
    printf "   3. 查看详细错误信息修复问题\n"
    exit 1
fi

if [ ! -d "dist" ]; then
    printf "${RED}❌ 构建失败，dist 目录不存在${NC}\n"
    exit 1
fi

printf "\n${CYAN}生成的文件:${NC}\n"
ls -lh dist/

# 6. 选择发布目标
printf "\n${YELLOW}🎯 选择发布目标:${NC}\n"
printf "   ${GREEN}1)${NC} TestPyPI (测试环境，推荐先测试)\n"
printf "      地址: https://test.pypi.org\n"
printf "      适用于: 测试发布流程、验证包配置\n\n"
printf "   ${GREEN}2)${NC} PyPI (正式环境)\n"
printf "      地址: https://pypi.org\n"
printf "      适用于: 正式发布给用户使用\n\n"

read -p "请选择 [1/2]: " TARGET_CHOICE

case $TARGET_CHOICE in
    1)
        REPO="testpypi"
        REPO_URL="https://test.pypi.org/simple/"
        PACKAGE_URL="https://test.pypi.org/project/${PACKAGE_NAME}"
        printf "${YELLOW}目标: TestPyPI (测试环境)${NC}\n\n"
        printf "${CYAN}💡 需要 TestPyPI 账号:${NC}\n"
        printf "   注册: ${BLUE}https://test.pypi.org/account/register/${NC}\n"
        printf "   登录后生成 API Token: ${BLUE}https://test.pypi.org/manage/account/token/${NC}\n\n"
        ;;
    2)
        REPO="pypi"
        REPO_URL="https://upload.pypi.org/legacy/"
        PACKAGE_URL="https://pypi.org/project/${PACKAGE_NAME}"
        printf "${YELLOW}目标: PyPI (正式环境)${NC}\n\n"
        printf "${CYAN}💡 需要 PyPI 账号:${NC}\n"
        printf "   注册: ${BLUE}https://pypi.org/account/register/${NC}\n"
        printf "   登录后生成 API Token: ${BLUE}https://pypi.org/manage/account/token/${NC}\n\n"
        ;;
    *)
        printf "${RED}无效选择，已取消${NC}\n"
        exit 0
        ;;
esac

# 7. 确认发布
printf "${CYAN}╔════════════════════════════════════════════╗${NC}\n"
printf "${CYAN}║          准备发布到 ${REPO}                  ${NC}\n"
printf "${CYAN}╚════════════════════════════════════════════╝${NC}\n\n"
printf "   包名: ${GREEN}${PACKAGE_NAME}${NC}\n"
printf "   版本: ${GREEN}${CURRENT_VERSION}${NC}\n"
printf "   目标: ${GREEN}${REPO}${NC}\n\n"

read -p "确认发布? [y/N]: " CONFIRM

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    printf "${YELLOW}已取消发布${NC}\n"
    exit 0
fi

# 8. 上传到 PyPI
printf "\n${YELLOW}🚀 上传到 ${REPO}...${NC}\n"

if [ "$REPO" == "testpypi" ]; then
    if python3 -m twine upload --repository testpypi dist/*; then
        printf "${GREEN}✅ 上传成功！${NC}\n"
    else
        printf "${RED}❌ 上传失败${NC}\n\n"
        printf "${CYAN}💡 常见问题:${NC}\n"
        printf "   1. 未配置 PyPI 凭证\n"
        printf "      配置 ~/.pypirc 或使用 API Token\n"
        printf "   2. 包名已存在\n"
        printf "      修改 setup.py 中的 name\n"
        printf "   3. 版本号已存在\n"
        printf "      更新 setup.py 中的 version\n"
        printf "   4. 网络问题\n"
        printf "      检查网络连接或使用 VPN\n"
        exit 1
    fi
else
    if python3 -m twine upload dist/*; then
        printf "${GREEN}✅ 上传成功！${NC}\n"
    else
        printf "${RED}❌ 上传失败${NC}\n\n"
        printf "${CYAN}💡 常见问题:${NC}\n"
        printf "   1. 未配置 PyPI 凭证\n"
        printf "      配置 ~/.pypirc 或使用 API Token\n"
        printf "   2. 包名已存在\n"
        printf "      修改 setup.py 中的 name\n"
        printf "   3. 版本号已存在\n"
        printf "      更新 setup.py 中的 version\n"
        printf "   4. 网络问题\n"
        printf "      检查网络连接或使用 VPN\n"
        exit 1
    fi
fi

# 9. 显示使用说明
printf "\n${GREEN}╔════════════════════════════════════════════╗${NC}\n"
printf "${GREEN}║                                            ║${NC}\n"
printf "${GREEN}║     ${CYAN}🎉 发布完成！${GREEN}                        ║${NC}\n"
printf "${GREEN}║                                            ║${NC}\n"
printf "${GREEN}╚════════════════════════════════════════════╝${NC}\n\n"

printf "${CYAN}📦 包信息:${NC}\n"
printf "   包名: ${GREEN}${PACKAGE_NAME}${NC}\n"
printf "   版本: ${GREEN}${CURRENT_VERSION}${NC}\n"
printf "   查看: ${BLUE}${PACKAGE_URL}${NC}\n"

printf "\n${CYAN}⏰ 等待同步...${NC}\n"
printf "   通常需要 ${YELLOW}2-5 分钟${NC}，请稍后使用\n"

printf "\n${CYAN}🚀 使用方式:${NC}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ "$REPO" == "testpypi" ]; then
    printf "# 从 TestPyPI 安装（测试）\n"
    printf "${GREEN}pip install -i https://test.pypi.org/simple/ ${PACKAGE_NAME}${NC}\n\n"
    printf "# 使用 pipx 安装（推荐）\n"
    printf "${GREEN}pipx install --index-url https://test.pypi.org/simple/ ${PACKAGE_NAME}${NC}\n"
else
    printf "# 使用 pipx 安装（推荐）\n"
    printf "${GREEN}pipx install ${PACKAGE_NAME}${NC}\n\n"
    printf "# 或使用 pip 安装\n"
    printf "${GREEN}pip install ${PACKAGE_NAME}${NC}\n"
fi

printf "\n# 运行\n"
printf "${GREEN}${PACKAGE_NAME}${NC}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

printf "\n${CYAN}🔧 Cursor 配置:${NC}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "{\n"
printf "  \"mcpServers\": {\n"
printf "    \"claude-stats\": {\n"
printf "      \"command\": \"${PACKAGE_NAME}\",\n"
printf "      \"env\": {\n"
printf "        \"KEYS_CONFIG_PATH\": \"/path/to/keys.json\"\n"
printf "      }\n"
printf "    }\n"
printf "  }\n"
printf "}\n"
printf "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ "$REPO" == "testpypi" ]; then
    printf "\n${YELLOW}💡 提示:${NC}\n"
    printf "   测试成功后，使用选项 ${GREEN}2${NC} 发布到正式 PyPI\n"
fi

printf "\n${GREEN}发布成功！${NC} 🎉\n\n"
printf "${CYAN}💡 下一步:${NC}\n"
printf "   1. 等待 2-5 分钟让 PyPI 同步\n"
printf "   2. 安装 pipx: ${GREEN}pip install pipx${NC}\n"
printf "   3. 测试: ${GREEN}pipx install ${PACKAGE_NAME}${NC}\n"
printf "   4. 分享给其他人使用\n\n"

printf "${CYAN}📚 了解 PIPX:${NC}\n"
printf "   PIPX 是 Python 版的 NPX，专门用于安装 CLI 工具\n"
printf "   文档: ${BLUE}https://pypa.github.io/pipx/${NC}\n\n"

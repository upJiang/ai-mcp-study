#!/bin/bash
# 自动生成 docker-compose.yml（支持混合包类型）

set -e

PACKAGES_DIR="./packages"
OUTPUT_FILE="./docker-compose.yml"

echo "========================================="
echo "自动生成 Docker Compose 配置"
echo "========================================="

# 开始生成 docker-compose.yml
cat > "$OUTPUT_FILE" <<'EOF'
version: '3.8'

services:
EOF

# 扫描 packages 目录
echo "扫描 packages 目录..."
PYTHON_COUNT=0
NPM_COUNT=0

for dir in "$PACKAGES_DIR"/*/ ; do
    if [ -d "$dir" ]; then
        package_name=$(basename "$dir")
        has_requirements=false
        has_package_json=false

        # 检查包类型
        if [ -f "$dir/requirements.txt" ]; then
            has_requirements=true
        fi
        if [ -f "$dir/package.json" ]; then
            has_package_json=true
        fi

        # 处理 Python MCP 包（有 requirements.txt）
        if [ "$has_requirements" = true ]; then
            echo "✓ 发现 Python MCP 项目: $package_name"
            PYTHON_COUNT=$((PYTHON_COUNT + 1))

            # 生成 service 名称（转换为小写，替换下划线为连字符）
            service_name=$(echo "$package_name" | tr '[:upper:]' '[:lower:]' | tr '_' '-')

            # 添加 service 配置
            cat >> "$OUTPUT_FILE" <<EOF
  $service_name:
    build:
      context: ./packages/$package_name
      dockerfile: ../../deployment/Dockerfile.python-mcp
    container_name: mcp-$service_name
    environment:
      - PYTHONUNBUFFERED=1
      - MCP_TRANSPORT=http
      - MCP_PORT=8000
    restart: unless-stopped
    networks:
      - mcp-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

EOF
        # 跳过 npm 包（仅统计）
        elif [ "$has_package_json" = true ]; then
            echo "⊗ 跳过 npm 包: $package_name (由 publish.yml 处理)"
            NPM_COUNT=$((NPM_COUNT + 1))
        else
            echo "⚠️  未识别的包类型: $package_name (无 requirements.txt 或 package.json)"
        fi
    fi
done

# 添加网络配置
cat >> "$OUTPUT_FILE" <<'EOF'
networks:
  mcp-network:
    driver: bridge
EOF

echo ""
echo "✓ docker-compose.yml 生成完成"
echo ""
echo "📊 包统计："
echo "  - Python MCP 服务: $PYTHON_COUNT"
echo "  - npm 包（已跳过）: $NPM_COUNT"
echo ""
echo "生成的 Docker 服务列表："
if [ $PYTHON_COUNT -gt 0 ]; then
    grep "container_name:" "$OUTPUT_FILE" | awk '{print "  -", $3}'
else
    echo "  （无 Python 服务需要部署）"
fi
echo ""
echo "========================================="

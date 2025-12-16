# 服务器初始化指南

## 当前状态

✅ 代码已推送到 GitHub
✅ 所有部署脚本已创建
✅ GitHub Actions 工作流已配置
❌ **服务器尚未初始化**（这导致 GitHub Actions 失败）

## GitHub Actions 失败原因

```
err: bash: line 7: cd: /opt/mcp-services/ai-mcp-study: No such file or directory
```

GitHub Actions 尝试访问 `/opt/mcp-services/ai-mcp-study` 目录，但该目录不存在。

## 解决方案：初始化服务器（仅需执行一次）

### 第一步：登录服务器

```bash
ssh root@junfeng530.xyz
```

如果使用其他用户名，请替换 `root`。

### 第二步：执行初始化脚本

复制并粘贴以下完整命令（一次性执行）：

```bash
bash -c "$(cat <<'EOF'
set -e

echo "========================================="
echo "MCP 服务器一键初始化"
echo "========================================="

# 1. 创建工作目录
echo ""
echo "步骤 1/7: 创建工作目录..."
sudo mkdir -p /opt/mcp-services
sudo chown $USER:$USER /opt/mcp-services
echo "✓ 工作目录创建完成"

# 2. 克隆代码仓库
echo ""
echo "步骤 2/7: 克隆代码仓库..."
cd /opt/mcp-services

if [ -d "ai-mcp-study" ]; then
    echo "⚠️  目录已存在，拉取最新代码..."
    cd ai-mcp-study
    git pull origin main
else
    git clone git@github.com:upJiang/ai-mcp-study.git
    cd ai-mcp-study
fi
echo "✓ 代码克隆完成"

# 3. 进入 mcp-list 目录
cd mcp-list

# 4. 生成 docker-compose.yml
echo ""
echo "步骤 3/7: 生成 docker-compose.yml..."
chmod +x deployment/generate-compose.sh
./deployment/generate-compose.sh
echo "✓ docker-compose.yml 生成完成"

# 5. 生成 Nginx 配置
echo ""
echo "步骤 4/7: 生成 Nginx 配置..."
chmod +x deployment/generate-nginx.sh
./deployment/generate-nginx.sh
echo "✓ Nginx 配置生成完成"

# 6. 部署 Nginx 配置
echo ""
echo "步骤 5/7: 部署 Nginx 配置..."
sudo cp deployment/nginx/mcp-services.conf /etc/nginx/conf.d/
echo "✓ Nginx 配置文件已复制"

# 7. 测试 Nginx 配置
echo ""
echo "步骤 6/7: 测试 Nginx 配置..."
sudo nginx -t
echo "✓ Nginx 配置测试通过"

# 8. 重载 Nginx
echo ""
echo "步骤 7/7: 重载 Nginx..."
sudo systemctl reload nginx
echo "✓ Nginx 已重载"

echo ""
echo "========================================="
echo "✅ 服务器初始化完成！"
echo "========================================="
echo ""
echo "📍 生成的配置文件位置："
echo "  - docker-compose.yml: /opt/mcp-services/ai-mcp-study/mcp-list/docker-compose.yml"
echo "  - Nginx 配置: /etc/nginx/conf.d/mcp-services.conf"
echo ""
echo "🔍 查看生成的服务列表："
echo "  cd /opt/mcp-services/ai-mcp-study/mcp-list"
echo "  docker-compose config --services"
echo ""
echo "📋 下一步选择："
echo "  选项 1: 等待 GitHub Actions 自动部署（推荐）"
echo "           - 在 GitHub 仓库页面重新运行失败的工作流"
echo "           - 或者推送任意代码变更触发自动部署"
echo ""
echo "  选项 2: 立即手动部署"
echo "           - cd /opt/mcp-services/ai-mcp-study"
echo "           - chmod +x deployment/deploy.sh"
echo "           - ./deployment/deploy.sh"
echo ""
EOF
)"
```

### 第三步：验证初始化结果

执行完成后，你应该看到：

```
✅ 服务器初始化完成！
```

然后验证目录结构：

```bash
# 验证目录存在
ls -la /opt/mcp-services/ai-mcp-study

# 查看生成的服务列表
cd /opt/mcp-services/ai-mcp-study/mcp-list
docker-compose config --services

# 查看 Nginx 配置
cat deployment/nginx/mcp-services.conf
```

## 初始化完成后的选择

### 选项 1：等待 GitHub Actions 自动部署（推荐）

1. 在 GitHub 仓库页面，进入 **Actions** 标签
2. 找到失败的工作流运行记录
3. 点击 **Re-run all jobs** 按钮重新运行

**或者**

推送任意代码变更，触发自动部署：

```bash
# 在本地项目目录
git commit --allow-empty -m "trigger deployment"
git push origin main
```

GitHub Actions 会自动：
- 拉取最新代码
- 生成 docker-compose.yml
- 生成 Nginx 配置
- 构建并启动所有 Docker 容器
- 健康检查验证

### 选项 2：立即手动部署

如果你想立即看到结果，可以在服务器上手动执行部署：

```bash
cd /opt/mcp-services/ai-mcp-study
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

## 验证部署成功

### 1. 检查容器状态

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list
docker-compose ps
```

应该看到所有服务状态为 `Up`。

### 2. 测试服务访问

```bash
# 根据实际部署的服务名称测试
# 格式：curl https://junfeng530.xyz/mcp/{service-name}

# 示例（实际服务名称可能不同）：
curl https://junfeng530.xyz/mcp/openapigenerator
```

### 3. 查看服务日志

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list

# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f openapigenerator
```

## 常见问题排查

### 问题1：Git 克隆失败

**错误**：`Permission denied (publickey)`

**解决**：
```bash
# 检查服务器是否配置了 GitHub SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# 将公钥添加到 GitHub Settings → SSH keys
```

### 问题2：Docker Compose 命令不存在

**错误**：`docker-compose: command not found`

**解决**：
```bash
# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 问题3：Nginx 配置测试失败

**错误**：`nginx: configuration file /etc/nginx/nginx.conf test failed`

**解决**：
```bash
# 查看详细错误
sudo nginx -t

# 检查配置文件语法
sudo cat /etc/nginx/conf.d/mcp-services.conf

# 如果是 SSL 证书问题，检查证书路径
ls -la /etc/letsencrypt/live/junfeng530.xyz/
```

### 问题4：容器启动失败

**错误**：容器状态显示 `Exit 1` 或 `Restarting`

**解决**：
```bash
# 查看容器日志
docker-compose logs [service-name]

# 常见原因：
# 1. requirements.txt 依赖安装失败
# 2. server.py 代码错误
# 3. 端口冲突

# 重新构建特定服务
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

## 后续维护

初始化完成后，所有后续部署将**完全自动化**：

1. ✅ 开发者推送代码到 main 分支
2. ✅ GitHub Actions 自动触发部署
3. ✅ 服务自动更新（无需手动操作）

你无需：
- ❌ 手动 SSH 到服务器
- ❌ 手动修改 Nginx 配置
- ❌ 手动重启容器
- ❌ 手动生成配置文件

## 总结

| 操作 | 频率 | 方式 |
|------|------|------|
| 服务器初始化 | 仅一次 | 本指南 |
| 代码部署 | 每次 push | GitHub Actions 自动 |
| Nginx 配置更新 | 自动 | GitHub Actions 自动 |
| 容器重启 | 自动 | GitHub Actions 自动 |
| 新增包部署 | 自动 | GitHub Actions 自动 |

---

**需要帮助？**

- 查看 GitHub Actions 日志：GitHub 仓库 → Actions 标签
- 查看服务器日志：`docker-compose logs -f`
- 查看 Nginx 日志：`sudo tail -f /var/log/nginx/mcp-services-error.log`

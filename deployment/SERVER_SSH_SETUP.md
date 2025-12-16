# 服务器 SSH 密钥配置指南

## 🎯 问题说明

服务器使用 HTTPS 拉取 GitHub 代码时经常超时：
```
fatal: unable to access 'https://github.com/upJiang/ai-mcp-study.git/': Connection timed out
```

**解决方案：使用 SSH 方式拉取代码**

---

## 📋 配置步骤

### 1. SSH 登录到服务器

```bash
ssh user@junfeng530.xyz
```

### 2. 生成 SSH 密钥（如果还没有）

```bash
# 检查是否已有 SSH 密钥
ls -la ~/.ssh/

# 如果没有 id_rsa.pub，生成新密钥
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 按 Enter 使用默认文件名
# 按 Enter 跳过密码（或设置密码）
```

### 3. 查看并复制公钥

```bash
cat ~/.ssh/id_rsa.pub
```

**输出示例：**
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDxxxxxx... your_email@example.com
```

**复制整行内容**（从 `ssh-rsa` 开始到邮箱结束）

### 4. 添加公钥到 GitHub

1. 打开 GitHub：https://github.com/settings/keys
2. 点击 **"New SSH key"**
3. **Title**: 输入 `MCP-Server` 或其他名称
4. **Key**: 粘贴刚才复制的公钥
5. 点击 **"Add SSH key"**

### 5. 测试 SSH 连接

```bash
ssh -T git@github.com
```

**成功输出：**
```
Hi upJiang! You've successfully authenticated, but GitHub does not provide shell access.
```

### 6. 切换仓库远程 URL 为 SSH

```bash
cd /opt/mcp-services/ai-mcp-study

# 查看当前 URL
git remote get-url origin

# 如果是 HTTPS URL，切换为 SSH
git remote set-url origin git@github.com:upJiang/ai-mcp-study.git

# 验证切换成功
git remote get-url origin
# 应该输出: git@github.com:upJiang/ai-mcp-study.git
```

### 7. 测试拉取代码

```bash
cd /opt/mcp-services/ai-mcp-study
git fetch origin main
```

**应该能快速成功，不再超时！** ✅

---

## 🔄 自动化部署脚本更新

部署脚本已更新，会自动检测并切换到 SSH URL：

```yaml
# .github/workflows/deploy-python-mcp.yml
script: |
  cd /opt/mcp-services/ai-mcp-study

  # 自动切换到 SSH URL
  CURRENT_URL=$(git remote get-url origin)
  if [[ "$CURRENT_URL" == https* ]]; then
    git remote set-url origin git@github.com:upJiang/ai-mcp-study.git
  fi

  git fetch origin main
  git reset --hard origin/main
```

---

## ✅ 验证清单

完成以下步骤后，部署应该能正常工作：

- [ ] 服务器上已生成 SSH 密钥
- [ ] 公钥已添加到 GitHub
- [ ] SSH 连接测试成功（`ssh -T git@github.com`）
- [ ] 仓库远程 URL 已切换为 SSH
- [ ] 手动测试 `git fetch` 成功
- [ ] 推送新代码触发自动部署成功

---

## 🚨 常见问题

### Q1: Permission denied (publickey)

**问题：**
```
Permission denied (publickey).
fatal: Could not read from remote repository.
```

**解决：**
1. 确认公钥已添加到 GitHub
2. 检查 SSH agent：
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_rsa
   ```

### Q2: Host key verification failed

**问题：**
```
Host key verification failed.
fatal: Could not read from remote repository.
```

**解决：**
```bash
# 添加 GitHub 到已知主机
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### Q3: 还是很慢

**问题：** SSH 连接建立很慢

**解决：** 配置 SSH 复用连接
```bash
# 编辑 ~/.ssh/config
cat >> ~/.ssh/config <<EOF
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
EOF

# 创建 sockets 目录
mkdir -p ~/.ssh/sockets
```

---

## 📞 需要帮助？

如果配置过程中遇到问题，请提供以下信息：

```bash
# 1. SSH 密钥信息
ls -la ~/.ssh/

# 2. Git 远程 URL
cd /opt/mcp-services/ai-mcp-study
git remote -v

# 3. SSH 测试输出
ssh -vT git@github.com 2>&1 | head -20
```

---

## 🎉 完成后

配置完成后，您只需：

```bash
# 本地推送代码
git push

# GitHub Actions 自动部署到服务器（使用 SSH 拉取）
# 再也不会超时了！✨
```

# 🚀 服务器 SSH 快速配置（2 分钟完成）

## 问题现状

部署失败原因：
```
Permission denied (publickey).
fatal: Could not read from remote repository.
```

**解决方案：** 在服务器上配置 SSH 密钥并添加到 GitHub

---

## ⚡ 快速配置（复制粘贴即可）

### 步骤 1：SSH 登录服务器

```bash
ssh user@junfeng530.xyz
```

### 步骤 2：执行配置命令（一次性复制全部）

```bash
# 生成 SSH 密钥（如果已有则跳过）
if [ ! -f ~/.ssh/id_rsa ]; then
  ssh-keygen -t rsa -b 4096 -C "deploy@server" -f ~/.ssh/id_rsa -N ""
  echo "✓ SSH 密钥已生成"
else
  echo "✓ SSH 密钥已存在"
fi

# 添加 GitHub 到 known_hosts
mkdir -p ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts 2>/dev/null
echo "✓ GitHub 已添加到 known_hosts"

# 显示公钥
echo ""
echo "========================================="
echo "📋 您的 SSH 公钥（请复制下面整行）："
echo "========================================="
cat ~/.ssh/id_rsa.pub
echo "========================================="
echo ""
echo "⬆️  请复制上面的公钥（从 ssh-rsa 开始到最后）"
```

### 步骤 3：添加公钥到 GitHub

1. **复制** 上面命令输出的公钥（整行，从 `ssh-rsa` 开始）

2. **打开 GitHub SSH 密钥页面**：
   👉 https://github.com/settings/keys

3. **点击** "New SSH key" 按钮

4. **填写信息**：
   - **Title**: `MCP-Deploy-Server` （或任意名称）
   - **Key**: 粘贴刚才复制的公钥

5. **点击** "Add SSH key" 保存

### 步骤 4：测试连接

在服务器上运行：

```bash
ssh -T git@github.com
```

**期望输出：**
```
Hi upJiang! You've successfully authenticated, but GitHub does not provide shell access.
```

✅ 看到这个消息说明配置成功！

### 步骤 5：切换仓库 URL 并测试

```bash
cd /opt/mcp-services/ai-mcp-study

# 切换到 SSH URL
git remote set-url origin git@github.com:upJiang/ai-mcp-study.git

# 测试拉取
git fetch origin main

# 应该立即成功！
```

✅ 如果 fetch 成功，说明一切配置正确！

---

## 🎉 完成！

配置完成后：

1. **本地推送代码**：
   ```bash
   git push
   ```

2. **自动触发部署**：
   - GitHub Actions 自动运行
   - SSH 到服务器
   - 拉取代码（使用 SSH，不再超时）
   - 自动构建并部署服务

3. **访问服务**：
   ```
   https://junfeng530.xyz/mcp/eventanalyzer
   ```

---

## 🔍 验证部署是否成功

### 方法 1：查看 GitHub Actions 日志

访问：https://github.com/upJiang/ai-mcp-study/actions

应该看到：
```
✓ 部署完成！所有服务运行正常
```

### 方法 2：SSH 到服务器查看容器

```bash
ssh user@junfeng530.xyz
cd /opt/mcp-services/ai-mcp-study/mcp-list

# 查看运行中的容器
docker-compose ps

# 查看服务日志
docker-compose logs -f eventanalyzer
```

### 方法 3：访问服务

```bash
curl https://junfeng530.xyz/mcp/eventanalyzer
```

---

## ❓ 常见问题

### Q: ssh-keygen 提示文件已存在

**解决：** 使用现有密钥即可，跳过生成步骤

### Q: Permission denied 仍然出现

**检查清单：**
1. ✅ 公钥已添加到 GitHub
2. ✅ `ssh -T git@github.com` 测试成功
3. ✅ 仓库 URL 已切换为 SSH（`git@github.com:...`）

**重新配置：**
```bash
# 删除旧密钥
rm -f ~/.ssh/id_rsa ~/.ssh/id_rsa.pub

# 重新生成
ssh-keygen -t rsa -b 4096 -C "deploy@server" -f ~/.ssh/id_rsa -N ""

# 显示新公钥并重新添加到 GitHub
cat ~/.ssh/id_rsa.pub
```

### Q: git fetch 仍然超时

**可能原因：** 防火墙阻止 SSH（22 端口）

**临时解决（使用 HTTPS over 443）：**
```bash
# 编辑 SSH 配置
cat >> ~/.ssh/config <<EOF
Host github.com
    Hostname ssh.github.com
    Port 443
    User git
EOF

# 测试
ssh -T git@github.com
```

---

## 📞 需要帮助？

如果遇到问题，请提供：

```bash
# 1. SSH 密钥状态
ls -la ~/.ssh/

# 2. Git 远程 URL
cd /opt/mcp-services/ai-mcp-study
git remote -v

# 3. SSH 连接测试详细输出
ssh -vT git@github.com 2>&1 | head -30
```

---

## 🎯 总结

**配置前：**
- ❌ HTTPS 拉取代码超时
- ❌ 部署失败

**配置后：**
- ✅ SSH 拉取代码秒完成
- ✅ 自动部署成功
- ✅ 添加新服务只需 `git push`

**完成配置后，您就可以享受完全自动化的部署流程了！** 🚀

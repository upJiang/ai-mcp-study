# 🔧 Nginx 配置修复指南

## 问题说明

Nginx 报错：`nginx: [emerg] host not found in upstream "mcp-eventanalyzer"`

**原因**：Nginx 进程运行在宿主机上，无法访问 Docker 内部网络来解析容器名称。

**解决方案**：使用端口映射 + localhost 代替容器名称。

---

## 📋 修复步骤

### 1️⃣ 在服务器上更新配置文件

SSH 登录到服务器后，执行以下操作：

```bash
cd /opt/mcp-services/ai-mcp-study

# 拉取最新代码（包含修复）
git pull origin main

# 进入 mcp-list 目录
cd mcp-list
```

### 2️⃣ 重新生成 Docker Compose 配置

```bash
# 重新生成 docker-compose.yml（现在包含端口映射）
./deployment/generate-compose.sh

# 查看生成的配置，确认端口映射已添加
cat docker-compose.yml | grep -A 5 "ports:"
```

**预期输出**：
```yaml
    ports:
      - "8100:8000"  # 映射容器端口到宿主机
```

### 3️⃣ 重启 Docker 容器

```bash
# 停止旧容器
docker-compose down

# 重新构建并启动（应用新的端口映射）
docker-compose up -d --build

# 验证容器状态
docker-compose ps
```

**预期输出**：
```
NAME                  IMAGE                     STATUS        PORTS
mcp-eventanalyzer     mcp-list-eventanalyzer    Up X seconds  0.0.0.0:8100->8000/tcp
```

### 4️⃣ 测试容器端口

```bash
# 测试容器内部
docker exec mcp-eventanalyzer curl -s http://localhost:8000/sse

# 测试宿主机端口映射
curl -s http://127.0.0.1:8100/sse
```

**预期输出**：两个命令都应该返回 SSE 连接响应。

### 5️⃣ 备份并更新 Nginx 配置

```bash
# 备份当前配置
sudo cp /www/server/nginx/conf/nginx.conf /www/server/nginx/conf/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# 复制修复后的配置（从本地仓库）
sudo cp ~/Desktop/studyProject/ai-mcp-study/nginx.conf.fixed /www/server/nginx/conf/nginx.conf

# 或者直接在服务器上编辑 nginx.conf
# 找到 location /mcp/eventanalyzer 块
# 将 proxy_pass http://mcp-eventanalyzer:8000;
# 改为 proxy_pass http://127.0.0.1:8100;
```

### 6️⃣ 测试并重载 Nginx

```bash
# 测试配置语法
sudo nginx -t
```

**预期输出**：
```
nginx: the configuration file /www/server/nginx/conf/nginx.conf syntax is ok
nginx: configuration file /www/server/nginx/conf/nginx.conf test is successful
```

```bash
# 重载 Nginx
sudo systemctl reload nginx
```

### 7️⃣ 验证外部访问

```bash
# 测试 HTTPS 访问
curl -I https://junfeng530.xyz/mcp/eventanalyzer
```

**预期输出**：应该看到 HTTP 200 或 SSE 相关的响应头，而不是 404。

---

## ✅ 完成验证

在 Cursor 中添加 MCP 服务器配置：

```json
{
  "mcpServers": {
    "eventanalyzer": {
      "url": "https://junfeng530.xyz/mcp/eventanalyzer"
    }
  }
}
```

重启 Cursor，检查 MCP 是否成功连接。

---

## 🎯 关键修改点

### docker-compose.yml
```yaml
ports:
  - "8100:8000"  # ✅ 新增：映射容器端口到宿主机
```

### nginx.conf
```nginx
location /mcp/eventanalyzer {
    # ...
    proxy_pass http://127.0.0.1:8100;  # ✅ 改用 localhost + 端口
    # 旧值：proxy_pass http://mcp-eventanalyzer:8000;  # ❌ Nginx 无法解析
}
```

---

## 🔍 排查命令

如果仍有问题，运行以下命令收集信息：

```bash
# 检查容器是否正在运行
docker ps | grep eventanalyzer

# 查看容器日志
docker-compose logs --tail=50 eventanalyzer

# 检查端口监听
netstat -tlnp | grep 8100

# 查看 Nginx 错误日志
sudo tail -50 /www/wwwlogs/md-error.log

# 测试 Nginx 到容器的连接
curl -v http://127.0.0.1:8100/sse
```

---

## 📝 未来部署

之后添加新的 Python MCP 服务时，使用自动化脚本即可：

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list

# 1. 生成 docker-compose.yml（自动分配端口 8100, 8101, 8102...）
./deployment/generate-compose.sh

# 2. 生成 Nginx 配置（自动读取端口映射）
./deployment/generate-nginx.sh

# 3. 应用配置
docker-compose up -d --build
sudo cp deployment/nginx/mcp-services.conf /etc/nginx/conf.d/
sudo nginx -t && sudo systemctl reload nginx
```

脚本已经更新为自动处理端口映射和 localhost 配置。

# MCP服务器部署完整指南

本文档提供Node.js和Python两个版本的MCP服务器的完整部署方案。

## 目录

- [部署方式对比](#部署方式对比)
- [Node.js版本部署](#nodejs版本部署)
- [Python版本部署](#python版本部署)
- [Cursor配置指南](#cursor配置指南)
- [HTTPS配置](#https配置)
- [故障排查](#故障排查)

---

## 部署方式对比

| 部署方式 | Node.js | Python | 推荐场景 |
|---------|---------|--------|---------|
| **本地STDIO** | ✅ 推荐 | ⚠️ 需Python环境 | 个人开发 |
| **本地HTTP** | ✅ | ✅ | 测试调试 |
| **Docker** | ✅ | ✅ 推荐 | 团队共享 |
| **PM2/Supervisor** | ✅ 推荐 | ✅ | 生产环境 |
| **Systemd** | ✅ | ✅ | Linux服务器 |
| **npm发布** | ✅ 推荐 | ❌ | 公开分发 |

---

## Node.js版本部署

### 方式1: 本地开发（STDIO）- 推荐

**适用场景**：个人使用，在Cursor中直接配置

**步骤**：

1. 安装依赖
```bash
cd node-mcp-demo
yarn install  # 或 npm install
```

2. 配置Cursor

编辑 `~/.config/cursor/config.json`（macOS/Linux）或 `%APPDATA%\Cursor\config.json`（Windows）：

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["tsx", "/Users/your-path/node-mcp-demo/src/index.ts"],
      "env": {
        "KEYS_CONFIG_PATH": "/Users/your-path/ccReport/config/keys.json"
      }
    }
  }
}
```

3. 重启Cursor即可使用！

### 方式2: 本地HTTP模式

**适用场景**：测试调试、多客户端连接

**启动**：

```bash
cd node-mcp-demo
MCP_TRANSPORT=http MCP_PORT=8000 yarn dev
# 服务运行在: http://localhost:8000/mcp
```

**Cursor配置**：

```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 方式3: 发布到npm（推荐分发）

**适用场景**：公开分发、团队共享

**步骤**：

1. 构建项目
```bash
cd node-mcp-demo
yarn build
```

2. 登录npm
```bash
npm login
```

3. 发布
```bash
npm publish
```

4. 用户使用
```bash
npx claude-stats-mcp
```

**Cursor配置**：
```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["claude-stats-mcp"]
    }
  }
}
```

### 方式4: PM2生产部署

**适用场景**：服务器生产环境、自动重启

**步骤**：

1. 安装PM2
```bash
npm install -g pm2
```

2. 构建项目
```bash
cd node-mcp-demo
yarn build
```

3. 使用部署脚本
```bash
chmod +x deploy-node.sh
./deploy-node.sh
# 选择: 1) PM2
```

或手动启动：

```bash
pm2 start ecosystem.config.js --env production
pm2 save
pm2 startup
```

4. 管理命令
```bash
pm2 status                # 查看状态
pm2 logs claude-stats-mcp # 查看日志
pm2 restart claude-stats-mcp # 重启
pm2 stop claude-stats-mcp    # 停止
```

### 方式5: Docker部署

**适用场景**：容器化环境、多环境部署

**步骤**：

1. 构建镜像
```bash
cd node-mcp-demo
yarn build
docker build -t claude-stats-mcp:latest .
```

2. 启动容器
```bash
docker-compose up -d
```

3. 管理命令
```bash
docker-compose ps        # 查看状态
docker-compose logs -f   # 查看日志
docker-compose restart   # 重启
docker-compose down      # 停止
```

---

## Python版本部署

### 方式1: Docker部署（推荐）

**适用场景**：无需Python环境、一键部署

**步骤**：

1. 启动
```bash
cd python-mcp-demo
docker-compose up -d
```

2. 查看日志
```bash
docker-compose logs -f
```

3. Cursor配置
```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 方式2: Supervisor部署

**适用场景**：Linux服务器、系统服务管理

**步骤**：

1. 使用部署脚本
```bash
cd python-mcp-demo
chmod +x deploy-python.sh
./deploy-python.sh
# 选择: 2) Supervisor
```

2. 手动配置（如需）
```bash
# 编辑supervisor.conf，修改路径
sudo cp supervisor.conf /etc/supervisor/conf.d/claude-stats-mcp.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start claude-stats-mcp
```

3. 管理命令
```bash
sudo supervisorctl status claude-stats-mcp  # 查看状态
sudo supervisorctl tail -f claude-stats-mcp # 查看日志
sudo supervisorctl restart claude-stats-mcp # 重启
sudo supervisorctl stop claude-stats-mcp    # 停止
```

### 方式3: Systemd部署

**适用场景**：现代Linux系统、开机自启

**步骤**：

1. 使用部署脚本
```bash
cd python-mcp-demo
chmod +x deploy-python.sh
./deploy-python.sh
# 选择: 3) Systemd
```

2. 管理命令
```bash
sudo systemctl status claude-stats-mcp  # 查看状态
sudo journalctl -u claude-stats-mcp -f  # 查看日志
sudo systemctl restart claude-stats-mcp # 重启
sudo systemctl stop claude-stats-mcp    # 停止
```

### 方式4: 本地Python运行

**适用场景**：开发测试（需要Python环境）

**步骤**：

1. 创建虚拟环境
```bash
cd python-mcp-demo
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动服务
```bash
# STDIO模式
python server.py

# HTTP模式
MCP_TRANSPORT=http MCP_PORT=8000 python server.py
```

---

## Cursor配置指南

### 配置文件位置

- **macOS/Linux**: `~/.config/cursor/config.json`
- **Windows**: `%APPDATA%\Cursor\config.json`

### 配置示例

#### 1. Node.js STDIO模式（推荐本地使用）

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["tsx", "/完整路径/node-mcp-demo/src/index.ts"],
      "env": {
        "KEYS_CONFIG_PATH": "/完整路径/ccReport/config/keys.json"
      }
    }
  }
}
```

**注意**：
- 必须使用**绝对路径**
- 确保`keys.json`文件存在
- 重启Cursor后生效

#### 2. HTTP模式（适用于两种语言）

```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**优点**：
- 语言无关
- 可以远程访问
- 容易调试

#### 3. npm包模式（发布后）

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "npx",
      "args": ["claude-stats-mcp"]
    }
  }
}
```

#### 4. Python虚拟环境模式

```json
{
  "mcpServers": {
    "claude-stats": {
      "command": "/完整路径/python-mcp-demo/venv/bin/python",
      "args": ["/完整路径/python-mcp-demo/server.py"]
    }
  }
}
```

---

## HTTPS配置

### 1. 获取SSL证书（Let's Encrypt）

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu/Debian
# 或
brew install certbot  # macOS

# 获取证书
sudo certbot --nginx -d your-domain.com
```

### 2. Nginx配置

**Node.js版本**：使用 `node-mcp-demo/nginx-node.conf`

**Python版本**：使用 `python-mcp-demo/nginx-python.conf`

**安装步骤**：

```bash
# 复制配置文件
sudo cp nginx-node.conf /etc/nginx/sites-available/claude-stats-mcp
# 或
sudo cp nginx-python.conf /etc/nginx/sites-available/claude-stats-mcp

# 修改域名
sudo nano /etc/nginx/sites-available/claude-stats-mcp
# 将 your-domain.com 替换为实际域名

# 启用配置
sudo ln -s /etc/nginx/sites-available/claude-stats-mcp /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 3. Cursor HTTPS配置

```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

---

## 故障排查

### 问题1: Cursor无法连接MCP服务器

**症状**：
- Cursor中看不到MCP工具
- 提示连接失败

**排查步骤**：

1. 检查配置文件路径是否正确（使用绝对路径）
```bash
# macOS/Linux
cat ~/.config/cursor/config.json

# Windows
type %APPDATA%\Cursor\config.json
```

2. 检查服务器是否运行（HTTP模式）
```bash
curl http://localhost:8000/mcp
lsof -i :8000  # 查看端口占用
```

3. 查看Cursor开发者工具
- 打开Cursor
- Help → Toggle Developer Tools
- 查看Console标签的错误信息

4. 检查命令是否可执行
```bash
# 测试Node.js
npx tsx /path/to/node-mcp-demo/src/index.ts

# 测试Python
python /path/to/python-mcp-demo/server.py
```

### 问题2: 找不到配置文件

**错误信息**：
```
加载API Key配置失败: 配置文件不存在
```

**解决方案**：

```bash
# 检查文件是否存在
ls -la /path/to/ccReport/config/keys.json

# 创建符号链接
cd node-mcp-demo
mkdir -p config
ln -s ../../ccReport/config/keys.json config/keys.json

# 或设置环境变量
export KEYS_CONFIG_PATH=/absolute/path/to/keys.json
```

### 问题3: API请求失败

**错误信息**：
```
获取统计数据失败
```

**排查步骤**：

1. 检查网络连接
```bash
ping as.imds.ai
curl https://as.imds.ai/apiStats/api
```

2. 检查API Key是否有效
```bash
# 查看keys.json内容
cat config/keys.json
```

3. 查看服务器日志
```bash
# PM2
pm2 logs claude-stats-mcp

# Docker
docker-compose logs -f

# Supervisor
sudo supervisorctl tail -f claude-stats-mcp

# Systemd
sudo journalctl -u claude-stats-mcp -f
```

### 问题4: 端口被占用

**错误信息**：
```
Error: listen EADDRINUSE: address already in use :::8000
```

**解决方案**：

```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或更换端口
MCP_PORT=8001 yarn dev
```

### 问题5: TypeScript编译错误

**解决方案**：

```bash
cd node-mcp-demo

# 清理缓存
rm -rf dist node_modules yarn.lock

# 重新安装
yarn install

# 构建
yarn build
```

### 问题6: Python依赖安装失败

**解决方案**：

```bash
cd python-mcp-demo

# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用清华源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 性能优化

### Node.js优化

1. **开启缓存**（已内置5分钟缓存）
2. **限制并发请求数**
3. **使用PM2集群模式**

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'claude-stats-mcp',
    script: './dist/index.js',
    instances: 2,  // 使用2个进程
    exec_mode: 'cluster'
  }]
};
```

### Python优化

1. **使用异步处理**（已使用asyncio）
2. **Docker资源限制**

```yaml
# docker-compose.yml
services:
  claude-stats-mcp:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## 安全建议

### 1. 保护API Key

```bash
# 确保keys.json不被提交
echo "config/keys.json" >> .gitignore

# 设置文件权限
chmod 600 config/keys.json
```

### 2. HTTPS传输

生产环境必须使用HTTPS：
- 使用Let's Encrypt免费证书
- 配置Nginx反向代理
- 启用SSL/TLS加密

### 3. 访问控制

```nginx
# 限制IP访问
location /mcp {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://localhost:8000;
}

# 或使用Basic Auth
location /mcp {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8000;
}
```

### 4. 请求限流

Nginx配置：

```nginx
# 限流配置
limit_req_zone $binary_remote_addr zone=mcp:10m rate=10r/s;

location /mcp {
    limit_req zone=mcp burst=20 nodelay;
    proxy_pass http://localhost:8000;
}
```

---

## 监控和日志

### Node.js日志

**PM2日志**：
```bash
pm2 logs claude-stats-mcp
pm2 logs claude-stats-mcp --lines 100
pm2 logs claude-stats-mcp --err  # 只看错误
```

**文件日志**：
```bash
# 添加到ecosystem.config.js
apps: [{
  error_file: './logs/error.log',
  out_file: './logs/output.log',
  log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
}]
```

### Python日志

**Supervisor日志**：
```bash
sudo supervisorctl tail -f claude-stats-mcp
sudo supervisorctl tail -f claude-stats-mcp stderr
```

**Systemd日志**：
```bash
sudo journalctl -u claude-stats-mcp -f
sudo journalctl -u claude-stats-mcp --since "1 hour ago"
```

### Nginx日志

```bash
# 访问日志
tail -f /var/log/nginx/claude-stats-mcp-access.log

# 错误日志
tail -f /var/log/nginx/claude-stats-mcp-error.log
```

---

## 备份和恢复

### 配置文件备份

```bash
# 备份配置
tar -czf mcp-backup-$(date +%Y%m%d).tar.gz \
  ccReport/config/keys.json \
  node-mcp-demo/.env \
  python-mcp-demo/.env

# 恢复
tar -xzf mcp-backup-20241208.tar.gz
```

### Docker数据卷备份

```bash
# 备份Docker卷
docker run --rm \
  -v python-mcp-demo_config:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/config-backup.tar.gz /data

# 恢复
docker run --rm \
  -v python-mcp-demo_config:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/config-backup.tar.gz -C /
```

---

## 高可用部署

### 使用负载均衡

```nginx
upstream mcp_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    location /mcp {
        proxy_pass http://mcp_backend;
    }
}
```

### 健康检查

```bash
# 添加健康检查脚本
#!/bin/bash
# healthcheck.sh

curl -f http://localhost:8000/health || exit 1
```

---

## 更新和维护

### Node.js更新

```bash
cd node-mcp-demo

# 更新依赖
yarn upgrade

# 重新构建
yarn build

# PM2重启
pm2 restart claude-stats-mcp
```

### Python更新

```bash
cd python-mcp-demo

# 更新依赖
pip install -r requirements.txt --upgrade

# Docker重新构建
docker-compose build --no-cache
docker-compose up -d
```

---

## 性能基准

### 预期性能

- **响应时间**：< 1秒（含API调用）
- **并发处理**：50 req/s
- **内存占用**：
  - Node.js: ~100MB
  - Python: ~80MB
- **CPU使用**：< 5%（空闲时）

### 压力测试

```bash
# 使用ab测试
ab -n 100 -c 10 http://localhost:8000/mcp

# 使用wrk测试
wrk -t4 -c100 -d30s http://localhost:8000/mcp
```

---

**部署完成后，记得在Cursor中重新加载配置！** 🚀


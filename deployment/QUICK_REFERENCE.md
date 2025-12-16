# 快速参考手册

## 🚀 一键初始化服务器

**仅需执行一次，在服务器上运行：**

```bash
ssh root@junfeng530.xyz

bash -c "$(cat <<'EOF'
set -e
sudo mkdir -p /opt/mcp-services && sudo chown $USER:$USER /opt/mcp-services
cd /opt/mcp-services
[ -d "ai-mcp-study" ] && cd ai-mcp-study && git pull origin main || git clone git@github.com:upJiang/ai-mcp-study.git && cd ai-mcp-study
cd mcp-list
chmod +x deployment/generate-compose.sh && ./deployment/generate-compose.sh
chmod +x deployment/generate-nginx.sh && ./deployment/generate-nginx.sh
sudo cp deployment/nginx/mcp-services.conf /etc/nginx/conf.d/
sudo nginx -t && sudo systemctl reload nginx
echo "✅ 初始化完成！"
EOF
)"
```

## 📋 常用命令

### 查看服务状态

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list
docker-compose ps
```

### 查看日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f [service-name]

# 最近 100 行
docker-compose logs --tail=100 -f
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart [service-name]
```

### 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止特定服务
docker-compose stop [service-name]
```

### 重新构建并启动

```bash
# 重建所有服务
docker-compose build --no-cache
docker-compose up -d

# 重建特定服务
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

### 查看容器资源使用

```bash
docker stats
```

### 进入容器内部

```bash
docker exec -it mcp-[service-name] bash
```

## 🔍 故障排查

### 检查 Nginx 状态

```bash
# 测试配置
sudo nginx -t

# 查看 Nginx 状态
sudo systemctl status nginx

# 重新加载配置
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 查看错误日志
sudo tail -f /var/log/nginx/mcp-services-error.log
```

### 检查 Docker 服务

```bash
# Docker 服务状态
sudo systemctl status docker

# 重启 Docker
sudo systemctl restart docker
```

### 查看容器详细信息

```bash
docker inspect mcp-[service-name]
```

### 查看容器内进程

```bash
docker top mcp-[service-name]
```

## 🔄 手动部署（紧急情况）

如果 GitHub Actions 出问题，可以手动部署：

```bash
cd /opt/mcp-services/ai-mcp-study
git pull origin main
cd mcp-list
./deployment/generate-compose.sh
./deployment/generate-nginx.sh
sudo cp deployment/nginx/mcp-services.conf /etc/nginx/conf.d/
sudo nginx -t && sudo systemctl reload nginx
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

或使用一键脚本：

```bash
cd /opt/mcp-services/ai-mcp-study
./deployment/deploy.sh
```

## 🧹 清理命令

### 清理未使用的 Docker 资源

```bash
# 清理停止的容器
docker container prune -f

# 清理未使用的镜像
docker image prune -a -f

# 清理未使用的卷
docker volume prune -f

# 清理所有未使用的资源
docker system prune -a -f
```

### 删除所有 MCP 容器和镜像

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list
docker-compose down --rmi all -v
```

## 📊 监控命令

### 实时查看容器日志

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list

# 所有服务（彩色输出）
docker-compose logs -f --tail=50

# 查看特定时间段的日志
docker-compose logs --since 1h

# 只看错误日志
docker-compose logs -f | grep -i error
```

### 查看服务健康状态

```bash
# 检查所有容器
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 测试服务响应
curl -I https://junfeng530.xyz/mcp/[service-name]
```

## 🔐 安全检查

### 检查开放端口

```bash
sudo netstat -tulpn | grep LISTEN
```

### 检查防火墙规则

```bash
# CentOS 7
sudo firewall-cmd --list-all

# Ubuntu
sudo ufw status
```

### 查看 SSL 证书状态

```bash
sudo certbot certificates
```

### 续期 SSL 证书

```bash
sudo certbot renew --dry-run
sudo certbot renew
```

## 📁 重要文件路径

| 文件 | 路径 |
|------|------|
| 项目根目录 | `/opt/mcp-services/ai-mcp-study` |
| docker-compose.yml | `/opt/mcp-services/ai-mcp-study/mcp-list/docker-compose.yml` |
| Nginx 配置 | `/etc/nginx/conf.d/mcp-services.conf` |
| Nginx 日志 | `/var/log/nginx/mcp-services-*.log` |
| SSL 证书 | `/etc/letsencrypt/live/junfeng530.xyz/` |
| 包目录 | `/opt/mcp-services/ai-mcp-study/mcp-list/packages/` |

## 🌐 服务访问 URL

**格式**：`https://junfeng530.xyz/mcp/{service-name}`

查看当前部署的服务：

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list
docker-compose config --services
```

## 🆘 紧急情况

### 所有服务都无法访问

```bash
# 1. 检查 Nginx
sudo systemctl status nginx
sudo systemctl restart nginx

# 2. 检查 Docker 容器
cd /opt/mcp-services/ai-mcp-study/mcp-list
docker-compose ps

# 3. 查看日志
docker-compose logs -f
sudo tail -f /var/log/nginx/mcp-services-error.log

# 4. 重启所有服务
docker-compose restart
```

### 特定服务无法访问

```bash
cd /opt/mcp-services/ai-mcp-study/mcp-list

# 1. 查看服务日志
docker-compose logs -f [service-name]

# 2. 重启服务
docker-compose restart [service-name]

# 3. 如果还是失败，重新构建
docker-compose build --no-cache [service-name]
docker-compose up -d [service-name]
```

### 磁盘空间不足

```bash
# 检查磁盘使用
df -h

# 清理 Docker 资源
docker system prune -a -f

# 清理旧日志
sudo find /var/log -type f -name "*.log" -mtime +30 -delete
```

## 📞 获取帮助

- **GitHub Actions 日志**: GitHub 仓库 → Actions 标签
- **服务日志**: `docker-compose logs -f`
- **Nginx 日志**: `sudo tail -f /var/log/nginx/mcp-services-error.log`
- **系统日志**: `sudo journalctl -xe`

# Claude Stats MCP - Python版本

基于FastMCP (Python)的Claude Code使用统计MCP服务器。

## 功能特性

✨ **8个强大的工具函数**：
- 📊 查询今日/本月统计
- 👤 查询特定用户数据
- 🏆 查询Top用户排行
- 🔄 对比用户使用情况
- 📈 分析使用趋势
- ⚠️ 检测异常使用
- 📑 生成完整报告

🐳 **推荐使用Docker部署**（无需本地Python环境）
🌐 **支持HTTPS远程访问**

## 快速开始

### 前置要求

- Python >= 3.8（如果本地运行）
- Docker（推荐部署方式）

### 方式1: Docker部署（推荐）

**无需Python环境，一键启动！**

```bash
cd python-mcp-demo

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务将在 `http://localhost:8000/mcp` 启动。

### 方式2: 本地Python运行

#### 1. 安装依赖

```bash
cd python-mcp-demo

# 使用venv（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置

```bash
# 复制配置文件
cp ../ccReport/config/keys.json ./config/keys.json

# 或创建符号链接
ln -s ../ccReport/config/keys.json ./config/keys.json

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件
```

#### 3. 运行

```bash
# STDIO模式（用于Cursor本地）
python server.py

# HTTP模式（远程访问）
MCP_TRANSPORT=http MCP_PORT=8000 python server.py
```

## 在Cursor中使用

### 方式1: HTTP远程模式（推荐）

**前提**：使用Docker或服务器部署Python版本

在Cursor配置文件中添加：

**macOS/Linux**: `~/.config/cursor/config.json`  
**Windows**: `%APPDATA%\Cursor\config.json`

```json
{
  "mcpServers": {
    "claude-stats": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 方式2: 本地STDIO模式（需要Python环境）

```json
{
  "mcpServers": {
    "claude-stats-python": {
      "command": "python",
      "args": ["/path/to/python-mcp-demo/server.py"],
      "env": {
        "KEYS_CONFIG_PATH": "/path/to/ccReport/config/keys.json"
      }
    }
  }
}
```

### 方式3: 使用虚拟环境

```json
{
  "mcpServers": {
    "claude-stats-python": {
      "command": "/path/to/python-mcp-demo/venv/bin/python",
      "args": ["/path/to/python-mcp-demo/server.py"]
    }
  }
}
```

## 工具说明

### 1. query_today_stats

查询今日所有账号的使用统计。

**参数**：
- `force_refresh` (bool, 可选): 是否强制刷新缓存

### 2. query_monthly_stats

查询本月所有账号的使用统计。

**参数**：
- `force_refresh` (bool, 可选): 是否强制刷新缓存

### 3. query_user_stats

查询特定用户的统计数据。

**参数**：
- `user_name` (str, 必填): 用户名称或账号关键词
- `period` (str, 可选): 'daily' 或 'monthly'，默认'daily'

### 4. query_top_users

查询使用率最高的前N名用户。

**参数**：
- `limit` (int, 可选): 返回数量（1-20），默认5
- `period` (str, 可选): 'daily' 或 'monthly'，默认'daily'

### 5. compare_users

比较两个用户的使用情况。

**参数**：
- `user1_name` (str, 必填): 第一个用户名称
- `user2_name` (str, 必填): 第二个用户名称
- `period` (str, 可选): 'daily' 或 'monthly'，默认'daily'

### 6. analyze_usage_trend

分析使用趋势，对比今日和本月的平均使用情况。

**参数**：无

### 7. detect_anomalies

检测异常使用情况。

**参数**：
- `threshold` (float, 可选): 费用阈值，默认40.0
- `period` (str, 可选): 'daily' 或 'monthly'，默认'daily'

### 8. generate_report

生成完整的使用报告和优化建议。

**参数**：
- `period` (str, 可选): 'daily' 或 'monthly'，默认'daily'

## Docker部署详解

### 构建自定义镜像

```bash
# 构建镜像
docker build -t claude-stats-mcp:latest .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/../ccReport/config:/app/config:ro \
  --name claude-stats-mcp \
  claude-stats-mcp:latest
```

### Docker Compose配置

```yaml
version: '3.8'

services:
  claude-stats-mcp:
    build: .
    container_name: claude-stats-mcp
    ports:
      - "8000:8000"
    volumes:
      - ../ccReport/config:/app/config:ro
    environment:
      - MCP_TRANSPORT=http
      - MCP_PORT=8000
      - KEYS_CONFIG_PATH=/app/config/keys.json
    restart: unless-stopped
```

### 管理容器

```bash
# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新并重启
docker-compose up -d --build
```

## 服务器部署

### 使用Supervisor

1. **安装Supervisor**

```bash
sudo apt-get install supervisor
```

2. **创建配置文件** `/etc/supervisor/conf.d/claude-stats-mcp.conf`

```ini
[program:claude-stats-mcp]
command=/path/to/python-mcp-demo/venv/bin/python /path/to/python-mcp-demo/server.py
directory=/path/to/python-mcp-demo
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/claude-stats-mcp.err.log
stdout_logfile=/var/log/claude-stats-mcp.out.log
environment=MCP_TRANSPORT="http",MCP_PORT="8000",KEYS_CONFIG_PATH="/path/to/keys.json"
```

3. **启动服务**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start claude-stats-mcp
```

### 使用Systemd

1. **创建服务文件** `/etc/systemd/system/claude-stats-mcp.service`

```ini
[Unit]
Description=Claude Stats MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/python-mcp-demo
Environment="MCP_TRANSPORT=http"
Environment="MCP_PORT=8000"
Environment="KEYS_CONFIG_PATH=/path/to/keys.json"
ExecStart=/path/to/python-mcp-demo/venv/bin/python /path/to/python-mcp-demo/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **启动服务**

```bash
sudo systemctl daemon-reload
sudo systemctl enable claude-stats-mcp
sudo systemctl start claude-stats-mcp
sudo systemctl status claude-stats-mcp
```

### Nginx反向代理

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location /mcp {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 一键部署脚本

```bash
chmod +x deploy-python.sh
./deploy-python.sh
```

脚本将自动：
1. 检查Python版本
2. 创建虚拟环境
3. 安装依赖
4. 选择部署方式（Docker/Supervisor/Systemd）
5. 配置并启动服务

## 故障排查

### 问题1: 找不到配置文件

```
错误: 加载API Key配置失败: 配置文件不存在
```

**解决方案**：
- 确保配置文件存在
- 检查环境变量 `KEYS_CONFIG_PATH`
- 检查Docker卷挂载路径

### 问题2: 依赖安装失败

```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3: Docker容器无法启动

```bash
# 查看详细日志
docker-compose logs

# 检查端口占用
lsof -i :8000

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 问题4: Cursor无法连接

**检查列表**：
- 服务是否正常运行
- 端口是否正确
- 防火墙是否开放
- 配置文件格式是否正确

## 性能优化

### 缓存配置

服务器内置5分钟缓存，可通过修改 `server.py` 中的 `CACHE_TTL` 调整：

```python
CACHE_TTL = 5 * 60  # 秒数
```

### 并发处理

FastMCP使用异步处理，自动支持并发请求。

### 资源限制（Docker）

```yaml
services:
  claude-stats-mcp:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          memory: 256M
```

## 技术栈

- **FastMCP**: MCP服务器框架
- **Python 3.8+**: 编程语言
- **HTTPX**: 异步HTTP客户端
- **Pydantic**: 数据验证
- **python-dotenv**: 环境变量管理

## 项目结构

```
python-mcp-demo/
├── server.py                 # MCP服务器和工具函数
├── utils/
│   ├── __init__.py
│   ├── api_client.py         # API客户端
│   ├── data_analyzer.py      # 数据分析
│   └── config_loader.py      # 配置加载
├── config/                   # 配置文件目录
├── requirements.txt          # Python依赖
├── Dockerfile               # Docker镜像
├── docker-compose.yml        # Docker Compose配置
├── deploy-python.sh          # 部署脚本
├── supervisor.conf           # Supervisor配置
├── nginx-python.conf         # Nginx配置
└── README.md
```

## 对比Node.js版本

| 特性 | Python版本 | Node.js版本 |
|-----|-----------|-----------|
| **本地使用** | ⚠️ 需Python环境 | ✅ 通过npm/npx |
| **远程部署** | ✅ Docker推荐 | ✅ PM2推荐 |
| **代码简洁度** | ✅ 更简洁 | ✅ 类型安全 |
| **性能** | ✅ 优秀 | ✅ 优秀 |
| **推荐场景** | 服务器部署 | 本地开发 |

## 相关链接

- [FastMCP Python文档](https://github.com/jlowin/fastmcp)
- [MCP官方文档](https://modelcontextprotocol.io)
- [Docker文档](https://docs.docker.com)

## License

MIT

---

**开发愉快！** 🐍

如有问题，欢迎提Issue或查阅主文档。


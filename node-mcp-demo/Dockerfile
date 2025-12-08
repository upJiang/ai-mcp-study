FROM node:18-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖（生产环境）
RUN npm ci --only=production

# 复制编译后的代码
COPY dist ./dist

# 创建config目录（用于挂载）
RUN mkdir -p /app/config

# 环境变量
ENV NODE_ENV=production
ENV MCP_TRANSPORT=httpStream
ENV MCP_PORT=8000
ENV KEYS_CONFIG_PATH=/app/config/keys.json

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# 启动命令
CMD ["node", "dist/index.js"]


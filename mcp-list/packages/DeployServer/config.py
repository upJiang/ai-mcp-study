"""
配置文件 - MCP Deploy Server
包含 API 地址、Token 等配置信息
"""

# 项目列表 API
PROJECT_LIST_API = "https://oa-api.3d66.com/api/v1/release/project"

# 发版 API
DEPLOY_API = "http://wh.3dliuliuwang.com/manual"

# 固定 Token
TOKEN = "d0528a75671f550abacfcf3027a2fa090"

# 请求超时时间（秒）
TIMEOUT = 300  # 5分钟

# API 请求重试次数
MAX_RETRIES = 3

# 重试延迟（秒）
RETRY_DELAY = 2

module.exports = {
  apps: [{
    name: 'claude-stats-mcp',
    script: './dist/index.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env_production: {
      NODE_ENV: 'production',
      MCP_TRANSPORT: 'httpStream',
      MCP_PORT: 8000,
      KEYS_CONFIG_PATH: './config/keys.json'
    },
    env_development: {
      NODE_ENV: 'development',
      MCP_TRANSPORT: 'stdio'
    }
  }]
};


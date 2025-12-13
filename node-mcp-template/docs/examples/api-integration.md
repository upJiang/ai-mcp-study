# 示例：API 集成 MCP 工具

本示例展示如何创建一个集成外部 API 的 MCP 工具。

## 场景说明

**需求**：创建一个 MCP 工具，集成高德地图 API 提供位置服务。

**功能**：
- 地址转经纬度（地理编码）
- 经纬度转地址（逆地理编码）
- 路径规划
- 周边搜索
- 支持结果缓存

---

## 第 1 步：告诉 AI 你的需求

在 Cursor/Claude Code 中输入：

```
创建一个 MCP 项目，集成高德地图 API：

项目信息：
- 项目名：@mycompany/amap-mcp
- 功能：提供地图位置服务
- 作者：李四 <lisi@company.com>
- 命令名：amap

需要的工具：
1. geocode - 地址转经纬度
   - 输入：地址文本
   - 返回：经纬度坐标

2. regeocode - 经纬度转地址
   - 输入：经纬度
   - 返回：地址信息

3. route_planning - 路径规划
   - 输入：起点、终点
   - 返回：路线方案、距离、时间

4. search_nearby - 周边搜索
   - 输入：位置、关键词、半径
   - 返回：周边 POI 列表

API Key 存放在环境变量中。
所有请求支持缓存（默认 5 分钟）。
```

---

## 第 2 步：AI 生成的项目结构

```
amap-mcp/
├── src/
│   ├── index.ts
│   ├── tools/
│   │   ├── geocode.ts
│   │   ├── regeocode.ts
│   │   ├── routePlanning.ts
│   │   └── searchNearby.ts
│   └── utils/
│       ├── config.ts
│       ├── cache.ts
│       └── amapClient.ts  # 高德 API 客户端
├── .env.example
├── package.json
├── tsconfig.json
├── .gitignore
└── README.md
```

---

## 第 3 步：生成的代码示例

### .env.example

```bash
# 高德地图 API Key
AMAP_API_KEY=your_api_key_here

# 缓存时长（毫秒），默认 5 分钟
CACHE_DURATION=300000
```

### package.json

```json
{
  "name": "@mycompany/amap-mcp",
  "version": "1.0.0",
  "description": "MCP tool for Amap (Gaode Map) API integration",
  "type": "module",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "bin": {
    "amap": "./dist/index.js"
  },
  "files": ["dist"],
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["mcp", "fastmcp", "amap", "gaode", "map", "location"],
  "author": "李四 <lisi@company.com>",
  "license": "MIT",
  "dependencies": {
    "dotenv": "^17.2.3",
    "fastmcp": "^3.25.3",
    "zod": "^4.1.13"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.3"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### src/utils/amapClient.ts

```typescript
/**
 * 高德地图 API 客户端
 */

const AMAP_BASE_URL = 'https://restapi.amap.com/v3';

interface AmapResponse {
  status: string;
  info: string;
  infocode: string;
  [key: string]: any;
}

export class AmapClient {
  private apiKey: string;

  constructor(apiKey: string) {
    if (!apiKey) {
      throw new Error('AMAP_API_KEY 未配置');
    }
    this.apiKey = apiKey;
  }

  /**
   * 发送 GET 请求到高德 API
   */
  async get(endpoint: string, params: Record<string, any> = {}): Promise<AmapResponse> {
    const url = new URL(`${AMAP_BASE_URL}${endpoint}`);
    url.searchParams.set('key', this.apiKey);

    // 添加其他参数
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }

    try {
      const response = await fetch(url.toString());

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: AmapResponse = await response.json();

      // 检查高德 API 响应状态
      if (data.status !== '1') {
        throw new Error(`高德 API 错误: ${data.info || '未知错误'}`);
      }

      return data;
    } catch (error: any) {
      console.error('[ERROR] Amap API 请求失败:', error);
      throw error;
    }
  }
}
```

### src/tools/geocode.ts

```typescript
import { z } from 'zod';
import { AmapClient } from '../utils/amapClient.js';
import { SimpleCache } from '../utils/cache.js';

const cache = new SimpleCache<any>();
const client = new AmapClient(process.env.AMAP_API_KEY || '');

export const geocodeTool = {
  name: 'geocode',
  description: '将地址转换为经纬度坐标（地理编码）',

  parameters: z.object({
    address: z.string().describe('要查询的地址'),
    city: z.string().optional().describe('城市名称（可选，提高查询准确度）')
  }),

  execute: async (args: { address: string; city?: string }) => {
    const cacheKey = `geocode_${args.address}_${args.city || 'all'}`;

    try {
      // 尝试从缓存获取
      const cached = cache.get(cacheKey);
      if (cached) {
        return JSON.stringify({
          success: true,
          data: cached,
          fromCache: true
        }, null, 2);
      }

      // 调用高德 API
      const response = await client.get('/geocode/geo', {
        address: args.address,
        city: args.city
      });

      if (!response.geocodes || response.geocodes.length === 0) {
        throw new Error('未找到匹配的地址');
      }

      const result = {
        formatted_address: response.geocodes[0].formatted_address,
        location: response.geocodes[0].location,
        level: response.geocodes[0].level
      };

      // 存入缓存（5 分钟）
      const cacheDuration = parseInt(process.env.CACHE_DURATION || '300000');
      cache.set(cacheKey, result, cacheDuration);

      return JSON.stringify({
        success: true,
        data: result,
        fromCache: false
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] geocode:', error);

      return JSON.stringify({
        success: false,
        error: error.message,
        suggestion: '请检查地址格式和 API Key 配置'
      }, null, 2);
    }
  }
};
```

### src/tools/regeocode.ts

```typescript
import { z } from 'zod';
import { AmapClient } from '../utils/amapClient.js';
import { SimpleCache } from '../utils/cache.js';

const cache = new SimpleCache<any>();
const client = new AmapClient(process.env.AMAP_API_KEY || '');

export const regeocodeTool = {
  name: 'regeocode',
  description: '将经纬度坐标转换为地址信息（逆地理编码）',

  parameters: z.object({
    longitude: z.number().describe('经度'),
    latitude: z.number().describe('纬度')
  }),

  execute: async (args: { longitude: number; latitude: number }) => {
    const location = `${args.longitude},${args.latitude}`;
    const cacheKey = `regeocode_${location}`;

    try {
      // 尝试从缓存获取
      const cached = cache.get(cacheKey);
      if (cached) {
        return JSON.stringify({
          success: true,
          data: cached,
          fromCache: true
        }, null, 2);
      }

      // 调用高德 API
      const response = await client.get('/geocode/regeo', {
        location: location
      });

      if (!response.regeocode) {
        throw new Error('逆地理编码失败');
      }

      const result = {
        formatted_address: response.regeocode.formatted_address,
        addressComponent: response.regeocode.addressComponent,
        pois: response.regeocode.pois?.slice(0, 5) // 返回前 5 个 POI
      };

      // 存入缓存
      const cacheDuration = parseInt(process.env.CACHE_DURATION || '300000');
      cache.set(cacheKey, result, cacheDuration);

      return JSON.stringify({
        success: true,
        data: result,
        fromCache: false
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] regeocode:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### src/tools/routePlanning.ts

```typescript
import { z } from 'zod';
import { AmapClient } from '../utils/amapClient.js';

const client = new AmapClient(process.env.AMAP_API_KEY || '');

export const routePlanningTool = {
  name: 'route_planning',
  description: '规划两点之间的路线，返回距离、时间和路线方案',

  parameters: z.object({
    origin: z.string().describe('起点坐标（经度,纬度）或地址'),
    destination: z.string().describe('终点坐标（经度,纬度）或地址'),
    strategy: z.number().optional().describe('路线策略：0-速度优先（默认），1-费用优先，2-距离优先，3-避免拥堵')
  }),

  execute: async (args: {
    origin: string;
    destination: string;
    strategy?: number;
  }) => {
    try {
      // 调用高德路径规划 API
      const response = await client.get('/direction/driving', {
        origin: args.origin,
        destination: args.destination,
        strategy: args.strategy || 0
      });

      if (!response.route || !response.route.paths || response.route.paths.length === 0) {
        throw new Error('未找到路线');
      }

      const path = response.route.paths[0];
      const result = {
        distance: `${(parseInt(path.distance) / 1000).toFixed(2)} 公里`,
        duration: `${Math.ceil(parseInt(path.duration) / 60)} 分钟`,
        traffic_lights: path.traffic_lights,
        tolls: path.tolls || '0',
        steps: path.steps.map((step: any) => ({
          instruction: step.instruction,
          road: step.road,
          distance: `${(parseInt(step.distance) / 1000).toFixed(2)} 公里`
        }))
      };

      return JSON.stringify({
        success: true,
        data: result
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] route_planning:', error);

      return JSON.stringify({
        success: false,
        error: error.message,
        suggestion: '请检查起点和终点坐标格式（经度,纬度）'
      }, null, 2);
    }
  }
};
```

### src/tools/searchNearby.ts

```typescript
import { z } from 'zod';
import { AmapClient } from '../utils/amapClient.js';

const client = new AmapClient(process.env.AMAP_API_KEY || '');

export const searchNearbyTool = {
  name: 'search_nearby',
  description: '搜索指定位置周边的 POI（兴趣点），如餐厅、酒店、加油站等',

  parameters: z.object({
    location: z.string().describe('中心点坐标（经度,纬度）'),
    keywords: z.string().describe('搜索关键词（如"餐厅"、"酒店"、"加油站"）'),
    radius: z.number().optional().describe('搜索半径（米），默认 1000'),
    limit: z.number().optional().describe('返回数量，默认 10')
  }),

  execute: async (args: {
    location: string;
    keywords: string;
    radius?: number;
    limit?: number;
  }) => {
    try {
      const response = await client.get('/place/around', {
        location: args.location,
        keywords: args.keywords,
        radius: args.radius || 1000,
        offset: args.limit || 10
      });

      if (!response.pois || response.pois.length === 0) {
        return JSON.stringify({
          success: true,
          data: [],
          count: 0,
          message: '未找到符合条件的 POI'
        }, null, 2);
      }

      const results = response.pois.map((poi: any) => ({
        name: poi.name,
        type: poi.type,
        address: poi.address,
        location: poi.location,
        distance: `${poi.distance} 米`,
        tel: poi.tel
      }));

      return JSON.stringify({
        success: true,
        data: results,
        count: results.length
      }, null, 2);
    } catch (error: any) {
      console.error('[ERROR] search_nearby:', error);

      return JSON.stringify({
        success: false,
        error: error.message
      }, null, 2);
    }
  }
};
```

### src/index.ts

```typescript
#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import * as dotenv from 'dotenv';
import { geocodeTool } from './tools/geocode.js';
import { regeocodeTool } from './tools/regeocode.js';
import { routePlanningTool } from './tools/routePlanning.js';
import { searchNearbyTool } from './tools/searchNearby.js';

dotenv.config();

// 检查 API Key
if (!process.env.AMAP_API_KEY) {
  console.error('[ERROR] 未配置 AMAP_API_KEY 环境变量');
  console.error('请创建 .env 文件并添加: AMAP_API_KEY=your_key');
  process.exit(1);
}

const server = new FastMCP({
  name: 'Amap MCP',
  version: '1.0.0',
});

// 注册工具
server.addTool(geocodeTool);
server.addTool(regeocodeTool);
server.addTool(routePlanningTool);
server.addTool(searchNearbyTool);

// 启动服务器
console.error('========================================');
console.error(`MCP Server: ${server.name}`);
console.error('========================================');

server.start({ transportType: 'stdio' });

process.on('SIGINT', () => {
  console.error('\n正在关闭服务器...');
  process.exit(0);
});
```

---

## 第 4 步：配置和测试

### 4.1 安装依赖

```bash
npm install
```

### 4.2 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填写真实 API Key
vi .env
```

获取高德 API Key：
1. 访问 https://console.amap.com/
2. 注册/登录账号
3. 创建应用
4. 获取 Web 服务 API Key

### 4.3 测试运行

```bash
npm run dev
```

---

## 第 5 步：在 Cursor 中使用

### 5.1 发布到 npm

```bash
./scripts/publish-npm.sh
```

### 5.2 配置 Cursor

```json
{
  "mcpServers": {
    "amap": {
      "command": "npx",
      "args": ["-y", "@mycompany/amap-mcp"]
    }
  }
}
```

### 5.3 使用示例

**示例 1：地址转坐标**

```
北京市朝阳区望京SOHO的坐标是多少？
```

AI 调用 `geocode` 工具：
```json
{
  "address": "北京市朝阳区望京SOHO",
  "city": "北京"
}
```

**示例 2：路线规划**

```
从天安门到故宫怎么走？
```

AI 先调用 `geocode` 获取坐标，再调用 `route_planning`。

**示例 3：周边搜索**

```
帮我找望京附近的咖啡店
```

AI 调用 `geocode` 和 `search_nearby`。

---

## 优化建议

### 1. 添加错误重试

```typescript
async function retryableFetch(url: string, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url);
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

### 2. 添加请求限流

```typescript
class RateLimiter {
  private requests: number[] = [];
  private limit: number;
  private window: number;

  constructor(limit: number, window: number) {
    this.limit = limit;
    this.window = window;
  }

  async acquire() {
    const now = Date.now();
    this.requests = this.requests.filter(time => now - time < this.window);

    if (this.requests.length >= this.limit) {
      const waitTime = this.window - (now - this.requests[0]);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      return this.acquire();
    }

    this.requests.push(now);
  }
}
```

---

## 常见问题

### Q1: API 调用失败？

**A**: 检查：
- API Key 是否正确
- API Key 是否有调用权限
- 网络连接是否正常
- 是否超过调用配额

### Q2: 缓存如何清除？

**A**: 重启服务器会自动清除内存缓存。如需持久化缓存，可以使用 Redis。

### Q3: 如何添加其他高德 API？

**A**: 告诉 AI：

```
添加天气查询工具，使用高德天气 API
```

---

## 总结

这个示例展示了：
- ✅ 如何集成外部 API
- ✅ 如何使用环境变量管理密钥
- ✅ 如何实现结果缓存
- ✅ 如何创建可复用的 API 客户端
- ✅ 如何处理 API 错误

**参考这个示例可以集成任何 REST API！**

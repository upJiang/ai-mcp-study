import fs from 'fs';
import path from 'path';
import { ApiKeyInfo } from './apiClient';

export interface Config {
  apiKeys: ApiKeyInfo[];
}

/**
 * 加载API Key配置
 */
export function loadApiKeys(configPath?: string): ApiKeyInfo[] {
  try {
    const finalPath = configPath || 
      process.env.KEYS_CONFIG_PATH || 
      path.join(process.cwd(), '../ccReport/config/keys.json');
    
    const absolutePath = path.resolve(finalPath);
    
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`配置文件不存在: ${absolutePath}`);
    }

    const data = fs.readFileSync(absolutePath, 'utf8');
    const config = JSON.parse(data);
    
    // 支持两种格式：api_keys 或 apiKeys
    const apiKeys = config.api_keys || config.apiKeys;
    
    if (!apiKeys || !Array.isArray(apiKeys)) {
      throw new Error('配置文件格式错误：缺少 apiKeys 或 api_keys 数组');
    }

    return apiKeys;
  } catch (error: any) {
    throw new Error(`加载API Key配置失败: ${error.message}`);
  }
}


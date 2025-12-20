/**
 * Base64 解码器
 * 支持灵活解码 Base64、JSON、对象等多种格式
 */

export class Base64Decoder {
  /**
   * 检查字符串是否是有效的 Base64
   */
  static isValidBase64(str: string): boolean {
    // Base64 只包含 A-Z, a-z, 0-9, +, /, = 字符
    const base64Regex = /^[A-Za-z0-9+/]*={0,2}$/;
    return base64Regex.test(str) && str.length % 4 === 0;
  }

  /**
   * 解码 Base64 字符串
   */
  static decode(encodedData: string): any {
    try {
      // 尝试 Base64 解码
      const decoded = Buffer.from(encodedData, 'base64').toString('utf-8');
      // 尝试解析为 JSON
      return JSON.parse(decoded);
    } catch {
      throw new Error('无法解码 Base64 数据或解析 JSON');
    }
  }

  /**
   * 灵活解码：支持 Base64、JSON、URL 编码等多种格式
   * @param data 编码的数据（可以是字符串或对象）
   */
  static decodeFlexible(data: string | object): any {
    // 如果已经是对象，直接返回
    if (typeof data === 'object' && data !== null) {
      return data;
    }

    if (typeof data !== 'string') {
      throw new Error('数据必须是字符串或对象');
    }

    let dataStr = data;

    // 1. 尝试 URL 解码
    try {
      const urlDecoded = decodeURIComponent(dataStr);
      if (urlDecoded !== dataStr) {
        dataStr = urlDecoded;
      }
    } catch {
      // URL 解码失败，继续使用原始字符串
    }

    // 2. 尝试直接解析为 JSON
    try {
      return JSON.parse(dataStr);
    } catch {
      // 不是 JSON，继续
    }

    // 3. 尝试 Base64 解码
    if (this.isValidBase64(dataStr)) {
      try {
        return this.decode(dataStr);
      } catch {
        // Base64 解码失败
      }
    }

    // 4. 如果是 Python dict 格式的字符串（单引号），尝试转换
    if (dataStr.includes("'")) {
      try {
        // 将单引号替换为双引号，尝试解析
        const jsonStr = dataStr.replace(/'/g, '"');
        return JSON.parse(jsonStr);
      } catch {
        // 转换失败
      }
    }

    throw new Error('无法解码数据：不是有效的 Base64、JSON 或对象格式');
  }

  /**
   * 编码为 Base64
   */
  static encode(data: any): string {
    const jsonStr = JSON.stringify(data);
    return Buffer.from(jsonStr, 'utf-8').toString('base64');
  }
}

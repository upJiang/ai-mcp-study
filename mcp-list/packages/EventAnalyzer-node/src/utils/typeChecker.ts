/**
 * 类型检查器
 * 用于推断值的类型并检查类型匹配
 */

export type TypeName = 'NUMBER' | 'STRING' | 'BOOL' | 'LIST' | 'OBJECT' | 'NULL' | 'UNKNOWN';

export class TypeChecker {
  /**
   * 推断值的类型
   */
  static inferType(value: any): TypeName {
    if (value === null || value === undefined) {
      return 'NULL';
    }

    if (typeof value === 'number') {
      return 'NUMBER';
    }

    if (typeof value === 'boolean') {
      return 'BOOL';
    }

    if (typeof value === 'string') {
      return 'STRING';
    }

    if (Array.isArray(value)) {
      return 'LIST';
    }

    if (typeof value === 'object') {
      return 'OBJECT';
    }

    return 'UNKNOWN';
  }

  /**
   * 检查类型是否匹配（支持隐式转换）
   * @param expected 期望的类型
   * @param actual 实际的类型
   * @param value 实际的值（用于隐式转换检查）
   */
  static typeMatches(expected: TypeName, actual: TypeName, value?: any): boolean {
    // 完全匹配
    if (expected === actual) {
      return true;
    }

    // NULL 类型特殊处理
    if (actual === 'NULL') {
      return false;
    }

    // 隐式转换规则
    if (expected === 'NUMBER' && actual === 'STRING' && value !== undefined) {
      // 字符串可以转换为数字
      const num = Number(value);
      return !isNaN(num);
    }

    if (expected === 'BOOL' && actual === 'STRING' && value !== undefined) {
      // "0"/"1" 或 "true"/"false" 可以转换为布尔值
      const lowerValue = String(value).toLowerCase();
      return ['0', '1', 'true', 'false'].includes(lowerValue);
    }

    if (expected === 'BOOL' && actual === 'NUMBER' && value !== undefined) {
      // 0/1 可以转换为布尔值
      return value === 0 || value === 1;
    }

    if (expected === 'STRING') {
      // 任何类型都可以转换为字符串
      return true;
    }

    return false;
  }

  /**
   * 获取类型的友好名称
   */
  static getTypeName(type: TypeName): string {
    const typeMap: Record<TypeName, string> = {
      NUMBER: '数字',
      STRING: '字符串',
      BOOL: '布尔值',
      LIST: '数组',
      OBJECT: '对象',
      NULL: '空值',
      UNKNOWN: '未知类型',
    };
    return typeMap[type] || type;
  }

  /**
   * 验证枚举值
   * @param value 要验证的值
   * @param enumValues 枚举值映射 { key: description }
   * @returns 是否是有效的枚举值
   */
  static validateEnum(value: any, enumValues: Record<string, string>): boolean {
    if (!enumValues || Object.keys(enumValues).length === 0) {
      return true;
    }

    const valueStr = String(value);
    return Object.keys(enumValues).includes(valueStr);
  }
}

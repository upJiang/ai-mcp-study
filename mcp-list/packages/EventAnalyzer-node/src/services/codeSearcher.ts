/**
 * 代码搜索器
 * 在项目代码中搜索字段的使用位置
 */

import * as fs from 'fs';
import * as path from 'path';

export interface SearchMatch {
  file: string;
  line: number;
  code: string;
  context_before: string[];
  context_after: string[];
}

export interface SearchResult {
  field_name: string;
  project_path: string;
  total_matches: number;
  matches: SearchMatch[];
  searched_files: number;
}

export class CodeSearcher {
  // 支持的文件扩展名
  private supportedExtensions = [
    '.ts',
    '.tsx',
    '.js',
    '.jsx',
    '.vue',
    '.json',
    '.py',
    '.java',
    '.kt',
    '.swift',
  ];

  // 忽略的目录
  private ignoredDirs = ['node_modules', '.git', 'dist', 'build', 'coverage', '.next', 'out'];

  /**
   * 在项目中搜索字段
   * @param fieldName 字段名称
   * @param projectPath 项目根目录
   * @param maxResults 最大结果数
   */
  findField(fieldName: string, projectPath: string, maxResults: number = 50): SearchResult {
    // 检查项目路径是否存在
    if (!fs.existsSync(projectPath)) {
      throw new Error(`项目路径不存在: ${projectPath}`);
    }

    const matches: SearchMatch[] = [];
    let searchedFiles = 0;

    // 递归搜索文件
    this.searchDirectory(projectPath, fieldName, matches, maxResults, (count) => {
      searchedFiles = count;
    });

    return {
      field_name: fieldName,
      project_path: projectPath,
      total_matches: matches.length,
      matches,
      searched_files: searchedFiles,
    };
  }

  /**
   * 递归搜索目录
   */
  private searchDirectory(
    dirPath: string,
    fieldName: string,
    matches: SearchMatch[],
    maxResults: number,
    onFileSearched: (count: number) => void
  ): void {
    if (matches.length >= maxResults) {
      return;
    }

    let fileCount = 0;

    try {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });

      for (const entry of entries) {
        if (matches.length >= maxResults) {
          break;
        }

        const fullPath = path.join(dirPath, entry.name);

        if (entry.isDirectory()) {
          // 跳过忽略的目录
          if (!this.ignoredDirs.includes(entry.name)) {
            this.searchDirectory(fullPath, fieldName, matches, maxResults, onFileSearched);
          }
        } else if (entry.isFile()) {
          // 检查文件扩展名
          const ext = path.extname(entry.name);
          if (this.supportedExtensions.includes(ext)) {
            fileCount++;
            onFileSearched(fileCount);
            this.searchFile(fullPath, fieldName, matches, maxResults);
          }
        }
      }
    } catch (error) {
      // 跳过无法访问的目录
    }
  }

  /**
   * 在单个文件中搜索
   */
  private searchFile(
    filePath: string,
    fieldName: string,
    matches: SearchMatch[],
    maxResults: number
  ): void {
    if (matches.length >= maxResults) {
      return;
    }

    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        if (matches.length >= maxResults) {
          break;
        }

        const line = lines[i];

        // 检查字段名是否出现在当前行
        if (this.containsField(line, fieldName)) {
          matches.push({
            file: filePath,
            line: i + 1,
            code: line.trim(),
            context_before: this.getContext(lines, i - 2, i),
            context_after: this.getContext(lines, i + 1, i + 3),
          });
        }
      }
    } catch (error) {
      // 跳过无法读取的文件
    }
  }

  /**
   * 检查行中是否包含字段名
   */
  private containsField(line: string, fieldName: string): boolean {
    // 使用正则表达式匹配完整的字段名（避免部分匹配）
    const patterns = [
      new RegExp(`["'\`]${fieldName}["'\`]`, 'i'), // 字符串形式："fieldName"
      new RegExp(`\\b${fieldName}\\b`, 'i'), // 作为标识符
      new RegExp(`${fieldName}:`, 'i'), // 对象属性
      new RegExp(`\\.${fieldName}\\b`, 'i'), // 属性访问
    ];

    return patterns.some((pattern) => pattern.test(line));
  }

  /**
   * 获取代码上下文
   */
  private getContext(lines: string[], start: number, end: number): string[] {
    const context: string[] = [];

    for (let i = Math.max(0, start); i < Math.min(lines.length, end); i++) {
      context.push(lines[i].trim());
    }

    return context;
  }
}

import * as path from "path";
import os from "os";
import { URL } from "url";

/**
 * 获取桌面路径
 */
export function getDesktopPath(): string {
  return path.join(os.homedir(), "Desktop");
}

/**
 * 从 URL 中提取域名（转换为安全的文件夹名）
 */
export function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname.replace(/[^a-zA-Z0-9]/g, "_");
  } catch {
    return "unknown";
  }
}

/**
 * 获取时间戳字符串 (格式: YYYYMMDD_HHMMSS)
 */
export function getTimestamp(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");
  return `${year}${month}${day}_${hours}${minutes}${seconds}`;
}

/**
 * 获取图片扩展名
 */
export function getImageExtension(url: string): string {
  const match = url.match(/\.(jpg|jpeg|png|webp|avif|gif)(\?.*)?$/i);
  if (match) {
    return match[1].toLowerCase() === "jpeg" ? "jpg" : match[1].toLowerCase();
  }
  return "jpg";
}

/**
 * 从 URL 中提取原始文件名（不含扩展名）
 * 会清理无效文件名字符
 */
export function extractFileName(url: string): string {
  try {
    const urlObj = new URL(url);
    // 获取路径部分的最后一段
    const pathname = urlObj.pathname;
    const lastSegment = pathname.split("/").pop() || "";

    // 移除扩展名部分（包括 .jpg, .png 等）
    const nameWithoutExt = lastSegment.replace(/\.(jpg|jpeg|png|webp|avif|gif)$/i, "");

    // 清理无效的文件名字符（Windows 文件系统不允许的字符）
    const cleanName = nameWithoutExt.replace(/[<>:"/\\|?*]/g, "_");

    // 如果文件名为空或只有特殊字符，返回空字符串（由调用方处理）
    if (!cleanName || cleanName.trim() === "") {
      return "";
    }

    // 限制文件名长度（避免过长的文件名）
    return cleanName.substring(0, 100);
  } catch {
    return "";
  }
}

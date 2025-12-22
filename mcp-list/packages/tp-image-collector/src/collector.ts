import * as fs from "fs";
import * as path from "path";
import { exec } from "child_process";
import { chromium, Browser, Page } from "playwright";
import { createRequire } from "module";
import { getDesktopPath, extractDomain, getTimestamp, getImageExtension, extractFileName } from "./utils.js";
import { downloadImage } from "./download.js";
import {
  getOverlayInitScript,
  getEnsureOverlayScript,
  getNoImagesFoundScript,
  getSuccessScript,
  getUpdateProgressScript,
  ImageDownloadItem,
} from "./overlay.js";

// 从 package.json 读取版本号
const require = createRequire(import.meta.url);
const packageJson = require("../package.json");
const VERSION: string = packageJson.version;

// 并发下载数量
const CONCURRENT_DOWNLOADS = 5;

export interface CollectResult {
  success: boolean;
  message: string;
}

/**
 * 图片信息（含尺寸）
 */
export interface ImageInfo {
  url: string;
  width: number;
  height: number;
}

/**
 * 从页面提取所有符合条件的图片 URL 及尺寸
 * 支持：img 标签、lazy loading 属性、CSS 背景图
 */
async function extractImageUrls(page: Page): Promise<ImageInfo[]> {
  const imageInfos = await page.evaluate(() => {
    const results: { url: string; width: number; height: number }[] = [];
    const seen = new Set<string>();

    // 图片格式正则
    const imagePattern = /\.(jpg|jpeg|png|webp|avif|gif)(\?.*)?$/i;
    // 从 URL 或 CSS 中提取图片地址的正则
    const urlExtractPattern = /url\(['"]?([^'"()]+)['"]?\)/gi;

    /**
     * 添加图片（去重）
     */
    const addImage = (url: string, width: number, height: number) => {
      if (!url || seen.has(url)) return;
      // 过滤 data: URL 和非图片格式
      if (url.startsWith('data:')) return;
      if (!imagePattern.test(url)) return;
      // 过滤小图
      if (width <= 50 || height <= 50) return;

      seen.add(url);
      results.push({ url, width, height });
    };

    // 1. 提取 <img> 标签图片
    const imgs = document.querySelectorAll("img");
    imgs.forEach((img) => {
      const width = img.naturalWidth || img.width;
      const height = img.naturalHeight || img.height;

      // 优先使用 src
      if (img.src) {
        addImage(img.src, width, height);
      }

      // 检查 lazy loading 属性
      const lazyAttrs = ['data-src', 'data-lazy-src', 'data-original', 'data-lazy', 'data-url', 'data-image'];
      for (const attr of lazyAttrs) {
        const lazySrc = img.getAttribute(attr);
        if (lazySrc && lazySrc.startsWith('http')) {
          addImage(lazySrc, width || 100, height || 100);
        }
      }

      // 检查 srcset
      const srcset = img.srcset || img.getAttribute('data-srcset');
      if (srcset) {
        const srcsetUrls = srcset.split(',').map(s => s.trim().split(' ')[0]);
        srcsetUrls.forEach(url => {
          if (url && url.startsWith('http')) {
            addImage(url, width || 100, height || 100);
          }
        });
      }
    });

    // 2. 提取 <picture> 中的 <source>
    const sources = document.querySelectorAll("picture source");
    sources.forEach((source) => {
      const srcset = source.getAttribute('srcset');
      if (srcset) {
        const srcsetUrls = srcset.split(',').map(s => s.trim().split(' ')[0]);
        srcsetUrls.forEach(url => {
          if (url && url.startsWith('http')) {
            addImage(url, 100, 100);
          }
        });
      }
    });

    // 3. 提取 CSS 背景图
    const allElements = document.querySelectorAll('*');
    allElements.forEach((el) => {
      const style = window.getComputedStyle(el);
      const bgImage = style.backgroundImage;

      if (bgImage && bgImage !== 'none') {
        let match;
        while ((match = urlExtractPattern.exec(bgImage)) !== null) {
          const url = match[1];
          if (url && url.startsWith('http')) {
            // 背景图默认使用元素尺寸
            const rect = el.getBoundingClientRect();
            addImage(url, rect.width || 100, rect.height || 100);
          }
        }
      }

      // 检查内联 style 中的背景图（可能有 lazy loading）
      const inlineStyle = el.getAttribute('style');
      if (inlineStyle) {
        let match;
        const inlinePattern = /url\(['"]?([^'"()]+)['"]?\)/gi;
        while ((match = inlinePattern.exec(inlineStyle)) !== null) {
          const url = match[1];
          if (url && url.startsWith('http')) {
            const rect = el.getBoundingClientRect();
            addImage(url, rect.width || 100, rect.height || 100);
          }
        }
      }

      // 检查 data-background 等属性
      const bgAttrs = ['data-background', 'data-bg', 'data-background-image'];
      for (const attr of bgAttrs) {
        const bgUrl = el.getAttribute(attr);
        if (bgUrl && bgUrl.startsWith('http')) {
          const rect = el.getBoundingClientRect();
          addImage(bgUrl, rect.width || 100, rect.height || 100);
        }
      }
    });

    return results;
  });

  return imageInfos;
}

/**
 * 生成唯一文件名（处理重名情况）
 * 如果文件名已存在，则添加 (2), (3) 等后缀
 */
function getUniqueFileName(
  baseName: string,
  ext: string,
  usedNames: Set<string>
): string {
  let fileName = `${baseName}.${ext}`;
  let counter = 2;

  while (usedNames.has(fileName.toLowerCase())) {
    fileName = `${baseName}(${counter}).${ext}`;
    counter++;
  }

  usedNames.add(fileName.toLowerCase());
  return fileName;
}

/**
 * 准备下载任务（生成文件名和路径）
 */
interface DownloadTask {
  imageUrl: string;
  fileName: string;
  filePath: string;
  ext: string;
  size: string;
}

function prepareDownloadTasks(
  imageInfos: ImageInfo[],
  savePath: string
): DownloadTask[] {
  const tasks: DownloadTask[] = [];
  const usedNamesByType: Record<string, Set<string>> = {};
  const defaultCounters: Record<string, number> = {};

  for (const { url: imageUrl, width, height } of imageInfos) {
    const ext = getImageExtension(imageUrl);
    const size = `${width}x${height}`;

    // 为每种类型创建子目录
    const typeDir = path.join(savePath, ext);
    if (!fs.existsSync(typeDir)) {
      fs.mkdirSync(typeDir, { recursive: true });
    }

    // 初始化该类型的已用名称集合
    if (!usedNamesByType[ext]) {
      usedNamesByType[ext] = new Set<string>();
    }

    // 从 URL 提取原始文件名
    let baseName = extractFileName(imageUrl);

    // 如果无法提取文件名，使用递增数字作为默认名称
    if (!baseName) {
      defaultCounters[ext] = (defaultCounters[ext] || 0) + 1;
      baseName = `image_${defaultCounters[ext]}`;
    }

    // 生成唯一文件名（处理重名）
    const fileName = getUniqueFileName(baseName, ext, usedNamesByType[ext]);
    const filePath = path.join(typeDir, fileName);

    tasks.push({ imageUrl, fileName, filePath, ext, size });
  }

  return tasks;
}

/**
 * 并发下载所有图片（支持进度回调）
 */
async function downloadAllImages(
  tasks: DownloadTask[],
  onProgress?: (current: number, total: number) => void
): Promise<{ successCount: number; failCount: number; errors: string[]; items: ImageDownloadItem[] }> {
  let successCount = 0;
  let failCount = 0;
  const errors: string[] = [];
  const items: ImageDownloadItem[] = new Array(tasks.length);
  let completedCount = 0;

  // 并发控制
  const downloadWithLimit = async (task: DownloadTask, index: number) => {
    const { imageUrl, fileName, filePath, ext, size } = task;

    const result = await downloadImage(imageUrl, filePath);

    if (result.success) {
      successCount++;
      items[index] = { fileName, size, url: imageUrl, success: true, ext };
    } else {
      failCount++;
      errors.push(`${fileName}: ${result.error}`);
      items[index] = { fileName, size, url: imageUrl, success: false, error: result.error, ext };
    }

    completedCount++;
    if (onProgress) {
      onProgress(completedCount, tasks.length);
    }
  };

  // 分批并发执行
  for (let i = 0; i < tasks.length; i += CONCURRENT_DOWNLOADS) {
    const batch = tasks.slice(i, i + CONCURRENT_DOWNLOADS);
    await Promise.all(batch.map((task, batchIndex) => downloadWithLimit(task, i + batchIndex)));
  }

  return { successCount, failCount, errors, items };
}

/**
 * 生成采集结果文本
 */
function formatResult(
  targetUrl: string,
  totalCount: number,
  successCount: number,
  failCount: number,
  savePath: string,
  errors: string[]
): string {
  let resultText = `图片采集完成！\n\n`;
  resultText += `网页地址：${targetUrl}\n`;
  resultText += `发现图片：${totalCount} 张\n`;
  resultText += `成功下载：${successCount} 张\n`;
  resultText += `下载失败：${failCount} 张\n`;
  resultText += `保存位置：${savePath}\n`;

  if (errors.length > 0 && errors.length <= 5) {
    resultText += `\n失败详情：\n${errors.join("\n")}`;
  }

  return resultText;
}

/**
 * 采集指定网页的图片
 */
export async function collectImages(targetUrl: string): Promise<CollectResult> {
  let browser: Browser | undefined;
  let page: Page | undefined;

  try {
    // 创建保存目录
    const domain = extractDomain(targetUrl);
    const timestamp = getTimestamp();
    const folderName = `图片采集_${domain}_${timestamp}`;
    const savePath = path.join(getDesktopPath(), folderName);

    if (!fs.existsSync(savePath)) {
      fs.mkdirSync(savePath, { recursive: true });
    }

    // 启动浏览器（显示窗口）
    browser = await chromium.launch({
      headless: false,
    });

    page = await browser.newPage();

    // 预注入脚本：页面加载后显示"采集中"弹窗
    await page.addInitScript(getOverlayInitScript(VERSION));

    // 访问目标网页
    await page.goto(targetUrl, {
      waitUntil: "networkidle",
      timeout: 30000,
    });

    // 等待页面稳定
    await page.waitForTimeout(1000);

    // 确保弹窗存在
    await page.evaluate(getEnsureOverlayScript(VERSION));

    // 等待 3 秒让图片加载完成
    await page.waitForTimeout(3000);

    // 提取所有图片 URL（支持 lazy loading 和 CSS 背景图）
    const uniqueUrls = await extractImageUrls(page);

    if (uniqueUrls.length === 0) {
      // 更新提示为"未找到图片"
      await page.evaluate(getNoImagesFoundScript());
      // 不自动关闭浏览器

      return {
        success: true,
        message: `未在页面上找到 jpg/png/webp/avif/gif 格式的图片（已过滤 50x50 以下的小图）。\n网页地址：${targetUrl}`,
      };
    }

    // 准备下载任务
    const tasks = prepareDownloadTasks(uniqueUrls, savePath);

    // 下载图片（并发 + 进度回调）
    const { successCount, failCount, errors, items } = await downloadAllImages(
      tasks,
      async (current, total) => {
        // 更新弹窗进度
        if (page) {
          try {
            await page.evaluate(getUpdateProgressScript(current, total));
          } catch {
            // 页面可能已关闭，忽略错误
          }
        }
      }
    );

    // 更新提示为"采集成功"并显示明细
    await page.evaluate(getSuccessScript(VERSION, { successCount, failCount, items, savePath }));

    // 不自动关闭浏览器，让用户查看明细后手动关闭

    // 自动打开保存的文件夹
    exec(`explorer "${savePath}"`);

    return {
      success: true,
      message: formatResult(
        targetUrl,
        uniqueUrls.length,
        successCount,
        failCount,
        savePath,
        errors
      ),
    };
  } catch (error) {
    // 出错时也不关闭浏览器，方便用户查看错误

    return {
      success: false,
      message: `采集失败：${error instanceof Error ? error.message : "未知错误"}`,
    };
  }
}

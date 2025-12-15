import * as fs from "fs";
import * as path from "path";
import { chromium, Browser, Page } from "playwright";
import { getDesktopPath, extractDomain, getTimestamp, getImageExtension } from "./utils.js";
import { downloadImage } from "./download.js";
import {
  getOverlayInitScript,
  getEnsureOverlayScript,
  getNoImagesFoundScript,
  getSuccessScript,
} from "./overlay.js";

export interface CollectResult {
  success: boolean;
  message: string;
}

/**
 * 从页面提取所有符合条件的图片 URL
 */
async function extractImageUrls(page: Page): Promise<string[]> {
  const imageUrls = await page.evaluate(() => {
    const imgs = document.querySelectorAll("img");
    return Array.from(imgs)
      .filter((img) => {
        // 检查图片尺寸，过滤 50x50 以下的图片
        const width = img.naturalWidth || img.width;
        const height = img.naturalHeight || img.height;
        return width > 50 && height > 50;
      })
      .map((img) => img.src)
      .filter((src) => src && /\.(jpg|jpeg|png)(\?.*)?$/i.test(src));
  });

  // 去重
  return [...new Set(imageUrls)];
}

/**
 * 下载所有图片到指定目录
 */
async function downloadAllImages(
  urls: string[],
  savePath: string
): Promise<{ successCount: number; failCount: number; errors: string[] }> {
  let successCount = 0;
  let failCount = 0;
  const errors: string[] = [];

  for (let i = 0; i < urls.length; i++) {
    const imageUrl = urls[i];
    const ext = getImageExtension(imageUrl);
    const fileName = `${i + 1}.${ext}`;
    const filePath = path.join(savePath, fileName);

    const result = await downloadImage(imageUrl, filePath);
    if (result.success) {
      successCount++;
    } else {
      failCount++;
      errors.push(`${fileName}: ${result.error}`);
    }
  }

  return { successCount, failCount, errors };
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

    const page = await browser.newPage();

    // 预注入脚本：页面加载后立即显示采集中弹窗
    await page.addInitScript(getOverlayInitScript());

    // 访问目标网页
    await page.goto(targetUrl, {
      waitUntil: "networkidle",
      timeout: 30000,
    });

    // 等待页面稳定
    await page.waitForTimeout(1000);

    // 确保弹窗已注入
    await page.evaluate(getEnsureOverlayScript());

    // 提取所有图片 URL
    const uniqueUrls = await extractImageUrls(page);

    if (uniqueUrls.length === 0) {
      // 更新提示为"未找到图片"
      await page.evaluate(getNoImagesFoundScript());
      await page.waitForTimeout(2000);
      await browser.close();

      return {
        success: true,
        message: `未在页面上找到 jpg/png 格式的图片（已过滤 50x50 以下的小图）。\n网页地址：${targetUrl}`,
      };
    }

    // 下载图片
    const { successCount, failCount, errors } = await downloadAllImages(
      uniqueUrls,
      savePath
    );

    // 更新提示为"采集成功"
    await page.evaluate(getSuccessScript(), successCount);

    // 等待 2 秒后关闭浏览器
    await page.waitForTimeout(2000);
    await browser.close();

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
    if (browser) {
      await browser.close();
    }

    return {
      success: false,
      message: `采集失败：${error instanceof Error ? error.message : "未知错误"}`,
    };
  }
}

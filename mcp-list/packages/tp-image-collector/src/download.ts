import * as fs from "fs";
import * as https from "https";
import * as http from "http";
import { URL } from "url";

export interface DownloadResult {
  success: boolean;
  error?: string;
}

/**
 * 下载单个图片到指定路径
 */
export function downloadImage(
  imageUrl: string,
  savePath: string
): Promise<DownloadResult> {
  return new Promise((resolve) => {
    try {
      const urlObj = new URL(imageUrl);
      const protocol = urlObj.protocol === "https:" ? https : http;

      const request = protocol.get(
        imageUrl,
        { timeout: 10000 },
        (response) => {
          // 处理重定向
          if (
            response.statusCode &&
            response.statusCode >= 300 &&
            response.statusCode < 400 &&
            response.headers.location
          ) {
            downloadImage(response.headers.location, savePath).then(resolve);
            return;
          }

          if (response.statusCode !== 200) {
            resolve({ success: false, error: `HTTP ${response.statusCode}` });
            return;
          }

          const fileStream = fs.createWriteStream(savePath);
          response.pipe(fileStream);

          fileStream.on("finish", () => {
            fileStream.close();
            resolve({ success: true });
          });

          fileStream.on("error", (err) => {
            fs.unlink(savePath, () => {});
            resolve({ success: false, error: err.message });
          });
        }
      );

      request.on("error", (err) => {
        resolve({ success: false, error: err.message });
      });

      request.on("timeout", () => {
        request.destroy();
        resolve({ success: false, error: "Timeout" });
      });
    } catch (err) {
      resolve({
        success: false,
        error: err instanceof Error ? err.message : "Unknown error",
      });
    }
  });
}

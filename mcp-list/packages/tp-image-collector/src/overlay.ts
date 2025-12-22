/**
 * 图片下载结果项
 */
export interface ImageDownloadItem {
  fileName: string;
  size: string;  // 图片尺寸：宽x高，如 "1920x1080"
  url: string;
  success: boolean;
  error?: string;
  ext: string;  // 图片类型：jpg/png/webp/avif/gif
}

/**
 * 获取注入弹窗的初始化脚本（用于 page.addInitScript）
 */
export function getOverlayInitScript(version: string): string {
  return `
    (() => {
      // 只在主页面执行，不在 iframe 中注入
      if (window !== window.top) return;

      const injectOverlay = () => {
        if (document.getElementById("mcp-image-collector-overlay")) return;

        const overlay = document.createElement("div");
        overlay.id = "mcp-image-collector-overlay";
        overlay.innerHTML = \`
          <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 999999;
            font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
          ">
            <div style="
              position: absolute;
              top: 16px;
              left: 16px;
              background: rgba(52, 152, 219, 0.9);
              color: white;
              padding: 6px 12px;
              border-radius: 4px;
              font-size: 12px;
              font-weight: 500;
            ">tp-image-collector MCP 提供服务 v${version}</div>
            <div style="
              background: white;
              padding: 40px 60px;
              border-radius: 12px;
              text-align: center;
              box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            ">
              <div id="mcp-loading-spinner" style="
                width: 50px;
                height: 50px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                margin: 0 auto 20px;
                animation: mcp-spin 1s linear infinite;
              "></div>
              <div id="mcp-loading-text" style="
                font-size: 18px;
                color: #333;
                font-weight: 500;
              ">正在采集中，请稍后~</div>
            </div>
          </div>
          <style>
            @keyframes mcp-spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          </style>
        \`;

        if (document.body) {
          document.body.appendChild(overlay);
        } else {
          document.documentElement.appendChild(overlay);
        }
      };

      // 尽早注入弹窗
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", injectOverlay);
      } else {
        injectOverlay();
      }

      // 确保弹窗存在
      setTimeout(injectOverlay, 100);
      setTimeout(injectOverlay, 500);
    })();
  `;
}

/**
 * 获取确保弹窗存在的脚本（用于 page.evaluate）
 */
export function getEnsureOverlayScript(version: string): string {
  return `
    (() => {
      // 只在主页面执行，不在 iframe 中注入
      if (window !== window.top) return;
      if (document.getElementById("mcp-image-collector-overlay")) return;

      const overlay = document.createElement("div");
      overlay.id = "mcp-image-collector-overlay";
      overlay.innerHTML = \`
        <div style="
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.7);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 999999;
          font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
        ">
          <div style="
            position: absolute;
            top: 16px;
            left: 16px;
            background: rgba(52, 152, 219, 0.9);
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
          ">tp-image-collector MCP 提供服务 v${version}</div>
          <div style="
            background: white;
            padding: 40px 60px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
          ">
            <div id="mcp-loading-spinner" style="
              width: 50px;
              height: 50px;
              border: 4px solid #f3f3f3;
              border-top: 4px solid #3498db;
              border-radius: 50%;
              margin: 0 auto 20px;
              animation: mcp-spin 1s linear infinite;
            "></div>
            <div id="mcp-loading-text" style="
              font-size: 18px;
              color: #333;
              font-weight: 500;
            ">正在采集中，请稍后~</div>
          </div>
        </div>
        <style>
          @keyframes mcp-spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
      \`;
      document.body.appendChild(overlay);
    })();
  `;
}

/**
 * 更新弹窗显示下载进度
 */
export function getUpdateProgressScript(current: number, total: number): string {
  return `
    (() => {
      if (window !== window.top) return;
      const text = document.getElementById("mcp-loading-text");
      if (text) {
        text.textContent = "正在下载 ${current}/${total}...";
      }
    })();
  `;
}

/**
 * 更新弹窗显示"未找到图片"
 */
export function getNoImagesFoundScript(): string {
  return `
    (() => {
      if (window !== window.top) return;
      const spinner = document.getElementById("mcp-loading-spinner");
      const text = document.getElementById("mcp-loading-text");
      if (spinner) spinner.style.display = "none";
      if (text) {
        text.textContent = "未找到符合条件的图片";
        text.style.color = "#e74c3c";
      }
    })();
  `;
}

/**
 * 更新弹窗显示"采集成功"并展示明细（支持按类型 tab 切换）
 */
export function getSuccessScript(
  version: string,
  data: { successCount: number; failCount: number; items: ImageDownloadItem[]; savePath: string }
): string {
  // 统计各类型数量
  const typeCounts: Record<string, number> = { all: data.items.length };
  const typeOrder = ['jpg', 'png', 'webp', 'avif', 'gif'];
  data.items.forEach(item => {
    typeCounts[item.ext] = (typeCounts[item.ext] || 0) + 1;
  });

  // 生成 tab 按钮 HTML
  const tabsHtml = ['all', ...typeOrder].filter(type => type === 'all' || typeCounts[type]).map(type => {
    const label = type === 'all' ? '全部' : type.toUpperCase();
    const count = typeCounts[type] || 0;
    if (type !== 'all' && count === 0) return '';
    return `
      <button
        data-tab="${type}"
        style="
          padding: 8px 16px;
          margin-right: 4px;
          border: none;
          border-radius: 6px 6px 0 0;
          background: ${type === 'all' ? '#3498db' : '#e9ecef'};
          color: ${type === 'all' ? '#fff' : '#495057'};
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s;
        "
      >${label} (${count})</button>
    `;
  }).join('');

  // 生成明细列表 HTML（带 data-ext 属性）
  const itemsHtml = data.items.map((item, index) => {
    const statusIcon = item.success
      ? '<span style="color: #27ae60;">✓</span>'
      : '<span style="color: #e74c3c;">✗</span>';
    const statusText = item.success ? '' : `<span style="color: #e74c3c; font-size: 12px;"> (${item.error || '失败'})</span>`;
    const shortUrl = item.url.length > 50 ? item.url.substring(0, 50) + '...' : item.url;
    // 转义 URL 中的特殊字符
    const escapedUrl = item.url.replace(/`/g, '\\`').replace(/\$/g, '\\$');
    const escapedFileName = item.fileName.replace(/`/g, '\\`').replace(/\$/g, '\\$');
    return `
      <div class="mcp-image-item" data-ext="${item.ext}" style="
        display: flex;
        align-items: center;
        padding: 0px 12px;
        background: ${index % 2 === 0 ? '#f8f9fa' : '#fff'};
        border-radius: 4px;
        margin-bottom: 4px;
        font-size: 13px;
        min-height: 62px;
      ">
        <span style="width: 40px; flex-shrink: 0; text-align: center;">${statusIcon}</span>
        <span style="width: 50px; flex-shrink: 0; color: #3498db; font-size: 11px; text-transform: uppercase; text-align: center;">${item.ext}</span>
        <span style="width: 46px; height: 46px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; margin: 0 8px;">
          <img src="${escapedUrl}" style="max-width: 46px; max-height: 46px; object-fit: contain; border-radius: 4px;" onerror="this.style.display='none'" />
        </span>
        <span style="width: 100px; flex-shrink: 0; color: #333; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: center;" title="${escapedFileName}">${escapedFileName}</span>
        <span style="width: 70px; flex-shrink: 0; color: #666; font-size: 12px; text-align: center;">${item.size}</span>
        <a href="${escapedUrl}" target="_blank" style="flex: 1; color: #3498db; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-decoration: none;" title="${escapedUrl}">${shortUrl}</a>
        ${statusText}
      </div>
    `;
  }).join('');

  // 转义保存路径
  const escapedSavePath = data.savePath.replace(/\\/g, '\\\\');

  return `
    (() => {
      if (window !== window.top) return;
      const overlay = document.getElementById("mcp-image-collector-overlay");
      if (!overlay) return;

      overlay.innerHTML = \`
        <div style="
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.7);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 999999;
          font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
        ">
          <div style="
            position: absolute;
            top: 16px;
            left: 16px;
            background: rgba(52, 152, 219, 0.9);
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
          ">tp-image-collector MCP 提供服务 v${version}</div>
          <div style="
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            max-width: 750px;
            width: 90%;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
          ">
            <div style="text-align: center; margin-bottom: 20px;">
              <h2 style="margin: 10px 0; color: #333; font-size: 20px;">采集完成 <span style="color: #27ae60;">✓</span></h2>
              <p style="color: #666; margin: 0; font-size: 14px;">
                成功 <span style="color: #27ae60; font-weight: bold;">${data.successCount}</span> 张，
                失败 <span style="color: #e74c3c; font-weight: bold;">${data.failCount}</span> 张
              </p>
              <p style="color: #999; margin: 8px 0 0; font-size: 12px;">保存位置：${escapedSavePath}（按类型分文件夹存放）</p>
            </div>

            <!-- Tab 切换区域 -->
            <div id="mcp-tabs" style="margin-bottom: 0; display: flex; border-bottom: 2px solid #e9ecef;">
              ${tabsHtml}
            </div>

            <div style="
              flex: 1;
              overflow-y: auto;
              border: 1px solid #eee;
              border-top: none;
              border-radius: 0 0 8px 8px;
              padding: 8px;
              max-height: 350px;
            ">
              <div style="
                display: flex;
                padding: 8px 12px;
                background: #e9ecef;
                border-radius: 4px;
                margin-bottom: 8px;
                font-size: 13px;
                font-weight: bold;
                color: #495057;
                align-items: center;
              ">
                <span style="width: 40px; flex-shrink: 0; text-align: center;">状态</span>
                <span style="width: 50px; flex-shrink: 0; text-align: center;">类型</span>
                <span style="width: 46px; flex-shrink: 0; text-align: center; margin: 0 8px;">缩略图</span>
                <span style="width: 100px; flex-shrink: 0; text-align: center;">文件名</span>
                <span style="width: 70px; flex-shrink: 0; text-align: center;">尺寸</span>
                <span style="flex: 1;">图片地址</span>
              </div>
              <div id="mcp-image-list">
                ${itemsHtml}
              </div>
            </div>
            <p style="text-align: center; color: #999; margin: 16px 0 0; font-size: 12px;">请手动关闭此窗口</p>
          </div>
        </div>
      \`;

      // 绑定 tab 切换事件
      const tabContainer = document.getElementById('mcp-tabs');
      if (tabContainer) {
        tabContainer.addEventListener('click', (e) => {
          const target = e.target;
          if (target.tagName !== 'BUTTON') return;

          const tabType = target.getAttribute('data-tab');
          if (!tabType) return;

          // 更新 tab 样式
          tabContainer.querySelectorAll('button').forEach(btn => {
            btn.style.background = '#e9ecef';
            btn.style.color = '#495057';
          });
          target.style.background = '#3498db';
          target.style.color = '#fff';

          // 过滤显示列表
          const items = document.querySelectorAll('.mcp-image-item');
          items.forEach(item => {
            const itemExt = item.getAttribute('data-ext');
            if (tabType === 'all' || itemExt === tabType) {
              item.style.display = 'flex';
            } else {
              item.style.display = 'none';
            }
          });
        });
      }
    })();
  `;
}

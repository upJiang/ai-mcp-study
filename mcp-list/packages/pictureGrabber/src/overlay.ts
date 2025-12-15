/**
 * 弹窗样式常量
 */
const OVERLAY_STYLES = {
  container: `
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
  `,
  dialog: `
    background: white;
    padding: 40px 60px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  `,
  spinner: `
    width: 50px;
    height: 50px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    margin: 0 auto 20px;
    animation: mcp-spin 1s linear infinite;
  `,
  text: `
    font-size: 18px;
    color: #333;
    font-weight: 500;
  `,
};

const SPINNER_ANIMATION = `
  @keyframes mcp-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

/**
 * 生成弹窗 HTML
 */
function generateOverlayHTML(): string {
  return `
    <div style="${OVERLAY_STYLES.container}">
      <div style="${OVERLAY_STYLES.dialog}">
        <div id="mcp-loading-spinner" style="${OVERLAY_STYLES.spinner}"></div>
        <div id="mcp-loading-text" style="${OVERLAY_STYLES.text}">正在采集中，请稍后~</div>
      </div>
    </div>
    <style>${SPINNER_ANIMATION}</style>
  `;
}

/**
 * 获取注入弹窗的初始化脚本（用于 page.addInitScript）
 */
export function getOverlayInitScript(): () => void {
  return () => {
    const injectOverlay = () => {
      if (document.getElementById("mcp-image-collector-overlay")) return;

      const overlay = document.createElement("div");
      overlay.id = "mcp-image-collector-overlay";
      overlay.innerHTML = `
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
      `;

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
  };
}

/**
 * 获取确保弹窗存在的脚本（用于 page.evaluate）
 */
export function getEnsureOverlayScript(): () => void {
  return () => {
    if (document.getElementById("mcp-image-collector-overlay")) return;

    const overlay = document.createElement("div");
    overlay.id = "mcp-image-collector-overlay";
    overlay.innerHTML = `
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
    `;
    document.body.appendChild(overlay);
  };
}

/**
 * 更新弹窗显示"未找到图片"
 */
export function getNoImagesFoundScript(): () => void {
  return () => {
    const spinner = document.getElementById("mcp-loading-spinner");
    const text = document.getElementById("mcp-loading-text");
    if (spinner) spinner.style.display = "none";
    if (text) {
      text.textContent = "未找到符合条件的图片";
      text.style.color = "#e74c3c";
    }
  };
}

/**
 * 更新弹窗显示"采集成功"
 */
export function getSuccessScript(): (count: number) => void {
  return (count: number) => {
    const spinner = document.getElementById("mcp-loading-spinner");
    const text = document.getElementById("mcp-loading-text");
    if (spinner) {
      spinner.style.display = "none";
    }
    if (text) {
      text.innerHTML = `<span style="color: #27ae60; font-size: 24px;">✓</span><br><span style="margin-top: 10px; display: inline-block;">采集成功！共 ${count} 张图片</span><br><span style="margin-top: 10px; display: inline-block;">请回到桌面查看吧~</span>`;
      text.style.color = "#27ae60";
    }
  };
}

/**
 * Background Service Worker
 * 监听网络请求，捕获 tpdi 埋点数据
 */

// 存储最近捕获的埋点数据（最多 100 条）
const MAX_TRACKING_DATA = 100;

// 导入解码工具函数
importScripts('utils/decoder.js');

// 监听网络请求
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    // 检查 URL 是否包含 tpdi
    if (details.url.includes('tpdi')) {
      try {
        // 解析 URL
        const url = new URL(details.url);
        const dataParam = url.searchParams.get('data');

        if (dataParam) {
          // 解码数据
          const decodedData = decodeTrackingData(dataParam);

          if (decodedData) {
            // 存储数据
            saveTrackingData({
              originalData: dataParam,
              decodedData: decodedData,
              url: details.url,
              timestamp: Date.now()
            });
          }
        }
      } catch (error) {
        console.error('处理请求失败:', error);
      }
    }
  },
  { urls: ["<all_urls>"] }
);

/**
 * 保存埋点数据到本地存储
 */
async function saveTrackingData(trackingRecord) {
  try {
    // 获取现有数据
    const result = await chrome.storage.local.get(['trackingData']);
    let trackingData = result.trackingData || [];

    // 添加新数据（最新的在前面）
    trackingData.unshift(trackingRecord);

    // 限制最大数量
    if (trackingData.length > MAX_TRACKING_DATA) {
      trackingData = trackingData.slice(0, MAX_TRACKING_DATA);
    }

    // 保存
    await chrome.storage.local.set({ trackingData });

    // 更新 Badge
    updateBadge(trackingData.length);

  } catch (error) {
    console.error('保存数据失败:', error);
  }
}

/**
 * 更新扩展图标上的徽章
 */
function updateBadge(count) {
  chrome.action.setBadgeText({
    text: count > 0 ? String(count) : ''
  });

  chrome.action.setBadgeBackgroundColor({
    color: '#4CAF50'
  });
}

// 监听来自 popup 的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'clearData') {
    // 清空数据
    chrome.storage.local.set({ trackingData: [] });
    updateBadge(0);
    sendResponse({ success: true });
  }

  return true;
});

console.log('EventAnalyzer Background Service Worker 已启动');

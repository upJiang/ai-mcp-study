/**
 * Base64 解码工具
 * 处理 URL 编码 + Base64 双重编码
 */

/**
 * 解码埋点数据
 * @param {string} encodedData - URL 编码 + Base64 编码的字符串
 * @returns {object|null} 解码后的 JSON 对象
 */
function decodeTrackingData(encodedData) {
  try {
    // Step 1: URL 解码
    const urlDecoded = decodeURIComponent(encodedData);

    // Step 2: Base64 解码
    const base64Decoded = atob(urlDecoded);

    // Step 3: JSON 解析
    const jsonData = JSON.parse(base64Decoded);

    return jsonData;
  } catch (error) {
    console.error('解码失败:', error);
    return null;
  }
}

/**
 * 格式化时间戳
 * @param {number} timestamp - 时间戳（毫秒）
 * @returns {string} 格式化后的时间字符串
 */
function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
}

/**
 * 提取事件关键信息
 * @param {object} trackingData - 埋点数据
 * @returns {object} 关键信息
 */
function extractKeyInfo(trackingData) {
  return {
    event: trackingData.event || 'Unknown',
    time: trackingData.time || Date.now(),
    timeStr: formatTimestamp(trackingData.time || Date.now()),
    type: trackingData.type || 'track',
    userId: trackingData.login_id || trackingData.distinct_id || 'Unknown',
    fieldCount: Object.keys(trackingData.properties || {}).length
  };
}

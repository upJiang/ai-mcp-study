/**
 * Popup JS
 * 弹窗界面逻辑
 */

let trackingData = [];
let filteredData = [];
let currentDetailRecord = null;

// DOM 元素
const trackingList = document.getElementById('trackingList');
const searchInput = document.getElementById('searchInput');
const clearBtn = document.getElementById('clearBtn');
const statsText = document.getElementById('statsText');
const detailModal = document.getElementById('detailModal');
const modalClose = document.getElementById('modalClose');
const modalTitle = document.getElementById('modalTitle');
const detailInfo = document.getElementById('detailInfo');
const detailData = document.getElementById('detailData');
const copyEventNameBtn = document.getElementById('copyEventNameBtn');
const copyJsonBtn = document.getElementById('copyJsonBtn');
const copyBase64Btn = document.getElementById('copyBase64Btn');
const copyMcpCmdBtn = document.getElementById('copyMcpCmdBtn');

// 加载数据
async function loadData() {
  try {
    const result = await chrome.storage.local.get(['trackingData']);
    trackingData = result.trackingData || [];
    filteredData = trackingData;
    renderList();
    updateStats();
  } catch (error) {
    console.error('加载数据失败:', error);
  }
}

// 渲染列表
function renderList() {
  if (filteredData.length === 0) {
    trackingList.innerHTML = `
      <div class="empty-state">
        <p>暂无捕获的埋点数据</p>
        <p class="hint">访问包含埋点的网页，数据将自动捕获</p>
      </div>
    `;
    return;
  }

  trackingList.innerHTML = filteredData.map((record, index) => {
    const keyInfo = extractKeyInfo(record.decodedData);
    return `
      <div class="tracking-item" data-index="${index}">
        <div class="tracking-item-header">
          <span class="event-name">${keyInfo.event}</span>
          <span class="event-time">${keyInfo.timeStr}</span>
        </div>
        <div class="tracking-item-body">
          类型: ${keyInfo.type} | 字段数: ${keyInfo.fieldCount} | 用户: ${keyInfo.userId}
        </div>
      </div>
    `;
  }).join('');

  // 绑定点击事件
  document.querySelectorAll('.tracking-item').forEach(item => {
    item.addEventListener('click', () => {
      const index = parseInt(item.dataset.index);
      showDetail(filteredData[index]);
    });
  });
}

// 更新统计
function updateStats() {
  statsText.textContent = `已捕获 ${trackingData.length} 条埋点`;
}

// 显示详情
function showDetail(record) {
  currentDetailRecord = record;
  const keyInfo = extractKeyInfo(record.decodedData);

  modalTitle.textContent = keyInfo.event;

  // 基本信息
  detailInfo.innerHTML = `
    <div class="detail-info-item">
      <span class="detail-label">事件名称:</span>
      <span class="detail-value">${keyInfo.event}</span>
    </div>
    <div class="detail-info-item">
      <span class="detail-label">事件类型:</span>
      <span class="detail-value">${keyInfo.type}</span>
    </div>
    <div class="detail-info-item">
      <span class="detail-label">时间戳:</span>
      <span class="detail-value">${keyInfo.time} (${keyInfo.timeStr})</span>
    </div>
    <div class="detail-info-item">
      <span class="detail-label">用户ID:</span>
      <span class="detail-value">${keyInfo.userId}</span>
    </div>
    <div class="detail-info-item">
      <span class="detail-label">字段数量:</span>
      <span class="detail-value">${keyInfo.fieldCount}</span>
    </div>
  `;

  // 完整数据
  detailData.textContent = JSON.stringify(record.decodedData, null, 2);

  // 显示模态框
  detailModal.classList.add('show');
}

// 关闭详情
function closeDetail() {
  detailModal.classList.remove('show');
  currentDetailRecord = null;
}

// 搜索
function handleSearch() {
  const keyword = searchInput.value.toLowerCase().trim();

  if (!keyword) {
    filteredData = trackingData;
  } else {
    filteredData = trackingData.filter(record => {
      const event = record.decodedData.event || '';
      return event.toLowerCase().includes(keyword);
    });
  }

  renderList();
}

// 清空数据
async function clearData() {
  if (confirm('确定要清空所有捕获的埋点数据吗？')) {
    await chrome.runtime.sendMessage({ action: 'clearData' });
    trackingData = [];
    filteredData = [];
    renderList();
    updateStats();
  }
}

// 复制事件名称
function copyEventName() {
  if (currentDetailRecord) {
    const eventName = currentDetailRecord.decodedData.event || 'Unknown';
    copyToClipboard(eventName);
    alert('事件名称已复制到剪贴板');
  }
}

// 复制 JSON
function copyJson() {
  if (currentDetailRecord) {
    const json = JSON.stringify(currentDetailRecord.decodedData, null, 2);
    copyToClipboard(json);
    alert('JSON 数据已复制到剪贴板');
  }
}

// 复制 Base64
function copyBase64() {
  if (currentDetailRecord) {
    copyToClipboard(currentDetailRecord.originalData);
    alert('Base64 数据已复制到剪贴板');
  }
}

// 复制 MCP 命令
function copyMcpCmd() {
  if (currentDetailRecord) {
    const cmd = `分析这个埋点数据：${currentDetailRecord.originalData}`;
    copyToClipboard(cmd);
    alert('MCP 命令已复制到剪贴板\\n现在可以在 Claude Code/Cursor 中粘贴并发送');
  }
}

// 复制到剪贴板
function copyToClipboard(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
}

// 事件监听
searchInput.addEventListener('input', handleSearch);
clearBtn.addEventListener('click', clearData);
modalClose.addEventListener('click', closeDetail);
copyEventNameBtn.addEventListener('click', copyEventName);
copyJsonBtn.addEventListener('click', copyJson);
copyBase64Btn.addEventListener('click', copyBase64);
copyMcpCmdBtn.addEventListener('click', copyMcpCmd);

// 点击模态框外部关闭
detailModal.addEventListener('click', (e) => {
  if (e.target === detailModal) {
    closeDetail();
  }
});

// 初始化
loadData();

// 监听存储变化
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.trackingData) {
    loadData();
  }
});

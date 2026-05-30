const currentData = [];
let currentUrl = '';
document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentUrl = tab.url || '';
  const isShopee = currentUrl.includes('shopee.');
  document.getElementById('extractBtn').disabled = !isShopee;
  document.getElementById('status').innerText = isShopee ? '已检测到 Shopee 页面' : '请在 Shopee 商品列表页使用';
});
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === 'DOM_UPDATED') {
    const btn = document.getElementById('extractBtn');
    if (btn) btn.textContent = '提取（页面已更新）';
  }
});
const sendBtn = document.getElementById('sendBtn');
const sendStatus = document.getElementById('sendStatus');
fetch('http://127.0.0.1:5719/api/ping').then(r => r.json()).then(() => { sendBtn.disabled = false; sendStatus.textContent = '选品助手已连接'; }).catch(() => { sendStatus.textContent = '选品助手未启动'; });
sendBtn.addEventListener('click', () => {
  if (!window._extractedProducts || !window._extractedProducts.length) { sendStatus.textContent = '请先点「提取」'; return; }
  sendBtn.disabled = true;
  sendStatus.textContent = '发送中...';
  fetch('http://127.0.0.1:5719/api/products', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ products: window._extractedProducts }) })
    .then(r => r.json()).then(d => { sendStatus.textContent = `✅ 已发送 ${d.count} 个商品`; }).catch(() => { sendStatus.textContent = '❌ 发送失败'; })
    .finally(() => { sendBtn.disabled = false; });
});
document.getElementById('extractBtn').addEventListener('click', async () => {
  const btn = document.getElementById('extractBtn');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.innerText = '正在提取...';
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  try {
    const response = await chrome.tabs.sendMessage(tab.id, { type: 'EXTRACT_PRODUCTS' });
    if (!response || !response.success) { status.innerText = '提取失败'; btn.disabled = false; return; }
    currentData = response.data;
    if (currentData.length === 0) {
      status.innerText = '⚠ 未提取到商品';
      document.getElementById('result').innerHTML = '<div class="empty">请确认在商品搜索结果页</div>';
      btn.disabled = false;
      return;
    }
    window._extractedProducts = currentData;
    status.innerText = `提取完成：${currentData.length} 个商品`;
    document.getElementById('actionsArea').style.display = 'block';
    document.getElementById('sendBtn').disabled = false;
  } catch (err) { status.innerText = '⚠ 无法连接页面'; }
  btn.disabled = false;
});
function escapeHtml(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }

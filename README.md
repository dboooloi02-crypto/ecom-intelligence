# 选品决策助手 (ecom-intelligence)

AI 驱动的跨境电商选品分析工具。输入关键词 → 自动分析市场数据 → 输出评分和推荐等级。

## 功能

- **Shopee 实时数据** — Chrome 扩展一键提取商品数据，发送到本地分析引擎
- **CSV 导入** — 导入已有商品数据，自动评分
- **规则引擎评分** — 多维权重计算（销量/价格/评分/竞争/利润），生成推荐/观察/放弃评级
- **本地服务** — 扩展数据通过 HTTP API 推送到本地 GUI

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## Chrome 扩展

安装 Chrome 扩展后打开 Shopee TW 搜索页：
1. `chrome://extensions` → 开发者模式 → 加载已解压的扩展
2. 选择 `shopee-extension` 文件夹
3. 搜索商品 → 点扩展图标 → 提取 → 发送到选品助手

## 技术栈

- Python 3.12 / PySide6 / Flask
- Chrome Extension MV3

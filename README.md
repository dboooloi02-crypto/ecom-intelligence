# 选品决策助手

AI 驱动的跨境电商选品工具。给关键词就能自动分析市场，评分出哪些值得卖。

## 适用人群

Shopee 卖家 / 想做跨境电商但不知道选什么品的新手 / 需要批量筛品的运营

## 功能

- **AI 搜索** — 输入关键词（如"蓝牙耳机"），AI 自动分析市场给出评分和推荐等级
- **CSV 导入** — 已有商品数据直接导入自动评分
- **Chrome 扩展抓取** — 打开 Shopee 搜索页，一键提取商品数据发送到工具
- **规则引擎评分** — 按销量、价格、评分、竞争、利润多维度算分，自动生成推荐/观察/不推荐评级
- **结果导出** — 分析完可以导出 CSV 留底

## 安装教程

### 1. 装 Python（如果已有 Python 3.10+ 可跳过）

去 python.org 下载 Python 3.12，安装时**勾上 "Add Python to PATH"**。

验证装好了：打开命令行（cmd）输入 `python --version`，显示版本号就行。

### 2. 下载项目

打开命令行，运行：

```bash
git clone https://github.com/dboooloi02-crypto/ecom-intelligence.git
cd ecom-intelligence
```

不会用 git 的话，去 GitHub 页面点绿色的 "Code" → "Download ZIP"，解压到文件夹，然后命令行 cd 进那个文件夹。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

需要装的：PySide6（界面）、flask（本地服务）、requests（网络请求）

### 4. 配置 API Key

本工具用智谱 AI（国产免费好申请）。打开 `app/ai/clients/zhipu_client.py`，找到：

```python
self.api_key = os.getenv("ZHIPUAI_API_KEY", "你的Key")
```

把 `你的Key` 换成你的智谱 API Key（去 open.bigmodel.cn 注册免费拿）。

### 5. 启动

```bash
python main.py
```

## 怎么用

### 方式一：AI 搜索（最适合新手）

1. 启动后左边输入框输入你要分析的产品关键词
2. 点"AI 搜索"，等十几秒出结果
3. 结果列表会显示：AI 评分、推荐等级（S/A/B/C）、分析理由
4. 选中某条点详情看完整分析

### 方式二：导入已有数据

1. 点"导入 CSV"
2. 选你的商品数据文件（需要含标题、价格、销量等字段）
3. 自动计算评分，生成推荐等级

### 方式三：Chrome 扩展抓取

需要先安装扩展：

1. 打开 Chrome，地址栏输 `chrome://extensions`
2. 右上角打开"开发者模式"
3. 点"加载已解压的扩展"，选择项目里的 `shopee-extension` 文件夹
4. 去 Shopee TW（shopee.tw）搜索任意商品
5. 点浏览器右上角扩展图标 → 点"提取数据" → 点"发送"
6. 数据会自动出现在工具里，开始评分

## 技术栈

- Python 3.12 / PySide6（桌面界面）
- 智谱 AI GLM-4-Flash（AI 分析）
- Flask（本地 HTTP 服务）
- Chrome Extension MV3（商品提取）
- 规则引擎评分（多维度加权计算）

## 注意

- 首次启动会创建 data/、logs/、exports/、reports/ 文件夹
- 日志存在 logs/ 目录下，遇到问题可以看
- 扩展只支持 Shopee（tw/my/ph/vn/th/sg），其他站后续支持
- 默认用智谱 AI，想换其他模型自己改 zhipu_client.py

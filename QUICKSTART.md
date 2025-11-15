# 快速启动指南

## 📦 安装

```bash
# 确保已安装 uv 和 pyenv
# 项目会自动使用 Python 3.11.13

# 安装依赖
uv sync
```

## 🚀 使用流程

### 1️⃣ 爬取产品数据

#### 方式 A: 交互式运行（推荐）

```bash
# 运行主爬虫程序
uv run python main.py
```

运行后可以选择：
- **单页模式** - 仅爬取第一页（快速测试）
- **多页模式** - 爬取所有页面（完整数据）
- **限制页数** - 爬取指定页数

这会：
- 爬取产品列表（单页或多页）
- 爬取产品详情
- 自动翻译为中文
- 自动处理图片上传

#### 方式 B: 非交互式多页爬取

```bash
# 爬取所有页面
uv run python scripts/scrape_multi_pages.py

# 只爬取前 3 页
uv run python scripts/scrape_multi_pages.py --max-pages 3

# 自定义分类URL
uv run python scripts/scrape_multi_pages.py --url "https://..."
```

输出文件：
- `data/output/products_basic.csv` - 基本信息（列表页）
- `data/output/products_complete.csv` - 英文完整数据
- `data/output/products_complete_zh.csv` - 中文完整数据
- `data/output/products_multi_page_*.csv` - 多页爬取结果

### 2️⃣ 批量处理图片（可选）

如果需要重新处理图片为 800x400 横条形格式：

```bash
# 非交互式批量处理
uv run python scripts/batch_process_images.py
```

这会处理所有CSV文件中的图片：
- 下载原始图片
- 调整为 800x400 白底居中
- 上传到图床
- 替换CSV中的URL

输出文件：
- `data/output/products_complete_800x400.csv`
- `data/output/products_complete_zh_800x400.csv`

### 3️⃣ 测试功能

```bash
# 测试图床上传
uv run python tests/test_upload.py

# 查看800x400效果演示
uv run python tests/demo_800x400.py

# 本地生成测试图片
uv run python tests/test_local_800x400.py
```

## ⚙️ 配置

### 图床配置
在 `scripts/batch_process_images.py` 中修改：
```python
API_URL = "http://81.68.170.234/api/index.php"
TOKEN = "your-token-here"
```

### 翻译配置
在 `utils/translate.py` 中配置 OpenAI API。

### 爬虫目标
在 `main.py` 中修改：
```python
list_url = "https://www.hollandandbarrett.com/shop/..."
```

## 📊 图片处理规格

- **尺寸**: 800x400 (横条形)
- **背景**: 纯白色 (#FFFFFF)
- **对齐**: 居中
- **格式**: PNG
- **质量**: 95%
- **特点**: 适合展示竖长的药品瓶子

## 🔍 目录说明

```
hb_scraper/
├── main.py              # 主程序
├── utils/               # 工具模块
├── scripts/             # 可执行脚本
├── tests/               # 测试文件
├── data/                # 数据文件
│   ├── input/          # 输入
│   └── output/         # 输出（CSV）
└── docs/               # 文档
```

详细说明见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🆘 常见问题

### 1. 图片下载失败
- 检查网络连接
- 可能需要代理

### 2. 图床上传失败
- 检查图床API和Token是否正确
- 查看图床是否在线：`curl http://81.68.170.234/api/index.php`

### 3. 翻译失败
- 检查 OpenAI API Key
- 查看 `utils/translate.py` 配置

### 4. 导入错误
- 确保在项目根目录运行
- 运行 `uv sync` 重新安装依赖

### 5. 多页爬取中断了
- 直接重新运行，会询问是否继续之前的进度
- 进度保存在 `data/output/scrape_progress.json`
- 删除该文件可重新开始

### 6. 无法自动翻页
- 检查网站分页结构是否变化
- 查看控制台输出的错误信息
- 尝试减少爬取页数测试

## 💡 提示

- 首次运行建议先测试少量产品
- 图片处理会比较耗时，请耐心等待
- 可以随时中断程序（Ctrl+C），已处理的数据会保存

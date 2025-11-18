# Holland & Barrett 产品爬虫 🛒

自动爬取 Holland & Barrett 产品信息，并处理图片上传到图床的完整工具链。

## ✨ 主要功能

- 🕷️ **智能爬虫** - 自动爬取产品列表和详情
- ⚡ **多线程并发** - 支持3-10个线程并行爬取（3-5倍加速）
- 📄 **多页爬取** - 支持分页爬取，自动翻页获取所有产品
- 💾 **断点续传** - 支持中断后继续爬取，不丢失进度
- 🔄 **自动重试** - 失败自动重试，提高成功率
- 📋 **失败记录** - 自动记录失败产品，支持后续重爬 ⭐ 新增
- 📝 **日志系统** - 完善的日志记录，方便调试和追踪
- 🌍 **自动翻译** - 集成 OpenAI API 翻译为中文
- 🖼️ **图片处理** - 自动处理图片为 800x400 横条形白底居中
- ☁️ **图床上传** - 自动上传到 EasyImage 图床
- 📊 **数据导出** - 导出为 CSV 格式（支持中文）
- 🎯 **稳定可靠** - 基于 JSON 提取，避免 DOM 变化

## 🚀 快速开始

```bash
# 交互式运行（支持并行模式）⭐ 推荐
uv run python main.py

# 重新爬取失败的产品 ⭐ 新增
uv run python scripts/retry_failed.py

# 自动测试找最佳线程数
uv run python scripts/find_optimal_threads.py

# 非交互式多页爬取（爬取所有页面）
uv run python scripts/scrape_multi_pages.py

# 限制爬取页数（如前3页）
uv run python scripts/scrape_multi_pages.py --max-pages 3

# 仅批量处理图片
uv run python scripts/batch_process_images.py

# 查看日志
python scripts/view_logs.py list
```

### ⚡ 并行爬取示例

```
选择模式 (1/2, 默认2): 2  # 选择并行模式
并发线程数 (建议3-5, 默认3): 5  # 5个线程并发
```

**性能对比**（100个产品）:
- 顺序模式: ~200秒
- 并行模式(3线程): ~70秒 ⚡ 快3倍
- 并行模式(5线程): ~45秒 ⚡ 快4.5倍

### 📋 失败重爬功能

爬取过程中失败的产品会自动记录到 `data/output/failed_products.json`

```bash
# 查看并重新爬取失败的产品
uv run python scripts/retry_failed.py
```

脚本会：
- 显示失败产品列表和失败原因
- 使用更保守的配置重新爬取
- 更新失败记录

📖 详细使用说明请查看 [QUICKSTART.md](QUICKSTART.md)
⚡ 并发使用说明请查看 [docs/QUICK_START_PARALLEL.md](docs/QUICK_START_PARALLEL.md)

## 📁 项目结构

```
hb_scraper/
├── main.py                      # 🎯 主程序入口
├── utils/                       # 🔧 工具模块
│   ├── image_processor.py       # 图片处理（下载、处理、上传）
│   ├── translate.py             # 翻译工具
│   └── extract_product.py       # 产品数据提取
├── scripts/                     # 📝 可执行脚本
│   ├── batch_process_images.py  # 批量图片处理（非交互）
│   └── process_csv_images.py    # 批量图片处理（交互式）
├── tests/                       # 🧪 测试和演示
├── data/                        # 💾 数据文件
│   ├── input/                   # 输入数据
│   └── output/                  # 输出 CSV
└── docs/                        # 📚 文档
```

完整结构说明见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 📊 输出文件

| 文件名 | 说明 |
|--------|------|
| `products_basic.csv` | 基本信息（列表页） |
| `products_complete.csv` | 完整英文数据 |
| `products_complete_zh.csv` | 完整中文数据 |
| `products_complete_800x400.csv` | 800x400 处理后英文版 |
| `products_complete_zh_800x400.csv` | 800x400 处理后中文版 |

## 🎨 图片处理特性

- **尺寸**: 800x400 横条形（适合药品瓶子展示）
- **背景**: 纯白色
- **对齐**: 居中
- **格式**: PNG（高质量）
- **优势**: 减少上下留白，产品更突出

## 🛠️ 技术栈

- **Python 3.11+** - 由 pyenv 管理
- **uv** - 现代包管理器
- **Selenium** - 浏览器自动化
- **Pillow** - 图片处理
- **httpx** - HTTP 客户端
- **pandas** - 数据处理
- **OpenAI API** - AI 翻译

## 📚 文档

### 快速入门
- [快速启动指南](QUICKSTART.md)
- [多WebDriver并发快速入门](docs/QUICK_START_PARALLEL.md) ⭐ 新增

### 功能详解
- [多WebDriver并发详解](docs/PARALLEL_SCRAPING.md) ⭐ 新增
- [WebDriver架构说明](docs/WEBDRIVER_ARCHITECTURE.md) ⭐ 新增
- [日志系统说明](docs/日志系统说明.md)
- [多页爬取说明](docs/多页爬取说明.md)
- [翻译工具说明](docs/翻译工具说明.md)

### 参考文档
- [项目结构说明](PROJECT_STRUCTURE.md)
- [详细使用文档](docs/使用说明.md)

## 🆘 支持

遇到问题？查看 [QUICKSTART.md](QUICKSTART.md) 的常见问题部分。

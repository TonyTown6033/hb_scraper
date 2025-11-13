# Holland & Barrett 产品爬虫

自动爬取 Holland & Barrett 产品信息的Python爬虫工具。

## 快速开始

```bash
# 运行完整爬虫
uv run python main.py

# 测试详情页提取
uv run python test_detail.py
```

## 功能特性

- ✅ 自动爬取产品列表页
- ✅ 提取产品详细信息（亮点、描述、用法、配料、营养成分）
- ✅ 自动处理Cookie弹窗
- ✅ 导出为CSV格式（支持中文）
- ✅ 基于JSON提取，稳定可靠

## 项目结构

```
hb_scraper/
├── main.py              # 主爬虫程序
├── extract_product.py   # 产品数据提取工具
├── test_detail.py       # 测试脚本
├── README.md            # 项目说明
├── pyproject.toml       # 项目配置
├── data/
│   ├── input/           # 输入数据（CSV模板等）
│   ├── output/          # 爬取结果输出
│   └── samples/         # HTML样本文件（测试用）
└── docs/
    └── 使用说明.md      # 详细使用文档
```

## 输出数据

- **data/output/products_basic.csv** - 基本信息（列表页）
- **data/output/products_complete.csv** - 完整信息（包含详情页）

## 技术栈

- Selenium - 浏览器自动化
- BeautifulSoup4 - HTML解析
- Python 3.11+ - 开发语言

## 详细文档

查看 [使用说明.md](./docs/使用说明.md) 了解更多信息。

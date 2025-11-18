# VPS 服务器快速开始指南

在 Ubuntu CLI 服务器上快速部署和运行爬虫。

## 🚀 5 分钟快速开始

### 1. 上传项目到服务器

```bash
# 在本地执行
scp -r hb_scraper user@your-server:/path/to/destination

# 或使用 git
ssh user@your-server
git clone <repo-url> hb_scraper
cd hb_scraper
```

### 2. 一键安装所有依赖

```bash
# 安装 Chrome 和 ChromeDriver
bash install_chromedriver.sh

# 安装 Python 依赖
uv sync
```

### 3. 测试配置

```bash
python test_headless_local.py --local
```

看到 `✓ 所有测试通过！` 就可以继续了。

### 4. 运行爬虫

```bash
# 方式 1: 交互式运行（需要输入）
uv run python main.py

# 方式 2: 非交互式运行（推荐）
uv run python scripts/scrape_multi_pages.py --max-pages 5

# 方式 3: 后台运行
screen -S scraper
uv run python scripts/scrape_multi_pages.py --max-pages 10
# 按 Ctrl+A 然后 D 分离会话
```

---

## ⚠️ 遇到问题？

### 问题：卡在 "初始化 ChromeDriver"

**原因**: 自动下载 ChromeDriver 失败或太慢

**解决**:
```bash
# 手动安装 ChromeDriver
bash install_chromedriver.sh

# 然后测试
python test_headless_local.py --local
```

### 问题：找不到 Chrome

**解决**:
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
```

### 问题：缺少系统库

**解决**:
```bash
sudo apt update
sudo apt install -y libnss3 libgconf-2-4 libfontconfig1 libxss1
```

### 需要完整诊断？

```bash
python diagnose_server.py
```

---

## 📋 完整配置步骤（首次部署）

### 步骤 1: 安装系统依赖

```bash
# 更新系统
sudo apt update

# 安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# 安装系统库
sudo apt install -y \
    libnss3 libgconf-2-4 libfontconfig1 libxss1 \
    libappindicator3-1 libasound2

# 验证
google-chrome --version
```

### 步骤 2: 配置 Python 环境（如果未配置）

```bash
# 安装 pyenv（如果没有）
curl https://pyenv.run | bash

# 添加到 ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# 安装 Python 3.11
pyenv install 3.11.13
pyenv global 3.11.13

# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# 验证
python --version
uv --version
```

### 步骤 3: 安装 ChromeDriver

```bash
cd hb_scraper
bash install_chromedriver.sh
```

### 步骤 4: 安装项目依赖

```bash
uv sync
```

### 步骤 5: 测试

```bash
python test_headless_local.py --local
```

### 步骤 6: 运行

```bash
# 简单运行
uv run python scripts/scrape_multi_pages.py --max-pages 5

# 后台运行（推荐）
screen -S scraper
uv run python main.py
# Ctrl+A, D 分离
# screen -r scraper 重新连接
```

---

## 🔧 常用命令

```bash
# 环境检查
python diagnose_server.py                    # 完整诊断
google-chrome --version                      # Chrome 版本
chromedriver --version                       # ChromeDriver 版本
python utils/webdriver_helper.py             # WebDriver 状态

# 测试
python test_headless_local.py --local        # 本地 ChromeDriver 测试
python test_headless.py                      # 自动下载测试

# 运行爬虫
uv run python main.py                        # 交互式（支持配置）
uv run python scripts/scrape_multi_pages.py  # 非交互式（快速）

# 后台运行
screen -S scraper                            # 创建会话
screen -r scraper                            # 重新连接
screen -ls                                   # 列出所有会话
# 在会话中按 Ctrl+A, D 分离

# 查看日志
tail -f logs/scraper.log                     # 实时日志
cat logs/scraper_error.log                   # 错误日志

# 查看结果
ls -lh data/output/                          # 输出文件
head -20 data/output/products_complete.csv   # 查看数据

# 系统监控
free -h                                      # 内存使用
df -h                                        # 磁盘空间
htop                                         # 进程监控（需要安装）
```

---

## 📊 运行模式对比

| 模式 | 命令 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| 交互式 | `uv run python main.py` | 可配置选项 | 需要输入 | 首次运行，测试 |
| 非交互式 | `uv run python scripts/scrape_multi_pages.py --max-pages 5` | 无需输入 | 配置固定 | 脚本化，批量 |
| 后台运行 | `screen -S scraper` | 不占用终端 | 需要管理会话 | 长时间运行 |
| 定时任务 | `crontab -e` | 自动执行 | 需要配置 | 定期爬取 |

---

## 🎯 推荐工作流

### 开发/测试阶段
```bash
# 1. 测试少量数据
uv run python scripts/scrape_multi_pages.py --max-pages 1

# 2. 检查输出
cat data/output/products_complete.csv
```

### 生产环境
```bash
# 1. 使用 screen 后台运行
screen -S scraper

# 2. 运行爬虫（推荐并行模式，3-5 线程）
uv run python main.py
# 选择: 模式 2 (多页)，并行模式，3 个线程

# 3. 分离会话
# Ctrl+A, D

# 4. 稍后重新连接查看进度
screen -r scraper
```

---

## 📁 输出文件

爬虫运行后，数据保存在以下位置：

```
data/output/
├── products_basic.csv           # 基本信息（列表页）
├── products_complete.csv        # 完整信息（含详情页）
└── failed_products.json         # 失败记录（可重试）
```

重试失败的产品：
```bash
uv run python scripts/retry_failed.py
```

---

## 🔄 更新代码

```bash
# 拉取最新代码
git pull

# 重新安装依赖（如果有变化）
uv sync

# 测试
python test_headless_local.py --local
```

---

## 📚 更多文档

- `TROUBLESHOOTING.md` - 故障排除完整指南
- `docs/SERVER_DEPLOYMENT.md` - 详细部署文档
- `docs/使用说明.md` - 使用说明
- `docs/PARALLEL_SCRAPING.md` - 并行爬取说明
- `README.md` - 项目说明

---

## 🆘 获取帮助

1. **运行诊断**: `python diagnose_server.py`
2. **查看故障排除**: `cat TROUBLESHOOTING.md`
3. **查看日志**: `tail -f logs/scraper.log`
4. **检查环境**: `python utils/webdriver_helper.py`

---

## ✅ 检查清单

在运行爬虫前，确保：

- [ ] Chrome 已安装: `google-chrome --version`
- [ ] ChromeDriver 已安装: `chromedriver --version`
- [ ] Python 3.11+: `python --version`
- [ ] 依赖已安装: `uv sync`
- [ ] 测试通过: `python test_headless_local.py --local`
- [ ] 磁盘空间充足: `df -h`
- [ ] 内存充足（建议 2GB+）: `free -h`

全部 ✓ 就可以开始爬取了！

# 服务器部署指南 (Ubuntu CLI)

本指南帮助你在没有 GUI 的 Ubuntu 服务器上运行 Holland & Barrett 爬虫程序。

## 环境要求

- Ubuntu 18.04+ (推荐 20.04 或 22.04)
- Python 3.11+
- 至少 2GB RAM
- 稳定的网络连接

## 1. 系统依赖安装

### 1.1 安装 Chrome/Chromium

```bash
# 更新包列表
sudo apt update

# 方法 1: 安装 Google Chrome (推荐)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# 方法 2: 或者安装 Chromium
# sudo apt install -y chromium-browser

# 验证安装
google-chrome --version
# 或
# chromium-browser --version
```

### 1.2 安装必要的系统库

```bash
# 安装 Chrome/Chromium 的依赖库
sudo apt install -y \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    xdg-utils
```

## 2. Python 环境配置

### 2.1 安装 pyenv (如果没有)

```bash
# 安装 pyenv 依赖
sudo apt install -y build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
    libffi-dev liblzma-dev

# 安装 pyenv
curl https://pyenv.run | bash

# 添加到 shell 配置 (~/.bashrc 或 ~/.zshrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# 重新加载配置
source ~/.bashrc
```

### 2.2 安装 Python 3.11

```bash
# 使用 pyenv 安装 Python 3.11
pyenv install 3.11.13
pyenv global 3.11.13

# 验证
python --version  # 应该显示 Python 3.11.13
```

### 2.3 安装 uv

```bash
# 安装 uv (Python 包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载配置
source ~/.bashrc

# 验证
uv --version
```

## 3. 项目部署

### 3.1 克隆或上传项目

```bash
# 方法 1: 使用 git 克隆
git clone <your-repo-url> hb_scraper
cd hb_scraper

# 方法 2: 或使用 scp 上传
# 在本地执行:
# scp -r /path/to/hb_scraper user@server:/path/to/destination
```

### 3.2 安装项目依赖

```bash
cd hb_scraper

# 使用 uv 安装依赖
uv sync

# 或使用 pip
# uv pip install -r requirements.txt
```

### 3.3 配置环境变量 (可选)

```bash
# 如果需要配置图床 API 或 OpenAI
cp .env.example .env  # 如果有示例文件
nano .env  # 编辑配置

# 或直接设置环境变量
export IMAGE_API_URL="http://81.68.170.234/api/index.php"
export IMAGE_API_TOKEN="your_token_here"
export OPENAI_API_KEY="your_openai_key_here"
```

## 4. 运行爬虫

### 4.1 基本用法

```bash
# 运行主程序 (交互式)
uv run python main.py

# 非交互式多页爬取
uv run python scripts/scrape_multi_pages.py --max-pages 5

# 指定分类URL
uv run python scripts/scrape_multi_pages.py \
    --url "https://www.hollandandbarrett.com/shop/vitamins-supplements/condition/hair-skin-nails/" \
    --max-pages 10
```

### 4.2 后台运行

```bash
# 使用 nohup 后台运行
nohup uv run python scripts/scrape_multi_pages.py --max-pages 10 > scraper.log 2>&1 &

# 查看进程
ps aux | grep python

# 查看日志
tail -f scraper.log

# 停止进程
kill <PID>
```

### 4.3 使用 screen 或 tmux (推荐)

```bash
# 安装 screen
sudo apt install -y screen

# 创建新会话
screen -S scraper

# 在 screen 中运行爬虫
uv run python main.py

# 分离会话: 按 Ctrl+A, 然后按 D
# 重新连接: screen -r scraper
# 列出所有会话: screen -ls
# 终止会话: 在会话中输入 exit
```

## 5. 测试配置

### 5.1 创建测试脚本

```bash
# 创建一个简单的测试脚本
cat > test_headless.py << 'EOF'
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("https://www.google.com")
    print(f"✓ 成功访问: {driver.title}")
    print("✓ Headless 模式配置正确!")
except Exception as e:
    print(f"✗ 错误: {e}")
finally:
    driver.quit()
EOF

# 运行测试
uv run python test_headless.py
```

### 5.2 验证输出

如果看到类似以下输出，说明配置成功：
```
✓ 成功访问: Google
✓ Headless 模式配置正确!
```

## 6. 常见问题与解决方案

### 6.1 Chrome 启动失败

**错误**: `selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start`

**解决方案**:
```bash
# 确保安装了所有依赖
sudo apt install -y libnss3 libgconf-2-4

# 检查 Chrome 是否可执行
which google-chrome
google-chrome --version
```

### 6.2 DevToolsActivePort 错误

**错误**: `WebDriverException: unknown error: DevToolsActivePort file doesn't exist`

**解决方案**: 确保使用了以下 Chrome 选项 (已在代码中配置):
```python
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
```

### 6.3 内存不足

**错误**: Chrome 崩溃或系统变慢

**解决方案**:
```bash
# 1. 减少并发线程数
# 在 main.py 中选择较少的线程 (1-2个)

# 2. 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 3. 使用更小的批处理大小
# 修改 batch_size 参数
```

### 6.4 ChromeDriver 版本不匹配

**错误**: `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XX`

**解决方案**:
```bash
# webdriver-manager 会自动下载匹配的 ChromeDriver
# 如果仍有问题，手动更新 Chrome
sudo apt update
sudo apt upgrade google-chrome-stable
```

### 6.5 网络连接问题

**错误**: 下载 ChromeDriver 失败或页面加载超时

**解决方案**:
```bash
# 1. 检查网络连接
ping google.com

# 2. 配置代理 (如果需要)
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"

# 3. 增加超时时间
# 在代码中已设置 30 秒超时
```

## 7. 性能优化建议

### 7.1 调整并发数

```bash
# 根据服务器配置选择合适的线程数:
# - 2GB RAM: 1-2 个线程
# - 4GB RAM: 3-5 个线程
# - 8GB+ RAM: 5-10 个线程
```

### 7.2 监控资源使用

```bash
# 实时监控
htop  # 或 top

# 查看内存使用
free -h

# 查看磁盘空间
df -h
```

### 7.3 日志管理

```bash
# 定期清理日志文件
find logs/ -name "*.log" -mtime +30 -delete

# 或使用 logrotate 自动管理
```

## 8. 数据备份

```bash
# 定期备份输出数据
tar -czf backup_$(date +%Y%m%d).tar.gz data/output/

# 使用 scp 下载到本地
scp user@server:/path/to/hb_scraper/backup_*.tar.gz ./
```

## 9. 自动化部署 (可选)

### 9.1 使用 cron 定时运行

```bash
# 编辑 crontab
crontab -e

# 添加定时任务 (每天凌晨 2 点运行)
0 2 * * * cd /path/to/hb_scraper && /path/to/uv run python scripts/scrape_multi_pages.py --max-pages 10 >> /path/to/cron.log 2>&1
```

### 9.2 使用 systemd 服务

```bash
# 创建服务文件
sudo nano /etc/systemd/system/hb-scraper.service

# 内容:
# [Unit]
# Description=HB Scraper Service
# After=network.target
#
# [Service]
# Type=simple
# User=your_user
# WorkingDirectory=/path/to/hb_scraper
# ExecStart=/path/to/uv run python scripts/scrape_multi_pages.py --max-pages 10
# Restart=on-failure
#
# [Install]
# WantedBy=multi-user.target

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start hb-scraper
sudo systemctl enable hb-scraper
```

## 10. 故障排除清单

- [ ] Chrome/Chromium 已安装并可执行
- [ ] Python 3.11+ 已安装
- [ ] 所有 Python 依赖已安装
- [ ] 系统库完整 (libnss3, libgconf-2-4 等)
- [ ] 有足够的磁盘空间和内存
- [ ] 网络连接正常
- [ ] headless 模式参数已配置
- [ ] 日志文件可写入

## 支持

如遇到其他问题，请查看日志文件:
- `logs/scraper.log` - 主日志
- `logs/scraper_error.log` - 错误日志
- `data/output/failed_products.json` - 失败的产品记录

# 故障排除指南

快速解决在 Ubuntu 服务器上运行爬虫时遇到的常见问题。

## 问题：ChromeDriver 初始化卡住 ⚠️

### 症状
```
[2/4] 初始化 ChromeDriver...
（长时间卡住，没有任何输出）
```

### 原因
webdriver-manager 尝试从网络下载 ChromeDriver，但下载速度慢或被阻塞。

### 快速解决方案

#### 方案 1: 一键安装脚本（最推荐）✅

```bash
# 在项目根目录运行
bash install_chromedriver.sh
```

这个脚本会：
1. 检查 Chrome 是否已安装（未安装则自动安装）
2. 获取 Chrome 版本号
3. 下载匹配的 ChromeDriver
4. 安装到 `/usr/local/bin/chromedriver`
5. 验证安装

#### 方案 2: 手动安装

```bash
# 1. 检查 Chrome 版本
google-chrome --version
# 输出示例: Google Chrome 120.0.6099.109

# 2. 获取主版本号（例如 120）
CHROME_MAJOR_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1)
echo $CHROME_MAJOR_VERSION

# 3. 查询对应的 ChromeDriver 版本
# Chrome 115+ 使用新 API
CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
echo $CHROMEDRIVER_VERSION

# Chrome 114 及以下使用旧 API
# CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")

# 4. 下载 ChromeDriver（Chrome 115+）
wget "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"

# Chrome 114 及以下
# wget "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"

# 5. 解压
unzip chromedriver-linux64.zip

# 6. 安装
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# 7. 验证
chromedriver --version
which chromedriver
```

#### 方案 3: 使用诊断工具

```bash
# 运行完整的环境诊断
python diagnose_server.py

# 查看 ChromeDriver 状态
python utils/webdriver_helper.py
```

### 验证修复

安装完成后，使用本地 ChromeDriver 进行测试：

```bash
# 使用本地 ChromeDriver 测试（不依赖网络下载）
python test_headless_local.py --local
```

预期输出：
```
✓ ChromeDriver: /usr/local/bin/chromedriver
✓ WebDriver 初始化成功
✓ 成功访问: https://www.google.com
✓ 所有测试通过！
```

---

## 问题：Chrome 未安装

### 症状
```
✗ 未找到 Chrome/Chromium
```

### 解决方案

```bash
# 方法 1: 安装 Google Chrome（推荐）
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# 方法 2: 安装 Chromium
sudo apt update
sudo apt install -y chromium-browser

# 验证
google-chrome --version
# 或
chromium-browser --version
```

---

## 问题：缺少系统依赖库

### 症状
```
error while loading shared libraries: libnss3.so
```

### 解决方案

```bash
# 安装所有必需的依赖库
sudo apt update
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

---

## 问题：DevToolsActivePort 错误

### 症状
```
WebDriverException: unknown error: DevToolsActivePort file doesn't exist
```

### 解决方案

这个问题已在代码中修复，确保使用了以下参数：

```python
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
```

如果仍有问题：

```bash
# 1. 检查 /dev/shm 挂载
df -h /dev/shm

# 2. 增加 /dev/shm 大小（如果太小）
sudo mount -o remount,size=2G /dev/shm

# 3. 或使用其他临时目录
# 在代码中添加:
# options.add_argument("--disable-dev-shm-usage")
```

---

## 问题：ChromeDriver 版本不匹配

### 症状
```
SessionNotCreatedException: Message: session not created:
This version of ChromeDriver only supports Chrome version XX
```

### 解决方案

```bash
# 1. 检查当前版本
google-chrome --version
chromedriver --version

# 2. 重新安装匹配的 ChromeDriver
bash install_chromedriver.sh

# 或更新 Chrome
sudo apt update
sudo apt upgrade google-chrome-stable
```

---

## 问题：权限被拒绝

### 症状
```
Permission denied: '/usr/local/bin/chromedriver'
```

### 解决方案

```bash
# 添加执行权限
sudo chmod +x /usr/local/bin/chromedriver

# 或更改所有者
sudo chown $USER:$USER /usr/local/bin/chromedriver
```

---

## 问题：内存不足

### 症状
- Chrome 进程崩溃
- 系统变慢
- Out of memory 错误

### 解决方案

```bash
# 1. 减少并发线程数
# 在运行爬虫时选择 1-2 个线程

# 2. 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 3. 监控内存使用
free -h
htop
```

---

## 问题：网络连接超时

### 症状
```
urllib.error.URLError: <urlopen error timed out>
```

### 解决方案

```bash
# 1. 测试网络连接
ping google.com
curl -I https://www.hollandandbarrett.com

# 2. 配置代理（如果需要）
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"
export NO_PROXY="localhost,127.0.0.1"

# 3. 增加超时时间（已在代码中设置为 30 秒）

# 4. 检查防火墙
sudo ufw status
sudo iptables -L
```

---

## 完整的故障排除流程

### 步骤 1: 运行诊断

```bash
python diagnose_server.py
```

这会检查：
- Chrome 安装状态
- 系统依赖库
- 网络连接
- Python 环境
- ChromeDriver 状态
- 系统资源

### 步骤 2: 安装 ChromeDriver

```bash
bash install_chromedriver.sh
```

### 步骤 3: 测试配置

```bash
# 使用本地 ChromeDriver 测试
python test_headless_local.py --local
```

### 步骤 4: 运行爬虫

```bash
# 如果测试通过，运行爬虫
uv run python main.py

# 或非交互式运行
uv run python scripts/scrape_multi_pages.py --max-pages 5
```

---

## 获取更多帮助

如果以上方法都无法解决问题：

1. **查看日志**
   ```bash
   # 查看爬虫日志
   cat logs/scraper.log
   cat logs/scraper_error.log

   # 查看系统日志
   sudo journalctl -xe
   ```

2. **检查完整环境**
   ```bash
   python diagnose_server.py > diagnosis.txt
   cat diagnosis.txt
   ```

3. **参考详细文档**
   - `docs/SERVER_DEPLOYMENT.md` - 完整部署指南
   - `docs/使用说明.md` - 使用说明

4. **测试基本功能**
   ```bash
   # 测试 Chrome
   google-chrome --headless --dump-dom https://www.google.com

   # 测试 ChromeDriver
   chromedriver --version

   # 测试 Selenium
   python -c "from selenium import webdriver; print('OK')"
   ```

---

## 快速参考命令

```bash
# 环境诊断
python diagnose_server.py

# 安装 ChromeDriver
bash install_chromedriver.sh

# 测试配置
python test_headless_local.py --local

# 运行爬虫
uv run python main.py

# 查看 Chrome 版本
google-chrome --version

# 查看 ChromeDriver 版本
chromedriver --version

# 检查 ChromeDriver 位置
which chromedriver

# 查看内存使用
free -h

# 查看磁盘空间
df -h

# 查看系统日志
tail -f logs/scraper.log
```

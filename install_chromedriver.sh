#!/bin/bash

# ChromeDriver 自动安装脚本
# 用于在 Ubuntu 服务器上快速安装 ChromeDriver

set -e  # 遇到错误立即退出

echo "======================================================================"
echo "ChromeDriver 自动安装脚本"
echo "======================================================================"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# 1. 检查 Chrome 是否已安装
echo -e "\n[1/5] 检查 Chrome 安装状态..."
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✓ 已安装: $CHROME_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROME_VERSION=$(chromium-browser --version)
    echo "✓ 已安装: $CHROME_VERSION"
elif command -v chromium &> /dev/null; then
    CHROME_VERSION=$(chromium --version)
    echo "✓ 已安装: $CHROME_VERSION"
else
    echo "✗ 未找到 Chrome/Chromium"
    echo -e "\n正在安装 Google Chrome..."

    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    $USE_SUDO apt install -y ./google-chrome-stable_current_amd64.deb
    rm google-chrome-stable_current_amd64.deb

    CHROME_VERSION=$(google-chrome --version)
    echo "✓ 安装完成: $CHROME_VERSION"
fi

# 2. 获取 Chrome 主版本号
echo -e "\n[2/5] 获取 Chrome 版本号..."
if command -v google-chrome &> /dev/null; then
    CHROME_MAJOR_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1)
elif command -v chromium-browser &> /dev/null; then
    CHROME_MAJOR_VERSION=$(chromium-browser --version | grep -oP '\d+' | head -1)
else
    CHROME_MAJOR_VERSION=$(chromium --version | grep -oP '\d+' | head -1)
fi

echo "✓ Chrome 主版本号: $CHROME_MAJOR_VERSION"

# 3. 获取对应的 ChromeDriver 版本
echo -e "\n[3/5] 查询匹配的 ChromeDriver 版本..."

# 尝试新的 API (Chrome 115+)
if [ "$CHROME_MAJOR_VERSION" -ge 115 ]; then
    echo "使用新版 ChromeDriver API..."
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_MAJOR_VERSION" || echo "")

    if [ -z "$CHROMEDRIVER_VERSION" ]; then
        echo "新版 API 失败，尝试旧版..."
        CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
        DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
    else
        DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip"
    fi
else
    # 使用旧的 API (Chrome 114 及以下)
    echo "使用旧版 ChromeDriver API..."
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
    DOWNLOAD_URL="https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
fi

echo "✓ ChromeDriver 版本: $CHROMEDRIVER_VERSION"
echo "  下载地址: $DOWNLOAD_URL"

# 4. 下载 ChromeDriver
echo -e "\n[4/5] 下载 ChromeDriver..."
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

if wget -q --show-progress "$DOWNLOAD_URL" -O chromedriver.zip; then
    echo "✓ 下载完成"
else
    echo "✗ 下载失败"
    echo "请手动下载: $DOWNLOAD_URL"
    rm -rf "$TMP_DIR"
    exit 1
fi

# 5. 解压并安装
echo -e "\n[5/5] 安装 ChromeDriver..."
unzip -q chromedriver.zip

# 新版本解压后的目录结构不同
if [ -d "chromedriver-linux64" ]; then
    CHROMEDRIVER_BIN="chromedriver-linux64/chromedriver"
else
    CHROMEDRIVER_BIN="chromedriver"
fi

if [ ! -f "$CHROMEDRIVER_BIN" ]; then
    echo "✗ 解压后未找到 chromedriver 文件"
    ls -la
    rm -rf "$TMP_DIR"
    exit 1
fi

# 安装到系统目录
$USE_SUDO mv "$CHROMEDRIVER_BIN" /usr/local/bin/chromedriver
$USE_SUDO chmod +x /usr/local/bin/chromedriver

# 清理临时文件
cd -
rm -rf "$TMP_DIR"

# 6. 验证安装
echo -e "\n======================================================================"
echo "验证安装"
echo "======================================================================"
if command -v chromedriver &> /dev/null; then
    INSTALLED_VERSION=$(chromedriver --version)
    echo "✓ ChromeDriver 安装成功!"
    echo "  版本: $INSTALLED_VERSION"
    echo "  路径: $(which chromedriver)"
else
    echo "✗ ChromeDriver 安装失败"
    exit 1
fi

echo -e "\n======================================================================"
echo "安装完成！"
echo "======================================================================"
echo ""
echo "下一步："
echo "  1. 测试配置:"
echo "     python test_headless_local.py --local"
echo ""
echo "  2. 运行爬虫:"
echo "     uv run python main.py"
echo ""
echo "======================================================================"

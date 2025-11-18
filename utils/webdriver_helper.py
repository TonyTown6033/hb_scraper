"""
WebDriver 辅助工具
提供多种方式创建 Chrome WebDriver，避免下载问题
"""

import os
import subprocess
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_chrome_version():
    """获取已安装的 Chrome 版本"""
    try:
        for cmd in ["google-chrome --version", "chromium-browser --version", "chromium --version"]:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return version
    except:
        pass
    return None


def find_chromedriver():
    """查找系统中已安装的 ChromeDriver"""
    possible_paths = [
        "/usr/local/bin/chromedriver",
        "/usr/bin/chromedriver",
        str(Path.home() / "bin" / "chromedriver"),
        str(Path.home() / ".local" / "bin" / "chromedriver"),
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

    # 尝试在 PATH 中查找
    try:
        result = subprocess.run(
            ["which", "chromedriver"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    return None


def create_chrome_driver(headless=True, use_local_driver=False, page_load_strategy='eager'):
    """
    创建 Chrome WebDriver 实例

    Args:
        headless: 是否使用无头模式
        use_local_driver: 是否使用本地 ChromeDriver（不使用 webdriver-manager）
        page_load_strategy: 页面加载策略 ('normal', 'eager', 'none')
                          - normal: 等待所有资源加载（默认，最慢）
                          - eager: 等待 DOM 加载完成（推荐，平衡）
                          - none: 不等待（最快，但可能不稳定）

    Returns:
        webdriver.Chrome: Chrome WebDriver 实例
    """
    # 配置 Chrome 选项
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if headless:
        options.add_argument("--headless=new")  # 新版无头模式

    # 服务器环境必需参数
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")

    # 性能优化 - 禁用不必要的功能
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")  # 只显示致命错误
    options.add_argument("--silent")

    # 禁用图片加载（可选，可以加速）
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)

    # User-Agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # 页面加载策略
    # eager: 不等待所有资源，只等 DOM 完成，更快且通常足够
    options.page_load_strategy = page_load_strategy

    # 创建 WebDriver
    if use_local_driver:
        # 使用本地 ChromeDriver
        driver_path = find_chromedriver()
        if not driver_path:
            raise FileNotFoundError(
                "未找到本地 ChromeDriver。请运行:\n"
                "  python diagnose_server.py\n"
                "查看手动安装方法"
            )
        print(f"使用本地 ChromeDriver: {driver_path}")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # 使用 webdriver-manager 自动管理
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("使用 webdriver-manager 下载 ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"webdriver-manager 失败: {e}")
            print("尝试使用本地 ChromeDriver...")
            # 回退到本地 ChromeDriver
            driver_path = find_chromedriver()
            if not driver_path:
                raise FileNotFoundError(
                    "未找到本地 ChromeDriver，且 webdriver-manager 下载失败。\n"
                    "请运行: python diagnose_server.py 查看解决方案"
                )
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)

    # 设置超时时间（增加到 60 秒以应对慢速网络）
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)

    return driver


def install_chromedriver_manual():
    """
    手动安装 ChromeDriver 的说明
    """
    instructions = """
手动安装 ChromeDriver:

1. 检查 Chrome 版本:
   google-chrome --version

2. 访问 ChromeDriver 下载页面:
   https://chromedriver.chromium.org/downloads
   或
   https://googlechromelabs.github.io/chrome-for-testing/

3. 下载对应版本的 ChromeDriver (Linux64)

4. 安装:
   unzip chromedriver_linux64.zip
   sudo mv chromedriver /usr/local/bin/
   sudo chmod +x /usr/local/bin/chromedriver

5. 验证:
   chromedriver --version

或使用自动脚本:

# 获取 Chrome 主版本号
CHROME_MAJOR_VERSION=$(google-chrome --version | grep -oP '\\d+' | head -1)

# 获取对应的 ChromeDriver 版本
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")

# 下载并安装
wget "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
chromedriver --version
"""
    return instructions


if __name__ == "__main__":
    print("WebDriver 辅助工具\n")

    # 显示 Chrome 版本
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"✓ Chrome 版本: {chrome_version}")
    else:
        print("✗ 未找到 Chrome/Chromium")

    # 查找 ChromeDriver
    driver_path = find_chromedriver()
    if driver_path:
        print(f"✓ ChromeDriver 路径: {driver_path}")

        # 检查版本
        try:
            result = subprocess.run(
                [driver_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"  版本: {result.stdout.strip()}")
        except:
            pass
    else:
        print("✗ 未找到本地 ChromeDriver")
        print("\n" + install_chromedriver_manual())

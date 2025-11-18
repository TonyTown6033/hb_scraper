#!/usr/bin/env python3
"""
Chrome 浏览器鲁棒性测试
增加超时时间和更多选项来处理网络问题
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_robust_driver(driver_path="/usr/local/bin/chromedriver"):
    """创建一个更鲁棒的 WebDriver"""

    print("\n配置 Chrome 选项...")
    options = webdriver.ChromeOptions()

    # 基本反检测
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Headless 模式
    options.add_argument("--headless=new")

    # 必需的服务器参数
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # 性能和稳定性优化
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-setuid-sandbox")

    # 禁用图片和样式表，加速加载
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
    }
    options.add_experimental_option("prefs", prefs)

    # 页面加载策略 - 使用 eager 模式，不等待所有资源加载完成
    options.page_load_strategy = 'eager'

    # User-Agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    print(f"✓ Chrome 选项配置完成")

    print(f"\n初始化 ChromeDriver: {driver_path}")
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # 设置更长的超时时间
    driver.set_page_load_timeout(60)  # 60秒页面加载超时
    driver.set_script_timeout(60)     # 60秒脚本执行超时

    print("✓ ChromeDriver 初始化成功")

    return driver


def test_simple_page():
    """测试访问简单页面"""
    print("=" * 60)
    print("Chrome 鲁棒性测试")
    print("=" * 60)

    driver = None

    try:
        # 创建 driver
        driver = create_robust_driver()

        # 测试1: 访问 data URI（不需要网络）
        print("\n[测试 1/3] 访问本地 data URI...")
        data_uri = "data:text/html,<h1>Hello World</h1>"
        driver.get(data_uri)
        print(f"✓ 成功访问本地页面")
        print(f"  页面标题: {driver.title}")
        time.sleep(1)

        # 测试2: 访问 example.com（轻量级网站）
        print("\n[测试 2/3] 访问 example.com...")
        try:
            start_time = time.time()
            driver.get("http://example.com")
            elapsed = time.time() - start_time
            print(f"✓ 成功访问 example.com（耗时 {elapsed:.1f}秒）")
            print(f"  页面标题: {driver.title}")
        except Exception as e:
            print(f"✗ 失败: {e}")
            print("\n⚠️  无法访问外网，可能原因:")
            print("  1. 服务器没有外网连接")
            print("  2. 防火墙阻止出站连接")
            print("  3. 需要配置代理")
            return False

        # 测试3: 访问目标网站
        print("\n[测试 3/3] 访问 Holland & Barrett...")
        try:
            start_time = time.time()
            driver.get("https://www.hollandandbarrett.com")
            elapsed = time.time() - start_time
            print(f"✓ 成功访问目标网站（耗时 {elapsed:.1f}秒）")
            print(f"  页面标题: {driver.title}")

            # 检查页面内容
            if "holland" in driver.title.lower():
                print("✓ 页面内容正常")
            else:
                print("⚠️  页面内容可能异常")

        except Exception as e:
            print(f"✗ 访问目标网站失败: {e}")
            print("\n可能原因:")
            print("  1. 目标网站访问慢")
            print("  2. 被反爬虫机制拦截")
            print("  3. 网络连接不稳定")
            return False

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n你的环境已经配置正确，可以运行爬虫了：")
        print("  uv run python scripts/scrape_multi_pages.py --max-pages 1")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if driver:
            try:
                driver.quit()
                print("\n✓ 浏览器已关闭")
            except:
                pass


def test_with_options():
    """测试不同的 Chrome 选项组合"""
    print("=" * 60)
    print("Chrome 选项测试")
    print("=" * 60)

    options_sets = [
        {
            "name": "最小选项",
            "args": ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage"]
        },
        {
            "name": "性能优化",
            "args": ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                    "--disable-gpu", "--disable-extensions", "--disable-images"]
        },
        {
            "name": "网络优化",
            "args": ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                    "--disable-gpu", "--disable-web-security", "--disable-features=IsolateOrigins,site-per-process"]
        }
    ]

    for option_set in options_sets:
        print(f"\n测试配置: {option_set['name']}")
        print("-" * 60)

        try:
            options = webdriver.ChromeOptions()
            for arg in option_set['args']:
                options.add_argument(arg)

            options.page_load_strategy = 'eager'

            service = Service(executable_path="/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)

            start_time = time.time()
            driver.get("http://example.com")
            elapsed = time.time() - start_time

            print(f"✓ 成功（耗时 {elapsed:.1f}秒）")
            driver.quit()

        except Exception as e:
            print(f"✗ 失败: {e}")
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chrome 鲁棒性测试")
    parser.add_argument("--test-options", action="store_true", help="测试不同选项组合")

    args = parser.parse_args()

    if args.test_options:
        test_with_options()
    else:
        success = test_simple_page()
        sys.exit(0 if success else 1)

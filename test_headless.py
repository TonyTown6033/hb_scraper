#!/usr/bin/env python3
"""
测试 Headless Chrome 配置是否正确
用于验证服务器环境配置
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import sys


def test_headless_chrome():
    """测试 headless Chrome 是否正常工作"""
    print("=" * 60)
    print("测试 Headless Chrome 配置")
    print("=" * 60)

    try:
        print("\n[1/4] 配置 Chrome 选项...")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        print("✓ Chrome 选项配置完成")

        print("\n[2/4] 初始化 ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✓ ChromeDriver 初始化成功")

        print("\n[3/4] 测试访问网页...")
        test_url = "https://www.google.com"
        driver.get(test_url)
        page_title = driver.title
        print(f"✓ 成功访问: {test_url}")
        print(f"  页面标题: {page_title}")

        print("\n[4/4] 测试目标网站...")
        target_url = "https://www.hollandandbarrett.com"
        driver.get(target_url)
        target_title = driver.title
        print(f"✓ 成功访问: {target_url}")
        print(f"  页面标题: {target_title}")

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！Headless 模式配置正确！")
        print("=" * 60)
        print("\n你现在可以在服务器上运行爬虫程序了:")
        print("  uv run python main.py")
        print("  uv run python scripts/scrape_multi_pages.py --max-pages 5")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        print("\n请检查:")
        print("  1. Chrome/Chromium 是否已安装")
        print("  2. 系统依赖是否完整 (libnss3, libgconf-2-4 等)")
        print("  3. 网络连接是否正常")
        print("\n详细错误信息:")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            driver.quit()
            print("\n✓ 浏览器已关闭")
        except:
            pass


if __name__ == "__main__":
    print("\n提示: 此脚本用于测试服务器环境是否正确配置\n")
    success = test_headless_chrome()
    sys.exit(0 if success else 1)

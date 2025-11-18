#!/usr/bin/env python3
"""
测试 Headless Chrome 配置（使用本地 ChromeDriver）
用于验证服务器环境配置（不依赖网络下载）
"""

import sys
import time
from utils.webdriver_helper import create_chrome_driver, get_chrome_version, find_chromedriver


def test_with_local_driver():
    """使用本地 ChromeDriver 测试"""
    print("=" * 60)
    print("测试 Headless Chrome 配置（本地 ChromeDriver）")
    print("=" * 60)

    # 检查环境
    print("\n[环境检查]")
    print("-" * 60)

    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"✓ Chrome: {chrome_version}")
    else:
        print("✗ 未找到 Chrome/Chromium")
        print("\n请先安装 Chrome:")
        print("  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        print("  sudo apt install -y ./google-chrome-stable_current_amd64.deb")
        return False

    driver_path = find_chromedriver()
    if driver_path:
        print(f"✓ ChromeDriver: {driver_path}")
    else:
        print("✗ 未找到本地 ChromeDriver")
        print("\n请手动安装 ChromeDriver:")
        print("  运行以下命令获取安装说明:")
        print("    python utils/webdriver_helper.py")
        return False

    try:
        print("\n[1/3] 初始化 WebDriver...")
        driver = create_chrome_driver(headless=True, use_local_driver=True)
        print("✓ WebDriver 初始化成功")

        print("\n[2/3] 测试访问网页...")
        test_url = "https://www.google.com"
        driver.get(test_url)
        page_title = driver.title
        print(f"✓ 成功访问: {test_url}")
        print(f"  页面标题: {page_title}")

        print("\n[3/3] 测试目标网站...")
        target_url = "https://www.hollandandbarrett.com"
        driver.get(target_url)
        target_title = driver.title
        print(f"✓ 成功访问: {target_url}")
        print(f"  页面标题: {target_title}")

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

        driver.quit()
        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_auto_download():
    """使用 webdriver-manager 自动下载测试"""
    print("=" * 60)
    print("测试 Headless Chrome 配置（自动下载 ChromeDriver）")
    print("=" * 60)

    try:
        print("\n[1/3] 初始化 WebDriver（可能需要下载，请稍候）...")
        print("提示: 如果卡住超过 30 秒，请按 Ctrl+C 中断，使用本地安装方式")

        start_time = time.time()
        driver = create_chrome_driver(headless=True, use_local_driver=False)
        elapsed = time.time() - start_time

        print(f"✓ WebDriver 初始化成功（耗时 {elapsed:.1f}秒）")

        print("\n[2/3] 测试访问网页...")
        test_url = "https://www.google.com"
        driver.get(test_url)
        page_title = driver.title
        print(f"✓ 成功访问: {test_url}")
        print(f"  页面标题: {page_title}")

        print("\n[3/3] 测试目标网站...")
        target_url = "https://www.hollandandbarrett.com"
        driver.get(target_url)
        target_title = driver.title
        print(f"✓ 成功访问: {target_url}")
        print(f"  页面标题: {target_title}")

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

        driver.quit()
        return True

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        print("\n下载 ChromeDriver 可能太慢，建议使用本地安装方式:")
        print("  python test_headless_local.py --local")
        return False

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        print("\n建议使用本地 ChromeDriver:")
        print("  python test_headless_local.py --local")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试 Headless Chrome 配置")
    parser.add_argument(
        "--local",
        action="store_true",
        help="使用本地 ChromeDriver（不自动下载）"
    )

    args = parser.parse_args()

    print("\n提示: 此脚本用于测试服务器环境是否正确配置\n")

    if args.local:
        success = test_with_local_driver()
    else:
        print("模式: 自动下载 ChromeDriver")
        print("提示: 如果下载太慢，可使用 --local 参数使用本地 ChromeDriver\n")
        success = test_with_auto_download()

    sys.exit(0 if success else 1)

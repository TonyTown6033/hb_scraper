"""非交互式多页爬虫脚本"""

import sys
import csv
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.multi_page_scraper import scrape_all_pages
import config


def handle_cookie_popup(driver, timeout=None):
    """处理 Cookie 弹窗"""
    if timeout is None:
        timeout = config.COOKIE_TIMEOUT
    try:
        # 使用配置文件中的 Cookie 选择器
        selectors = config.COOKIE_SELECTORS

        for selector in selectors:
            try:
                button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, selector)))
                button.click()
                print("✓ 已接受 Cookie")
                time.sleep(1)
                return True
            except:
                continue

        print("→ 未发现 Cookie 弹窗")
        return False
    except Exception as e:
        print(f"→ Cookie 处理跳过: {type(e).__name__}")
        return False


def scrape_product_list(driver, url):
    """爬取产品列表页面"""
    print(f"\n正在访问: {url}")
    driver.get(url)

    # 等待页面加载
    time.sleep(3)

    # 处理 Cookie 弹窗
    handle_cookie_popup(driver)

    # 等待产品卡片加载
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-card"]'))
        )
        print("✓ 产品列表已加载")
    except:
        print("✗ 未找到产品卡片")
        return []

    # 找到所有产品卡片
    product_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')
    print(f"✓ 找到 {len(product_cards)} 个产品")

    products = []

    for idx, card in enumerate(product_cards, 1):
        try:
            product = {}

            # 产品链接
            product["url"] = card.get_attribute("href")

            # 产品品牌
            try:
                brand_element = card.find_element(By.CSS_SELECTOR, ".ProductCard-module_productBrand__-rFtT")
                product["brand"] = brand_element.text.strip()
            except:
                product["brand"] = ""

            # 产品名称
            try:
                title_element = card.find_element(By.CSS_SELECTOR, ".ProductCard-module_title__ytKYE")
                product["name"] = title_element.text.strip()
            except:
                product["name"] = ""

            # 产品价格
            try:
                price_element = card.find_element(By.CSS_SELECTOR, ".MppProductCardPrice-module_price__bold__BpYBE")
                product["price"] = price_element.text.strip()
            except:
                product["price"] = ""

            # 产品图片
            try:
                image_element = card.find_element(By.CSS_SELECTOR, ".ProductCard-module_productImage__9bfwO")
                product["image"] = image_element.get_attribute("src")
            except:
                product["image"] = ""

            products.append(product)
            print(f"  [{idx}] {product['brand']} - {product['name'][:50]}...")

        except Exception as e:
            print(f"  ✗ 产品 {idx} 提取失败: {e}")
            continue

    return products


def main(max_pages=None, category_url=None):
    """
    主函数

    Args:
        max_pages: 最大爬取页数，None 表示全部
        category_url: 分类URL，None 使用默认
    """
    print("=" * 70)
    print("Holland & Barrett 多页爬虫")
    print("=" * 70)

    # 使用配置文件中的默认URL
    if category_url is None:
        category_url = config.DEFAULT_CATEGORY_URL

    product_type = config.get_product_type_from_url(category_url)

    print(f"\n目标分类: {product_type}")
    print(f"最大页数: {max_pages or '不限制'}")
    print(f"URL: {category_url}")

    # 使用配置文件中的 Chrome 选项
    options = config.get_chrome_options()

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 使用配置文件中的超时设置
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    driver.set_script_timeout(config.SCRIPT_TIMEOUT)

    try:
        # 使用配置文件中的多页爬取配置
        products = scrape_all_pages(
            driver=driver,
            base_url=category_url,
            scrape_single_page_func=scrape_product_list,
            max_pages=max_pages,
            enable_resume=config.ENABLE_RESUME
        )

        print(f"\n{'=' * 70}")
        print(f"爬取完成！共 {len(products)} 个产品")
        print(f"{'=' * 70}")

        # 使用配置文件中的输出路径
        if products:
            output_file = config.get_output_path(product_type=product_type, output_type='multipage')
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=config.CSV_FIELDNAMES_BASIC)
                writer.writeheader()
                writer.writerows(products)

            print(f"\n✓ 数据已保存到: {output_file}")
        else:
            print("\n✗ 未获取到任何产品")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断爬虫")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n关闭浏览器...")
        driver.quit()
        print("完成!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Holland & Barrett 多页爬虫")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="最大爬取页数（默认：不限制）"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="分类URL（默认：hair-skin-nails）"
    )

    args = parser.parse_args()

    main(max_pages=args.max_pages, category_url=args.url)

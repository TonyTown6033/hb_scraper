"""测试多页爬取功能"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def mock_scrape_function(driver, url):
    """模拟单页爬取函数"""
    print(f"  → 访问: {url}")
    driver.get(url)

    # 模拟爬取结果
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    time.sleep(2)

    try:
        # 等待产品卡片加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-card"]'))
        )

        # 找到所有产品卡片
        product_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')
        print(f"  ✓ 找到 {len(product_cards)} 个产品")

        products = []
        for idx, card in enumerate(product_cards[:5], 1):  # 只提取前5个作为测试
            try:
                product = {}
                product["url"] = card.get_attribute("href")

                # 产品名称
                try:
                    title_element = card.find_element(By.CSS_SELECTOR, ".ProductCard-module_title__ytKYE")
                    product["name"] = title_element.text.strip()
                except:
                    product["name"] = f"Product {idx}"

                products.append(product)
                print(f"    [{idx}] {product['name'][:40]}...")

            except Exception as e:
                print(f"    ✗ 产品 {idx} 提取失败: {e}")
                continue

        return products

    except Exception as e:
        print(f"  ✗ 页面加载失败: {e}")
        return []


def test_multi_page():
    """测试多页爬取"""
    print("\n" + "=" * 70)
    print("测试多页爬取功能")
    print("=" * 70)

    # 配置 Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        from utils.multi_page_scraper import scrape_all_pages

        # 测试URL
        test_url = "https://www.hollandandbarrett.com/shop/vitamins-supplements/condition/hair-skin-nails/"

        print("\n测试场景: 爬取前 2 页")
        print("=" * 70)

        # 爬取前2页
        products = scrape_all_pages(
            driver=driver,
            base_url=test_url,
            scrape_single_page_func=mock_scrape_function,
            max_pages=2,
            enable_resume=False  # 测试时不启用断点续传
        )

        print("\n" + "=" * 70)
        print("测试结果")
        print("=" * 70)
        print(f"✓ 总共获取: {len(products)} 个产品")
        print(f"✓ 前5个产品:")
        for idx, product in enumerate(products[:5], 1):
            print(f"  {idx}. {product.get('name', 'N/A')}")

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n关闭浏览器...")
        driver.quit()
        print("完成!")


if __name__ == "__main__":
    test_multi_page()

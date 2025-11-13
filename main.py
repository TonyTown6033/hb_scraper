from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os
import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional


def handle_cookie_popup(driver, timeout=5):
    """优雅地处理 Cookie 弹窗"""
    try:
        # 尝试多种可能的 Cookie 接受按钮选择器
        selectors = [
            "//button[contains(text(), 'Yes I Accept')]",
            "//button[contains(text(), 'Accept')]",
            "//button[@id='onetrust-accept-btn-handler']",
        ]

        for selector in selectors:
            try:
                button = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
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
    """爬取产品列表页面的基本信息"""
    print(f"\n正在访问列表页: {url}")
    driver.get(url)

    # 等待页面加载
    time.sleep(3)

    # 处理 Cookie 弹窗
    handle_cookie_popup(driver)

    # 等待产品卡片加载
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="product-card"]')
            )
        )
        print("✓ 产品列表已加载")
    except:
        print("✗ 未找到产品卡片")
        return []

    # 找到所有产品卡片
    product_cards = driver.find_elements(
        By.CSS_SELECTOR, '[data-testid="product-card"]'
    )
    print(f"✓ 找到 {len(product_cards)} 个产品")

    products = []

    for idx, card in enumerate(product_cards, 1):
        try:
            # 提取基本信息
            product = {}

            # 产品链接
            product["url"] = card.get_attribute("href")

            # 产品品牌
            try:
                brand_element = card.find_element(
                    By.CSS_SELECTOR, ".ProductCard-module_productBrand__-rFtT"
                )
                product["brand"] = brand_element.text.strip()
            except:
                product["brand"] = ""

            # 产品名称
            try:
                title_element = card.find_element(
                    By.CSS_SELECTOR, ".ProductCard-module_title__ytKYE"
                )
                product["name"] = title_element.text.strip()
            except:
                product["name"] = ""

            # 产品价格
            try:
                price_element = card.find_element(
                    By.CSS_SELECTOR, ".MppProductCardPrice-module_price__bold__BpYBE"
                )
                product["price"] = price_element.text.strip()
            except:
                product["price"] = ""

            # 产品图片
            try:
                image_element = card.find_element(
                    By.CSS_SELECTOR, ".ProductCard-module_productImage__9bfwO"
                )
                product["image"] = image_element.get_attribute("src")
            except:
                product["image"] = ""

            products.append(product)
            print(f"  [{idx}] {product['brand']} - {product['name'][:50]}...")

        except Exception as e:
            print(f"  ✗ 产品 {idx} 提取失败: {e}")
            continue

    return products


def find_product_uuid(widgets: List[Dict]) -> Optional[str]:
    """递归查找产品数据的UUID"""
    for widget in widgets:
        if widget.get("name") == "accordions":
            refs = widget.get("resolveParamRefs", {})
            for key, uuid in refs.items():
                if "pdp_product_data" in key:
                    return uuid
        if "children" in widget and widget["children"]:
            uuid = find_product_uuid(widget["children"])
            if uuid:
                return uuid
    return None


def clean_html(html_text: str) -> str:
    """清理HTML标签，返回纯文本"""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(strip=True, separator=" ")


def extract_product_json(html_content: str) -> Dict[str, Any]:
    """从HTML中提取产品JSON数据"""
    # 提取JSON数据
    match = re.search(
        r'<script id="__LAYOUT__"[^>]*>(.*?)</script>', html_content, re.DOTALL
    )

    if not match:
        print("  ✗ 未找到__LAYOUT__数据")
        return {}

    try:
        layout_data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON解析失败: {e}")
        return {}

    # 查找产品数据UUID
    product_uuid = find_product_uuid(layout_data.get("widgets", []))
    if not product_uuid:
        print("  ✗ 未找到产品UUID")
        return {}

    # 获取产品数据
    resolve_values = layout_data.get("resolveParamValues", {})
    if product_uuid not in resolve_values:
        print(f"  ✗ UUID {product_uuid} 未找到")
        return {}

    product_wrapper = resolve_values[product_uuid]
    if "data" not in product_wrapper:
        print("  ✗ 产品数据格式错误")
        return {}

    return product_wrapper["data"]


def scrape_product_detail(driver, url):
    """爬取产品详情页的详细信息"""
    try:
        driver.get(url)
        time.sleep(3)

        # 获取页面HTML
        html_content = driver.page_source

        # 提取JSON数据
        product_data = extract_product_json(html_content)

        if not product_data:
            return {}

        details = {}

        # 产品亮点
        benefits = product_data.get("benefits", [])
        details["highlights"] = "; ".join(benefits) if benefits else ""

        # 产品描述
        description_html = product_data.get("description", "")
        details["description"] = clean_html(description_html)

        # Info Sections
        info_sections = product_data.get("infoSections", {})
        info_section = info_sections.get("infoSection", {})

        # 用法服量
        directions = info_section.get("directions", {})
        details["directions"] = f"{directions.get('heading', '')} {directions.get('text', '')}".strip()

        # 配料表
        ingredients = info_section.get("otherIngredients", {})
        ingredients_html = ingredients.get("text", "")
        details["ingredients"] = clean_html(ingredients_html)

        # 营养成分
        nutritionals = info_sections.get("nutritionals", [])
        nutritional_text = []
        for nutritional in nutritionals:
            for section in nutritional.get("sections", []):
                fact = section.get("fact", {})
                for item in fact.get("keys", []):
                    nutrient = item.get("key", "").strip()
                    amount = item.get("value", "").strip()
                    if nutrient and amount:
                        nutritional_text.append(f"{nutrient}: {amount}")
        details["nutritional_info"] = "; ".join(nutritional_text)

        # 产品类型和作用部位（从CSV模板来看需要这些字段，但JSON中可能没有直接对应）
        # 暂时留空，后续可以根据实际需要补充
        details["product_type"] = ""
        details["target_area"] = ""

        return details

    except Exception as e:
        print(f"  ✗ 详情提取失败: {e}")
        return {}


def main():
    print("=" * 60)
    print("Holland & Barrett 产品爬虫")
    print("=" * 60)

    # 配置 Chrome 选项
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 使用 webdriver_manager 自动管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 爬取产品列表
        list_url = "https://www.hollandandbarrett.com/shop/vitamins-supplements/condition/hair-skin-nails/"
        product_type = list_url.split("/shop/")[1].split("/")[0]
        products = scrape_product_list(driver, list_url)

        print(f"\n{'=' * 60}")
        print(f"共爬取 {len(products)} 个产品的基本信息")
        print(f"{'=' * 60}")

        # 保存基本信息到CSV（暂时不包含详情）
        output_file = "data/output/products_basic.csv"
        if products:
            with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["brand", "name", "price", "image", "url"]
                )
                writer.writeheader()
                writer.writerows(products)
            print(f"\n✓ 基本信息已保存到: {output_file}")

        # 询问是否继续爬取详情页
        print("\n下一步: 爬取产品详情页（需要更多时间）")
        print("提示: 详情页爬取会花费较长时间，建议先测试几个产品")
        response = input("是否继续爬取详情页？(y/n): ")

        if response.lower() == "y":
            # 询问爬取数量
            try:
                max_count = input(
                    f"要爬取多少个产品？(1-{len(products)}, 回车默认全部): "
                ).strip()
                if max_count:
                    max_products = min(int(max_count), len(products))
                else:
                    max_products = len(products)
            except ValueError:
                max_products = len(products)

            print(f"\n开始爬取 {max_products} 个产品的详情...")
            print(f"{'=' * 60}")

            for idx, product in enumerate(products[:max_products], 1):
                print(f"\n[{idx}/{max_products}] {product['name'][:50]}...")
                details = scrape_product_detail(driver, product["url"])
                product.update(details)
                time.sleep(2)  # 避免请求过快

            # 保存完整数据到CSV
            final_output = "data/output/products_complete.csv"
            fieldnames = [
                "产品名称",
                "产品亮点",
                "产品价格",
                "产品品牌",
                "产品图",
                "产品描述",
                "产品类型",
                "作用部位",
                "用法服量",
                "知识科普",
                "营养成分",
                "配料表",
                "URL",
            ]

            with open(final_output, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for product in products[:max_products]:
                    row = {
                        "产品名称": product.get("name", ""),
                        "产品亮点": product.get("highlights", ""),
                        "产品价格": product.get("price", ""),
                        "产品品牌": product.get("brand", ""),
                        "产品图": product.get("image", ""),
                        "产品描述": product.get("description", ""),
                        "产品类型": product_type,
                        "作用部位": product.get("target_area", ""),
                        "用法服量": product.get("directions", ""),
                        "知识科普": product.get("knowledge", ""),
                        "营养成分": product.get("nutritional_info", ""),
                        "配料表": product.get("ingredients", ""),
                        "URL": product.get("url", ""),
                    }
                    writer.writerow(row)

            print(f"\n{'=' * 60}")
            print(f"✓ 完整数据已保存到: {final_output}")
            print(f"✓ 共爬取 {max_products} 个产品的完整信息")
            print(f"{'=' * 60}")

    except KeyboardInterrupt:
        print("\n\n用户中断爬虫")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
    finally:
        print("\n关闭浏览器...")
        driver.quit()
        print("完成!")


if __name__ == "__main__":
    main()

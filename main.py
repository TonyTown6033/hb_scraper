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
from utils.translate import translate_main
from scripts.process_csv_images import image_post_precessor
from utils.multi_page_scraper import scrape_all_pages
from utils.parallel_scraper import scrape_details_parallel
from utils.logger import setup_logger, get_logger
import logging
import config


def handle_cookie_popup(driver, timeout=None):
    """优雅地处理 Cookie 弹窗"""
    logger = get_logger()
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
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="product-card"]'))
        )
        print("✓ 产品列表已加载")
    except:
        print("✗ 未找到产品卡片")
        return []

    # 找到所有产品卡片
    product_cards = driver.find_elements(By.CSS_SELECTOR, '[data-test="product-card"]')
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
                brand_element = card.find_element(By.CSS_SELECTOR, '[data-test="product-card-brand-name"]')
                product["brand"] = brand_element.text.strip()
            except:
                product["brand"] = ""

            # 产品名称
            try:
                title_element = card.find_element(By.CSS_SELECTOR, '[data-test="product-card-title"]')
                product["name"] = title_element.text.strip()
            except:
                product["name"] = ""

            # 产品价格
            try:
                price_element = card.find_element(By.CSS_SELECTOR, '[data-test="product-card-price"]')
                product["price"] = price_element.text.strip()
            except:
                product["price"] = ""

            # 产品图片
            try:
                image_element = card.find_element(By.CSS_SELECTOR, '[data-test="product-image"]')
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
    match = re.search(r'<script id="__LAYOUT__"[^>]*>(.*?)</script>', html_content, re.DOTALL)

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

        # 增加等待时间，确保页面完全加载
        time.sleep(4)

        # 等待页面关键元素加载
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except:
            pass  # 超时也继续尝试

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

        # 用法说明
        directions = info_section.get("directions", {})
        heading = directions.get("heading", "")
        text = directions.get("text", "")
        details["directions"] = f"{heading} {text}".strip()

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

        # 作用部位（从CSV模板来看需要这些字段，但JSON中可能没有直接对应）
        # 暂时留空，后续可以根据实际需要补充
        details["target_area"] = ""

        return details

    except Exception as e:
        print(f"  ✗ 详情提取失败: {e}")
        return {}


def main():
    print("=" * 60)
    print("Holland & Barrett 产品爬虫")
    print("=" * 60)

    # 使用配置文件中的 Chrome 选项
    options = config.get_chrome_options()

    # 使用 webdriver_manager 自动管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 使用配置文件中的超时设置
    driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
    driver.set_script_timeout(config.SCRIPT_TIMEOUT)

    try:
        # 使用配置文件中的默认URL
        list_url = config.DEFAULT_CATEGORY_URL
        product_type = config.get_product_type_from_url(list_url)

        # 爬取模式选择 - 支持交互式和非交互式
        if config.INTERACTIVE_MODE:
            print("\n爬取模式:")
            print("  1. 单页模式 - 仅爬取第一页（快速测试）")
            print("  2. 多页模式 - 爬取所有页面（完整数据）")
            print("  3. 限制页数 - 爬取指定页数")
            mode = input("\n选择模式 (1/2/3, 默认1): ").strip() or "1"
        else:
            mode = str(config.SCRAPE_MODE)
            print(f"\n使用配置文件中的爬取模式: {mode}")

        if mode == "1":
            # 单页模式
            print("  → 单页模式")
            products = scrape_product_list(driver, list_url)
        elif mode == "2":
            # 多页模式 - 爬取所有页
            print("  → 多页模式 - 爬取所有页面")
            products = scrape_all_pages(
                driver=driver,
                base_url=list_url,
                scrape_single_page_func=scrape_product_list,
                max_pages=None,
                enable_resume=config.ENABLE_RESUME
            )
        elif mode == "3":
            # 限制页数模式
            if config.INTERACTIVE_MODE:
                try:
                    max_pages = int(input("要爬取多少页？: ").strip())
                except ValueError:
                    print("输入无效，使用配置文件默认值")
                    max_pages = config.MAX_PAGES_LIMIT
            else:
                max_pages = config.MAX_PAGES_LIMIT

            print(f"  → 限制页数模式 - 爬取{max_pages}页")
            products = scrape_all_pages(
                driver=driver,
                base_url=list_url,
                scrape_single_page_func=scrape_product_list,
                max_pages=max_pages,
                enable_resume=config.ENABLE_RESUME
            )
        else:
            print("无效选择，使用单页模式")
            products = scrape_product_list(driver, list_url)

        print(f"\n{'=' * 60}")
        print(f"共爬取 {len(products)} 个产品的基本信息")
        print(f"{'=' * 60}")

        # 使用配置文件中的输出路径
        output_file = config.get_output_path(output_type='basic')
        if products:
            with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=config.CSV_FIELDNAMES_BASIC)
                writer.writeheader()
                writer.writerows(products)
            print(f"\n✓ 基本信息已保存到: {output_file}")

        # 询问是否继续爬取详情页 - 支持交互式和非交互式
        if config.INTERACTIVE_MODE:
            print("\n下一步: 爬取产品详情页（需要更多时间）")
            print("提示: 详情页爬取会花费较长时间，建议先测试几个产品")
            response = input("是否继续爬取详情页？(y/n): ")
            scrape_details = response.lower() == "y"
        else:
            scrape_details = config.SCRAPE_DETAILS
            if scrape_details:
                print("\n配置文件设置: 爬取详情页")
            else:
                print("\n配置文件设置: 跳过详情页爬取")

        if scrape_details:
            # 询问爬取数量 - 支持交互式和非交互式
            if config.INTERACTIVE_MODE:
                try:
                    max_count = input(f"要爬取多少个产品？(1-{len(products)}, 回车默认全部): ").strip()
                    if max_count:
                        max_products = min(int(max_count), len(products))
                    else:
                        max_products = len(products)
                except ValueError:
                    max_products = len(products)
            else:
                if config.MAX_PRODUCTS_TO_SCRAPE is not None:
                    max_products = min(config.MAX_PRODUCTS_TO_SCRAPE, len(products))
                    print(f"配置文件设置: 爬取{max_products}个产品")
                else:
                    max_products = len(products)
                    print(f"配置文件设置: 爬取全部{max_products}个产品")

            # 询问是否使用并行爬取 - 支持交互式和非交互式
            if config.INTERACTIVE_MODE:
                print("\n爬取模式:")
                print("  1. 顺序模式 - 一个接一个爬取（较慢但稳定）")
                print("  2. 并行模式 - 多线程同时爬取（推荐，3-5个线程）")
                parallel_mode = input("选择模式 (1/2, 默认2): ").strip() or "2"
            else:
                parallel_mode = str(config.DETAIL_SCRAPE_MODE)
                mode_name = "并行模式" if parallel_mode == "2" else "顺序模式"
                print(f"配置文件设置: {mode_name}")

            if parallel_mode == "2":
                # 并行模式配置 - 支持交互式和非交互式
                if config.INTERACTIVE_MODE:
                    print(f"\n提示: 建议使用{config.DEFAULT_MAX_WORKERS}-5个线程以平衡速度和稳定性")
                    try:
                        workers = input(f"并发线程数 (建议{config.DEFAULT_MAX_WORKERS}-5, 默认{config.DEFAULT_MAX_WORKERS}): ").strip() or str(config.DEFAULT_MAX_WORKERS)
                        max_workers = min(max(int(workers), 1), config.MAX_WORKERS_LIMIT)
                    except ValueError:
                        max_workers = config.DEFAULT_MAX_WORKERS
                else:
                    max_workers = config.DEFAULT_MAX_WORKERS
                    print(f"配置文件设置: {max_workers}个并发线程")

                retry_times = config.RETRY_TIMES
                request_delay = (config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)

                print(f"\n使用并行模式爬取 {max_products} 个产品，{max_workers} 个线程并发")
                print(f"配置: {retry_times}次重试, {request_delay[0]}-{request_delay[1]}秒随机延迟")
                print(f"💡 每{config.BATCH_SIZE}个产品自动写入CSV，避免内存占用过大")
                print(f"{'=' * 60}")

                # 使用配置文件中的路径和字段名
                final_output = config.get_output_path(output_type='complete')
                fieldnames = config.CSV_FIELDNAMES_COMPLETE

                # 创建批次写入回调函数
                def write_batch_to_csv(batch_products, batch_num):
                    """将批次产品写入CSV"""
                    from pathlib import Path
                    output_path = Path(final_output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    # 第一批写入时包含表头，后续批次追加
                    mode = 'w' if batch_num == 1 else 'a'
                    write_header = (batch_num == 1)

                    with open(output_path, mode, newline="", encoding="utf-8-sig") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        if write_header:
                            writer.writeheader()

                        for product in batch_products:
                            row = {
                                "产品名称": product.get("name", ""),
                                "产品价格": product.get("price", ""),
                                "产品亮点": product.get("highlights", ""),
                                "用法说明": product.get("directions", ""),
                                "产品图": product.get("image", ""),
                                "产品类型": product_type,
                                "作用部位": product.get("target_area", ""),
                                "配料表": product.get("ingredients", ""),
                                "产品品牌": product.get("brand", ""),
                                "产品描述": product.get("description", ""),
                                "营养成分": product.get("nutritional_info", ""),
                                "URL": product.get("url", ""),
                            }
                            writer.writerow(row)

                    print(f"✓ 批次 {batch_num} 已写入 {len(batch_products)} 个产品到 {final_output}")

                # 使用并行爬取（带分批写入）- 使用配置文件中的批次大小
                products = scrape_details_parallel(
                    products=products,
                    scrape_detail_func=scrape_product_detail,
                    max_workers=max_workers,
                    max_products=max_products,
                    retry_times=retry_times,
                    request_delay=request_delay,
                    batch_size=config.BATCH_SIZE,
                    batch_callback=write_batch_to_csv
                )
            else:
                # 顺序爬取（保留原有逻辑）
                print(f"\n使用顺序模式爬取 {max_products} 个产品的详情...")
                print(f"{'=' * 60}")

                failed_products = []  # 记录失败的产品
                for idx, product in enumerate(products[:max_products], 1):
                    print(f"\n[{idx}/{max_products}] {product['name'][:50]}...")
                    try:
                        details = scrape_product_detail(driver, product["url"])
                        # 检查是否成功获取到详情
                        if details and any(key in details for key in ['highlights', 'description', 'directions']):
                            product.update(details)
                        else:
                            print(f"  ✗ 未获取到详情数据")
                            failed_products.append({
                                "item_data": product.copy(),
                                "error": "未获取到详情数据",
                                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "url": product["url"]
                            })
                    except Exception as e:
                        print(f"  ✗ 爬取失败: {e}")
                        failed_products.append({
                            "item_data": product.copy(),
                            "error": str(e),
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "url": product["url"]
                        })
                    time.sleep(2)  # 避免请求过快

                # 保存失败记录 - 使用配置文件中的路径
                if failed_products:
                    import json
                    from pathlib import Path
                    failed_file = config.get_output_path(output_type='failed')
                    failed_file.parent.mkdir(parents=True, exist_ok=True)

                    # 加载现有失败记录
                    existing_failed = []
                    if failed_file.exists():
                        try:
                            with open(failed_file, 'r', encoding='utf-8') as f:
                                existing_failed = json.load(f)
                        except:
                            pass

                    # 合并并保存
                    all_failed = existing_failed + failed_products
                    with open(failed_file, 'w', encoding='utf-8') as f:
                        json.dump(all_failed, f, ensure_ascii=False, indent=2)

                    print(f"\n✗ {len(failed_products)} 个产品爬取失败，已记录到: {failed_file}")
                    print(f"  可使用 'uv run python scripts/retry_failed.py' 重新爬取")

            # 保存完整数据到CSV（如果是并行模式且使用了分批写入，则跳过）
            if parallel_mode != "2":  # 顺序模式需要保存
                # 使用配置文件中的路径和字段名
                final_output = config.get_output_path(output_type='complete')
                fieldnames = config.CSV_FIELDNAMES_COMPLETE

                with open(final_output, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for product in products[:max_products]:
                        row = {
                            "产品名称": product.get("name", ""),
                            "产品价格": product.get("price", ""),
                            "产品亮点": product.get("highlights", ""),
                            "用法说明": product.get("directions", ""),
                            "产品图": product.get("image", ""),
                            "产品类型": product_type,
                            "作用部位": product.get("target_area", ""),
                            "配料表": product.get("ingredients", ""),
                            "产品品牌": product.get("brand", ""),
                            "产品描述": product.get("description", ""),
                            "营养成分": product.get("nutritional_info", ""),
                            "URL": product.get("url", ""),
                        }
                        writer.writerow(row)

            print(f"\n{'=' * 60}")
            if parallel_mode == "2":
                # 并行模式已经分批保存
                print(f"✓ 所有数据已保存到: data/output/products_complete.csv")
                print(f"✓ 共爬取 {len(products)} 个产品的完整信息")
            else:
                # 顺序模式最后保存
                print(f"✓ 完整数据已保存到: data/output/products_complete.csv")
                print(f"✓ 共爬取 {max_products} 个产品的完整信息")
            print(f"{'=' * 60}")

        # 运行翻译和图片处理 - 根据配置决定
        if config.RUN_TRANSLATION:
            print("\n运行翻译...")
            translate_main()
        else:
            print("\n跳过翻译（配置文件设置）")

        if config.RUN_IMAGE_PROCESSING:
            print("\n运行图片处理...")
            image_post_precessor()
        else:
            print("\n跳过图片处理（配置文件设置）")
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

"""多页爬虫工具 - 支持分页爬取和断点续传"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger


class MultiPageScraper:
    """多页爬虫管理器"""

    def __init__(self, driver):
        """
        初始化多页爬虫

        Args:
            driver: Selenium WebDriver 实例
        """
        self.driver = driver
        self.progress_file = Path("data/output/scrape_progress.json")
        self.logger = get_logger()

    def has_next_page(self) -> bool:
        """
        检查是否有下一页

        Returns:
            bool: 是否有下一页
        """
        try:
            # 查找"下一页"按钮 - 使用 data-test 属性
            next_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[data-test="button-next"]'
            )

            if not next_buttons:
                return False

            # 检查按钮是否禁用
            next_button = next_buttons[0]
            is_disabled = (
                next_button.get_attribute("disabled") == "true" or
                next_button.get_attribute("aria-disabled") == "true" or
                "disabled" in (next_button.get_attribute("class") or "")
            )

            return not is_disabled

        except Exception as e:
            print(f"  → 检查下一页时出错: {e}")
            return False

    def get_current_page_number(self) -> int:
        """
        获取当前页码

        Returns:
            int: 当前页码，获取失败返回 1
        """
        try:
            # 尝试从URL参数获取
            current_url = self.driver.current_url
            if "page=" in current_url:
                import re
                match = re.search(r'page=(\d+)', current_url)
                if match:
                    return int(match.group(1))

            # 尝试从分页元素获取
            current_page_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                'button[aria-current="page"], a[aria-current="page"]'
            )
            if current_page_elements:
                return int(current_page_elements[0].text.strip())

            return 1

        except Exception as e:
            print(f"  → 获取页码时出错: {e}")
            return 1

    def _handle_cookie_popup(self):
        """处理可能出现的 Cookie 弹窗"""
        try:
            # 尝试查找并关闭 Cookie 弹窗
            cookie_selectors = [
                "//button[contains(text(), 'Yes I Accept')]",
                "//button[contains(text(), 'Accept')]",
                "//button[@id='onetrust-accept-btn-handler']",
                "#onetrust-accept-btn-handler",
            ]
            
            for selector in cookie_selectors:
                try:
                    if selector.startswith("//"):
                        button = self.driver.find_element(By.XPATH, selector)
                    else:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if button.is_displayed():
                        button.click()
                        print("  → 已关闭 Cookie 弹窗")
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            return False

    def go_to_next_page(self) -> bool:
        """
        跳转到下一页

        Returns:
            bool: 是否成功跳转
        """
        try:
            if not self.has_next_page():
                return False

            # 获取当前页码
            current_page = self.get_current_page_number()

            # 处理可能出现的 Cookie 弹窗
            self._handle_cookie_popup()

            # 点击"下一页"按钮 - 使用 data-test 属性
            next_button = self.driver.find_element(
                By.CSS_SELECTOR,
                '[data-test="button-next"]'
            )

            # 滚动到按钮位置
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)

            # 使用 JavaScript 点击(避免被遮挡)
            try:
                next_button.click()
            except Exception as click_error:
                # 如果普通点击失败,使用 JavaScript 点击
                print("  → 普通点击失败,尝试 JavaScript 点击...")
                self.driver.execute_script("arguments[0].click();", next_button)
            
            print(f"\n→ 点击下一页按钮...")

            # 等待页面加载
            time.sleep(3)

            # 等待产品卡片重新加载 - 使用正确的选择器
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="product-card"]'))
            )

            # 验证是否成功跳转
            new_page = self.get_current_page_number()
            if new_page > current_page or new_page == 1:  # 有些网站重置页码
                print(f"✓ 成功跳转到第 {new_page} 页")
                return True
            else:
                print(f"✗ 页码未变化，可能已到最后一页")
                return False

        except Exception as e:
            print(f"✗ 跳转下一页失败: {e}")
            return False

    def save_progress(self, data: Dict):
        """
        保存爬取进度

        Args:
            data: 进度数据
        """
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  → 保存进度失败: {e}")

    def load_progress(self) -> Optional[Dict]:
        """
        加载爬取进度

        Returns:
            Dict: 进度数据，不存在返回 None
        """
        try:
            if self.progress_file.exists():
                with open(self.progress_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"  → 加载进度失败: {e}")
        return None

    def clear_progress(self):
        """清除进度文件"""
        try:
            if self.progress_file.exists():
                self.progress_file.unlink()
        except Exception as e:
            print(f"  → 清除进度失败: {e}")

    def estimate_total_pages(self) -> Optional[int]:
        """
        估算总页数

        Returns:
            int: 估算的总页数，失败返回 None
        """
        try:
            # 查找分页按钮
            page_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                'nav[aria-label="Pagination"] button, nav[aria-label="Pagination"] a'
            )

            # 获取所有页码数字
            page_numbers = []
            for button in page_buttons:
                text = button.text.strip()
                if text.isdigit():
                    page_numbers.append(int(text))

            if page_numbers:
                return max(page_numbers)

            return None

        except Exception as e:
            print(f"  → 估算总页数失败: {e}")
            return None


def scrape_all_pages(
    driver,
    base_url: str,
    scrape_single_page_func,
    max_pages: Optional[int] = None,
    start_page: int = 1,
    enable_resume: bool = True
) -> List[Dict]:
    """
    爬取所有分页

    Args:
        driver: WebDriver 实例
        base_url: 基础URL
        scrape_single_page_func: 单页爬取函数，接收 driver 和 url 参数
        max_pages: 最大爬取页数，None 表示爬取所有页
        start_page: 起始页码
        enable_resume: 是否启用断点续传

    Returns:
        List[Dict]: 所有产品数据
    """
    scraper = MultiPageScraper(driver)
    all_products = []
    current_page = start_page

    # 尝试加载之前的进度
    if enable_resume:
        progress = scraper.load_progress()
        if progress and progress.get("base_url") == base_url:
            print(f"\n📂 发现之前的进度:")
            print(f"   已爬取: {progress.get('pages_scraped', 0)} 页")
            print(f"   产品数: {progress.get('total_products', 0)} 个")
            response = input("是否继续之前的爬取？(y/n): ").strip().lower()
            if response == "y":
                all_products = progress.get("products", [])
                current_page = progress.get("last_page", 1) + 1
                print(f"✓ 从第 {current_page} 页继续爬取")

    print(f"\n{'=' * 70}")
    print(f"开始多页爬取")
    print(f"{'=' * 70}")
    print(f"起始页: {current_page}")
    print(f"最大页数: {max_pages or '不限制'}")
    print(f"{'=' * 70}")

    # 构建起始URL
    if current_page > 1:
        if "?" in base_url:
            url = f"{base_url}&page={current_page}"
        else:
            url = f"{base_url}?page={current_page}"
    else:
        url = base_url

    page_count = 0

    try:
        while True:
            # 检查是否超过最大页数
            if max_pages and page_count >= max_pages:
                print(f"\n→ 已达到最大页数限制 ({max_pages} 页)")
                break

            print(f"\n{'=' * 70}")
            print(f"正在爬取第 {current_page} 页")
            print(f"{'=' * 70}")

            # 爬取当前页
            products = scrape_single_page_func(driver, url)

            if not products:
                print(f"✗ 第 {current_page} 页未获取到产品，停止爬取")
                break

            all_products.extend(products)
            page_count += 1

            print(f"✓ 第 {current_page} 页爬取完成，获得 {len(products)} 个产品")
            print(f"✓ 累计: {len(all_products)} 个产品")

            # 保存进度
            if enable_resume:
                scraper.save_progress({
                    "base_url": base_url,
                    "last_page": current_page,
                    "pages_scraped": page_count,
                    "total_products": len(all_products),
                    "products": all_products,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

            # 尝试跳转到下一页
            if not scraper.go_to_next_page():
                print(f"\n→ 没有更多页面了")
                break

            current_page += 1
            url = driver.current_url  # 使用当前URL

            # 稍微延迟，避免请求过快
            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断爬取")
        print(f"✓ 已保存进度，下次可继续")
        print(f"✓ 已爬取 {page_count} 页，共 {len(all_products)} 个产品")

    # 清除进度文件（如果正常完成）
    if enable_resume:
        scraper.clear_progress()

    print(f"\n{'=' * 70}")
    print(f"多页爬取完成")
    print(f"{'=' * 70}")
    print(f"总页数: {page_count}")
    print(f"总产品: {len(all_products)}")
    print(f"{'=' * 70}")

    return all_products

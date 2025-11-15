"""带日志功能的爬虫辅助函数"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils.logger import get_logger


def handle_cookie_popup_logged(driver, timeout=5):
    """处理 Cookie 弹窗（带日志）"""
    logger = get_logger()
    logger.debug("开始处理 Cookie 弹窗")

    try:
        selectors = [
            "//button[contains(text(), 'Yes I Accept')]",
            "//button[contains(text(), 'Accept')]",
            "//button[@id='onetrust-accept-btn-handler']",
        ]

        for selector in selectors:
            try:
                button = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, selector)))
                button.click()
                logger.info("✓ 已接受 Cookie")
                time.sleep(1)
                return True
            except:
                continue

        logger.debug("未发现 Cookie 弹窗")
        return False

    except Exception as e:
        logger.debug(f"Cookie 处理跳过: {type(e).__name__}")
        return False


def scrape_product_list_logged(driver, url):
    """爬取产品列表（带日志）"""
    logger = get_logger()

    logger.info(f"正在访问列表页: {url}")
    try:
        driver.get(url)
        logger.debug("页面加载完成，等待3秒")
        time.sleep(3)

        # 处理 Cookie
        handle_cookie_popup_logged(driver)

        # 等待产品卡片
        logger.debug("等待产品卡片加载...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-card"]'))
            )
            logger.info("✓ 产品列表已加载")
        except Exception as e:
            logger.error(f"✗ 未找到产品卡片: {e}")
            return []

        # 提取产品
        product_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')
        logger.info(f"✓ 找到 {len(product_cards)} 个产品")

        products = []
        for idx, card in enumerate(product_cards, 1):
            try:
                product = {}

                # 提取信息
                product["url"] = card.get_attribute("href")

                try:
                    brand_element = card.find_element(By.CSS_SELECTOR, ".ProductCard-module_productBrand__-rFtT")
                    product["brand"] = brand_element.text.strip()
                except:
                    product["brand"] = ""
                    logger.debug(f"产品 {idx} 未找到品牌信息")

                try:
                    title_element = card.find_element(By.CSS_SELECTOR, ".ProductCard-module_title__ytKYE")
                    product["name"] = title_element.text.strip()
                except:
                    product["name"] = ""
                    logger.warning(f"产品 {idx} 未找到名称")

                try:
                    price_element = card.find_element(By.CSS_SELECTOR, ".MppProductCardPrice-module_price__bold__BpYBE")
                    product["price"] = price_element.text.strip()
                except:
                    product["price"] = ""

                try:
                    image_element = card.find_element(By.CSS_SELECTOR, ".ProductCard-module_productImage__9bfwO")
                    product["image"] = image_element.get_attribute("src")
                except:
                    product["image"] = ""

                products.append(product)
                logger.debug(f"[{idx}] {product['brand']} - {product['name'][:40]}")

            except Exception as e:
                logger.error(f"✗ 产品 {idx} 提取失败: {e}")
                continue

        logger.info(f"成功提取 {len(products)} 个产品")
        return products

    except Exception as e:
        logger.exception(f"爬取页面时发生错误: {e}")
        return []

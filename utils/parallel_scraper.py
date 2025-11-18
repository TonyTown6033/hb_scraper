"""并行爬取工具 - 使用多线程加速详情页爬取"""

import time
import random
import json
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Semaphore
from typing import List, Dict, Callable, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import get_logger


class ParallelScraper:
    """并行爬取管理器"""

    def __init__(
        self,
        max_workers: int = 4,
        retry_times: int = 3,
        request_delay: tuple = (1, 3),
        enable_headless: bool = True
    ):
        """
        初始化并行爬取器

        Args:
            max_workers: 最大并发线程数，默认4个
            retry_times: 失败重试次数，默认3次
            request_delay: 请求延迟范围(最小, 最大)秒，默认(1, 3)
            enable_headless: 是否启用无头模式，默认True
        """
        self.max_workers = max_workers
        self.retry_times = retry_times
        self.request_delay = request_delay
        self.enable_headless = enable_headless
        self.logger = get_logger()
        self.lock = Lock()  # 用于保护共享资源
        self.rate_limiter = Semaphore(max_workers)  # 限流控制
        self.failed_items = []  # 记录失败的产品

    def _create_driver(self) -> webdriver.Chrome:
        """
        为每个线程创建独立的WebDriver实例

        Returns:
            webdriver.Chrome: Chrome WebDriver实例
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        if self.enable_headless:
            options.add_argument("--headless=new")  # 新版无头模式

        # 性能优化选项
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-images")  # 禁用图片加载，提速

        # 设置User-Agent，避免被识别为爬虫
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # 设置页面加载策略
        options.page_load_strategy = 'normal'

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # 设置超时时间
        driver.set_page_load_timeout(30)  # 页面加载超时30秒
        driver.set_script_timeout(30)  # 脚本执行超时30秒

        return driver

    def _scrape_single_item(
        self,
        item_data: Dict,
        scrape_func: Callable,
        item_index: int,
        total_items: int
    ) -> Dict:
        """
        爬取单个项目（在单独的线程中运行，带重试机制）

        Args:
            item_data: 项目数据
            scrape_func: 爬取函数
            item_index: 当前索引
            total_items: 总数

        Returns:
            Dict: 更新后的项目数据
        """
        driver = None
        url = item_data.get("url", "")

        # 使用信号量控制并发请求速率
        with self.rate_limiter:
            # 添加随机延迟，避免请求过快
            delay = random.uniform(*self.request_delay)
            time.sleep(delay)

            # 重试机制
            for attempt in range(1, self.retry_times + 1):
                try:
                    # 如果不是第一次尝试，先关闭之前的driver
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                        time.sleep(2)  # 重试前等待

                    # 创建新的driver
                    driver = self._create_driver()

                    # 执行爬取
                    if attempt > 1:
                        self.logger.warning(
                            f"[{item_index}/{total_items}] 重试 {attempt}/{self.retry_times}: {url}"
                        )
                    else:
                        self.logger.info(f"[{item_index}/{total_items}] 开始爬取: {url}")

                    details = scrape_func(driver, url)

                    # 合并数据
                    result = {**item_data, **details}

                    self.logger.info(
                        f"[{item_index}/{total_items}] ✓ 完成: {item_data.get('name', 'Unknown')[:40]}"
                    )

                    return result

                except Exception as e:
                    error_msg = str(e)
                    if attempt < self.retry_times:
                        self.logger.warning(
                            f"[{item_index}/{total_items}] 失败 (尝试 {attempt}/{self.retry_times}): "
                            f"{error_msg[:100]}"
                        )
                    else:
                        self.logger.error(
                            f"[{item_index}/{total_items}] ✗ 最终失败: {error_msg[:100]}"
                        )
                        # 记录失败信息
                        with self.lock:
                            self.failed_items.append({
                                "item_data": item_data,
                                "error": error_msg[:200],
                                "timestamp": datetime.now().isoformat(),
                                "url": url
                            })

                finally:
                    # 确保driver被关闭
                    if driver and attempt == self.retry_times:
                        try:
                            driver.quit()
                        except:
                            pass

            # 所有重试都失败，返回原始数据
            return item_data

    def scrape_items_parallel(
        self,
        items: List[Dict],
        scrape_func: Callable,
        max_items: int = None,
        batch_size: int = None,
        batch_callback: Callable = None
    ) -> List[Dict]:
        """
        并行爬取多个项目

        Args:
            items: 要爬取的项目列表
            scrape_func: 单个项目的爬取函数，接收(driver, url)参数
            max_items: 最大爬取数量，None表示全部
            batch_size: 分批大小，每爬取N个就调用回调函数，None表示不分批
            batch_callback: 分批回调函数，接收(batch_results, batch_num)参数

        Returns:
            List[Dict]: 爬取后的数据列表
        """
        # 确定要爬取的数量
        items_to_scrape = items[:max_items] if max_items else items
        total_items = len(items_to_scrape)

        self.logger.info(
            f"开始并行爬取 {total_items} 个项目\n"
            f"  - 线程数: {self.max_workers}\n"
            f"  - 重试次数: {self.retry_times}\n"
            f"  - 请求延迟: {self.request_delay[0]}-{self.request_delay[1]}秒"
        )

        start_time = time.time()
        results = []
        batch_results = []  # 临时批次结果
        completed_count = 0
        success_count = 0
        failed_count = 0
        batch_num = 0  # 当前批次号

        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_item = {
                executor.submit(
                    self._scrape_single_item,
                    item,
                    scrape_func,
                    idx + 1,
                    total_items
                ): item
                for idx, item in enumerate(items_to_scrape)
            }

            # 收集结果
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    results.append(result)
                    batch_results.append(result)  # 添加到批次结果
                    completed_count += 1

                    # 检查是否成功爬取到详情
                    original_item = future_to_item[future]
                    if result != original_item and any(
                        key in result for key in ['highlights', 'description', 'directions']
                    ):
                        success_count += 1
                    else:
                        failed_count += 1

                    # 检查是否需要执行批次回调
                    if batch_size and batch_callback and len(batch_results) >= batch_size:
                        batch_num += 1
                        self.logger.info(
                            f"\n📦 批次 {batch_num}: 已完成 {len(batch_results)} 个产品，正在写入CSV..."
                        )
                        batch_callback(batch_results, batch_num)
                        batch_results = []  # 清空批次结果

                    # 显示进度（每5个显示一次，避免刷屏）
                    if completed_count % 5 == 0 or completed_count == total_items:
                        elapsed = time.time() - start_time
                        avg_time = elapsed / completed_count
                        remaining = (total_items - completed_count) * avg_time

                        self.logger.info(
                            f"进度: {completed_count}/{total_items} "
                            f"({completed_count/total_items*100:.1f}%) - "
                            f"成功: {success_count}, 失败: {failed_count} - "
                            f"已用时: {elapsed:.1f}s - "
                            f"预计剩余: {remaining:.1f}s"
                        )

                except Exception as e:
                    self.logger.error(f"任务执行失败: {e}")
                    failed_count += 1

            # 处理最后一批（如果有剩余）
            if batch_size and batch_callback and batch_results:
                batch_num += 1
                self.logger.info(
                    f"\n📦 批次 {batch_num} (最后一批): 已完成 {len(batch_results)} 个产品，正在写入CSV..."
                )
                batch_callback(batch_results, batch_num)

        elapsed = time.time() - start_time
        self.logger.info(
            f"\n并行爬取完成!\n"
            f"  - 总耗时: {elapsed:.1f}s\n"
            f"  - 平均速度: {elapsed/total_items:.2f}s/项\n"
            f"  - 成功: {success_count}/{total_items} ({success_count/total_items*100:.1f}%)\n"
            f"  - 失败: {failed_count}/{total_items} ({failed_count/total_items*100:.1f}%)"
        )

        # 保存失败记录
        if self.failed_items:
            self._save_failed_items()

        return results

    def _save_failed_items(self):
        """保存失败的产品记录"""
        failed_file = Path("data/output/failed_products.json")
        failed_file.parent.mkdir(parents=True, exist_ok=True)

        # 如果文件已存在，加载并合并
        existing_failed = []
        if failed_file.exists():
            try:
                with open(failed_file, 'r', encoding='utf-8') as f:
                    existing_failed = json.load(f)
            except:
                pass

        # 合并新失败记录
        all_failed = existing_failed + self.failed_items

        # 保存到文件
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(all_failed, f, ensure_ascii=False, indent=2)

        self.logger.info(f"\n✗ {len(self.failed_items)} 个失败产品已记录到: {failed_file}")
        self.logger.info(f"  可使用 'uv run python scripts/retry_failed.py' 重新爬取")


def scrape_details_parallel(
    products: List[Dict],
    scrape_detail_func: Callable,
    max_workers: int = 3,
    max_products: int = None,
    retry_times: int = 3,
    request_delay: tuple = (2, 4),
    enable_headless: bool = True,
    batch_size: int = None,
    batch_callback: Callable = None
) -> List[Dict]:
    """
    并行爬取产品详情的便捷函数

    Args:
        products: 产品列表
        scrape_detail_func: 详情爬取函数
        max_workers: 最大并发数，默认3（降低以提高稳定性）
        max_products: 最大产品数
        retry_times: 失败重试次数，默认3
        request_delay: 请求延迟范围(秒)，默认(2, 4)
        enable_headless: 是否启用无头模式
        batch_size: 分批大小，每爬取N个就写入CSV，默认None（不分批）
        batch_callback: 分批回调函数，接收(batch_results, batch_num)

    Returns:
        List[Dict]: 包含详情的产品列表
    """
    scraper = ParallelScraper(
        max_workers=max_workers,
        retry_times=retry_times,
        request_delay=request_delay,
        enable_headless=enable_headless
    )
    return scraper.scrape_items_parallel(
        items=products,
        scrape_func=scrape_detail_func,
        max_items=max_products,
        batch_size=batch_size,
        batch_callback=batch_callback
    )

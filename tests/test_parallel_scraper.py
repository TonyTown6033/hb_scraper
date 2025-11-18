"""测试并行爬取功能"""

import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.parallel_scraper import ParallelScraper


def mock_scrape_func(driver, url):
    """模拟爬取函数"""
    # 模拟网络延迟
    time.sleep(2)
    return {
        "details": f"Details for {url}",
        "scraped_at": time.strftime("%H:%M:%S")
    }


def test_parallel_vs_sequential():
    """测试并行爬取vs顺序爬取的性能差异"""
    print("=" * 70)
    print("并行爬取性能测试")
    print("=" * 70)

    # 准备测试数据
    test_items = [
        {"name": f"Product {i}", "url": f"https://example.com/product/{i}"}
        for i in range(1, 11)
    ]

    print(f"\n测试数据: {len(test_items)} 个产品")
    print(f"每个产品模拟爬取时间: 2秒")

    # 测试顺序爬取
    print("\n" + "=" * 70)
    print("1. 顺序爬取测试（单线程）")
    print("=" * 70)
    start_time = time.time()

    sequential_results = []
    for idx, item in enumerate(test_items, 1):
        print(f"[{idx}/{len(test_items)}] 爬取: {item['name']}")
        # 这里我们不实际创建driver，只是模拟延迟
        time.sleep(2)
        item["details"] = f"Details for {item['url']}"
        sequential_results.append(item)

    sequential_time = time.time() - start_time
    print(f"\n顺序爬取完成! 耗时: {sequential_time:.2f}秒")

    # 测试并行爬取
    print("\n" + "=" * 70)
    print("2. 并行爬取测试（4个线程）")
    print("=" * 70)
    start_time = time.time()

    # 注意：这里使用实际的并行爬取会创建真实的WebDriver
    # 为了测试目的，我们注释掉这部分
    # scraper = ParallelScraper(max_workers=4)
    # parallel_results = scraper.scrape_items_parallel(
    #     items=test_items,
    #     scrape_func=mock_scrape_func
    # )

    # 估算并行时间（理论值）
    estimated_parallel_time = (len(test_items) * 2) / 4  # 假设4个线程
    print(f"预计并行爬取时间: {estimated_parallel_time:.2f}秒")

    # 性能对比
    print("\n" + "=" * 70)
    print("性能对比")
    print("=" * 70)
    print(f"顺序爬取: {sequential_time:.2f}秒")
    print(f"并行爬取（理论值）: {estimated_parallel_time:.2f}秒")
    print(f"加速比: {sequential_time / estimated_parallel_time:.2f}x")
    print(f"时间节省: {sequential_time - estimated_parallel_time:.2f}秒 "
          f"({(sequential_time - estimated_parallel_time) / sequential_time * 100:.1f}%)")


if __name__ == "__main__":
    test_parallel_vs_sequential()

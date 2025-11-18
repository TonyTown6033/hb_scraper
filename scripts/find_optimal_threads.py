#!/usr/bin/env python3
"""
自动寻找最佳线程数的性能测试工具

使用方法:
    uv run python scripts/find_optimal_threads.py

这个脚本会:
1. 测试不同线程数的性能
2. 记录成功率和耗时
3. 推荐最佳配置
"""

import sys
import time
import csv
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.parallel_scraper import scrape_details_parallel
from main import scrape_product_detail, scrape_product_list


def create_test_driver():
    """创建测试用的driver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def test_thread_count(products, thread_count, test_size=10):
    """
    测试特定线程数的性能

    Args:
        products: 产品列表
        thread_count: 线程数
        test_size: 测试产品数量

    Returns:
        dict: 测试结果
    """
    print(f"\n{'=' * 70}")
    print(f"测试配置: {thread_count} 个线程, {test_size} 个产品")
    print(f"{'=' * 70}")

    start_time = time.time()

    # 执行并行爬取
    results = scrape_details_parallel(
        products=products[:test_size],
        scrape_detail_func=scrape_product_detail,
        max_workers=thread_count,
        max_products=test_size,
        retry_times=2,  # 测试时减少重试次数
        request_delay=(1, 2),  # 测试时使用较短延迟
        enable_headless=True
    )

    elapsed = time.time() - start_time

    # 计算成功率
    success_count = sum(
        1 for r in results
        if any(key in r for key in ['highlights', 'description', 'directions'])
    )
    success_rate = (success_count / test_size) * 100

    result = {
        'threads': thread_count,
        'total_time': elapsed,
        'avg_time': elapsed / test_size,
        'success_count': success_count,
        'success_rate': success_rate,
        'products_per_second': test_size / elapsed
    }

    print(f"\n结果:")
    print(f"  总耗时: {elapsed:.1f}秒")
    print(f"  平均速度: {result['avg_time']:.2f}秒/产品")
    print(f"  成功率: {success_rate:.1f}% ({success_count}/{test_size})")
    print(f"  吞吐量: {result['products_per_second']:.2f} 产品/秒")

    return result


def main():
    print("=" * 70)
    print("WebDriver 并发性能测试工具")
    print("=" * 70)
    print("\n这个工具将帮助你找到系统的最佳线程配置")
    print("测试过程可能需要几分钟...\n")

    # 获取测试URL
    test_url = input("输入测试URL（回车使用默认）: ").strip()
    if not test_url:
        test_url = "https://www.hollandandbarrett.com/shop/vitamins-supplements/condition/hair-skin-nails/"

    # 测试产品数量
    try:
        test_size = int(input("每次测试的产品数量 (默认10): ").strip() or "10")
    except ValueError:
        test_size = 10

    print(f"\n正在获取测试产品列表...")

    # 获取产品列表
    driver = create_test_driver()
    try:
        from main import scrape_product_list
        products = scrape_product_list(driver, test_url)

        if len(products) < test_size:
            print(f"⚠️  只找到 {len(products)} 个产品，将使用全部")
            test_size = len(products)

        print(f"✓ 获取到 {len(products)} 个产品，将测试前 {test_size} 个\n")

    except Exception as e:
        print(f"✗ 获取产品列表失败: {e}")
        return
    finally:
        driver.quit()

    # 要测试的线程数
    thread_counts = [2, 3, 5, 8]

    # 询问是否测试更多
    print(f"默认测试线程数: {thread_counts}")
    custom = input("是否测试更多线程？输入线程数（如 10,12），回车跳过: ").strip()
    if custom:
        try:
            additional = [int(x.strip()) for x in custom.split(',')]
            thread_counts.extend(additional)
            thread_counts = sorted(set(thread_counts))
        except:
            print("输入格式错误，使用默认配置")

    print(f"\n将测试以下线程数: {thread_counts}\n")
    time.sleep(2)

    # 执行测试
    results = []
    for thread_count in thread_counts:
        try:
            result = test_thread_count(products, thread_count, test_size)
            results.append(result)

            # 测试之间稍作休息
            if thread_count != thread_counts[-1]:
                print(f"\n等待5秒后继续下一个测试...")
                time.sleep(5)

        except KeyboardInterrupt:
            print("\n\n用户中断测试")
            break
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            continue

    if not results:
        print("\n没有完成任何测试")
        return

    # 分析结果
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)

    print(f"\n{'线程数':<8} {'总耗时':<10} {'平均速度':<12} {'成功率':<10} {'吞吐量':<12}")
    print("-" * 70)

    for r in results:
        print(f"{r['threads']:<8} "
              f"{r['total_time']:<10.1f} "
              f"{r['avg_time']:<12.2f} "
              f"{r['success_rate']:<10.1f}% "
              f"{r['products_per_second']:<12.2f}")

    # 推荐最佳配置
    print("\n" + "=" * 70)
    print("推荐配置")
    print("=" * 70)

    # 找到成功率 >= 80% 中最快的
    valid_results = [r for r in results if r['success_rate'] >= 80]

    if valid_results:
        fastest = min(valid_results, key=lambda x: x['avg_time'])
        print(f"\n🏆 最佳配置（速度优先，成功率>=80%）:")
        print(f"   线程数: {fastest['threads']}")
        print(f"   平均速度: {fastest['avg_time']:.2f}秒/产品")
        print(f"   成功率: {fastest['success_rate']:.1f}%")

        # 找到成功率最高的
        most_stable = max(results, key=lambda x: x['success_rate'])
        if most_stable != fastest:
            print(f"\n🛡️  最稳定配置（成功率优先）:")
            print(f"   线程数: {most_stable['threads']}")
            print(f"   平均速度: {most_stable['avg_time']:.2f}秒/产品")
            print(f"   成功率: {most_stable['success_rate']:.1f}%")
    else:
        print("\n⚠️  所有测试的成功率都低于80%，建议:")
        print("   1. 减少并发线程数")
        print("   2. 增加请求延迟")
        print("   3. 检查网络连接")

    # 保存结果
    output_file = project_root / "data" / "output" / "thread_test_results.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'threads', 'total_time', 'avg_time', 'success_count',
            'success_rate', 'products_per_second'
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ 详细结果已保存到: {output_file}")


if __name__ == "__main__":
    main()

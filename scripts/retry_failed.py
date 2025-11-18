#!/usr/bin/env python3
"""
重新爬取失败的产品

使用方法:
    uv run python scripts/retry_failed.py

功能:
    - 读取失败记录文件
    - 显示失败产品列表
    - 重新爬取失败的产品
    - 更新失败记录
"""

import sys
import json
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.parallel_scraper import scrape_details_parallel
from main import scrape_product_detail
from utils.logger import get_logger


def load_failed_products():
    """加载失败的产品记录"""
    failed_file = project_root / "data" / "output" / "failed_products.json"

    if not failed_file.exists():
        print("✓ 没有失败的产品记录")
        return []

    with open(failed_file, 'r', encoding='utf-8') as f:
        failed_products = json.load(f)

    return failed_products


def show_failed_summary(failed_products):
    """显示失败产品摘要"""
    if not failed_products:
        return

    print(f"\n{'=' * 70}")
    print(f"失败产品列表 (共 {len(failed_products)} 个)")
    print(f"{'=' * 70}\n")

    # 按时间分组统计
    from collections import defaultdict
    by_date = defaultdict(list)
    for item in failed_products:
        timestamp = item.get('timestamp', '')
        date = timestamp.split('T')[0] if 'T' in timestamp else '未知日期'
        by_date[date].append(item)

    for date, items in sorted(by_date.items(), reverse=True):
        print(f"{date}: {len(items)} 个失败")

    print(f"\n{'=' * 70}")
    print("失败原因统计:")
    print(f"{'=' * 70}\n")

    # 统计失败原因
    error_types = defaultdict(int)
    for item in failed_products:
        error = item.get('error', 'Unknown')
        # 简化错误信息
        if 'Could not reach host' in error:
            error_type = '网络连接失败'
        elif '未找到__LAYOUT__数据' in error:
            error_type = '页面数据提取失败'
        elif 'timeout' in error.lower():
            error_type = '超时'
        else:
            error_type = error[:50]
        error_types[error_type] += 1

    for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {error_type}: {count} 个")


def retry_failed_products(failed_products, max_workers=3):
    """重新爬取失败的产品"""
    logger = get_logger()

    # 提取产品数据
    products_to_retry = [item['item_data'] for item in failed_products]

    logger.info(f"\n开始重新爬取 {len(products_to_retry)} 个失败的产品...")

    # 使用并行爬取
    results = scrape_details_parallel(
        products=products_to_retry,
        scrape_detail_func=scrape_product_detail,
        max_workers=max_workers,
        retry_times=5,  # 增加重试次数
        request_delay=(3, 6),  # 增加延迟，提高成功率
        enable_headless=True
    )

    # 检查哪些成功了
    success_count = 0
    still_failed = []

    for i, result in enumerate(results):
        original = products_to_retry[i]
        # 检查是否成功获取到详情
        if any(key in result for key in ['highlights', 'description', 'directions']):
            success_count += 1
        else:
            # 仍然失败，保留记录
            still_failed.append(failed_products[i])

    logger.info(
        f"\n重爬结果:\n"
        f"  - 成功: {success_count}/{len(products_to_retry)}\n"
        f"  - 仍失败: {len(still_failed)}/{len(products_to_retry)}"
    )

    # 更新失败记录文件
    failed_file = project_root / "data" / "output" / "failed_products.json"
    if still_failed:
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(still_failed, f, ensure_ascii=False, indent=2)
        logger.info(f"\n更新失败记录: {len(still_failed)} 个产品仍未成功")
    else:
        # 全部成功，删除失败记录文件
        failed_file.unlink()
        logger.info(f"\n🎉 所有产品都已成功爬取！失败记录已清空")

    return results, success_count


def main():
    print("=" * 70)
    print("失败产品重爬工具")
    print("=" * 70)

    # 加载失败记录
    failed_products = load_failed_products()

    if not failed_products:
        print("\n✓ 没有需要重爬的产品")
        return

    # 显示失败摘要
    show_failed_summary(failed_products)

    # 询问是否重爬
    print(f"\n{'=' * 70}")
    response = input(f"是否重新爬取这 {len(failed_products)} 个失败的产品？(y/n): ").strip().lower()

    if response != 'y':
        print("取消操作")
        return

    # 询问线程数
    print("\n提示: 建议使用较少的线程数和较长的延迟来提高成功率")
    try:
        workers = input("并发线程数 (建议2-3, 默认2): ").strip() or "2"
        max_workers = min(max(int(workers), 1), 5)
    except ValueError:
        max_workers = 2

    # 重新爬取
    results, success_count = retry_failed_products(failed_products, max_workers)

    # 保存成功的结果
    if success_count > 0:
        print(f"\n{'=' * 70}")
        save_option = input("是否将成功爬取的产品保存到CSV？(y/n): ").strip().lower()

        if save_option == 'y':
            import csv
            output_file = project_root / "data" / "output" / "retry_success.csv"

            fieldnames = [
                "产品名称", "产品亮点", "产品价格", "产品品牌",
                "产品图", "产品描述", "产品类型", "作用部位",
                "用法说明", "营养成分", "配料表", "URL"
            ]

            with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for product in results:
                    # 只保存成功的
                    if any(key in product for key in ['highlights', 'description', 'directions']):
                        row = {
                            "产品名称": product.get("name", ""),
                            "产品价格": product.get("price", ""),
                            "产品亮点": product.get("highlights", ""),
                            "用法说明": product.get("directions", ""),
                            "产品图": product.get("image", ""),
                            "产品类型": "",
                            "作用部位": product.get("target_area", ""),
                            "配料表": product.get("ingredients", ""),
                            "产品品牌": product.get("brand", ""),
                            "产品描述": product.get("description", ""),
                            "营养成分": product.get("nutritional_info", ""),
                            "URL": product.get("url", ""),
                        }
                        writer.writerow(row)

            print(f"✓ 成功产品已保存到: {output_file}")

    print(f"\n{'=' * 70}")
    print("完成!")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()

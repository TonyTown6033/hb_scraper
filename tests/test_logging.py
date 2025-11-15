"""测试日志系统"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import setup_logger, get_logger
import logging


def test_basic_logging():
    """测试基本日志功能"""
    print("\n" + "=" * 80)
    print("测试 1: 基本日志功能")
    print("=" * 80 + "\n")

    # 设置日志
    logger_manager = setup_logger(
        name="test_scraper",
        log_dir="logs",
        console_level=logging.DEBUG,  # 控制台显示所有级别
        enable_color=True
    )

    logger = get_logger()

    # 测试不同级别
    logger.debug("这是一条调试信息 - 用于开发调试")
    logger.info("这是一条普通信息 - 记录正常流程")
    logger.warning("这是一条警告信息 - 需要注意但不影响运行")
    logger.error("这是一条错误信息 - 发生了错误但可以继续")
    logger.critical("这是一条严重错误 - 系统可能无法继续")

    print("\n✓ 基本日志测试完成")
    print(f"📁 日志文件位置: logs/test_scraper.log")


def test_exception_logging():
    """测试异常日志"""
    print("\n" + "=" * 80)
    print("测试 2: 异常日志记录")
    print("=" * 80 + "\n")

    logger = get_logger()

    try:
        # 故意触发异常
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.exception("捕获到除零异常，包含完整堆栈信息")

    try:
        # 另一个异常
        data = {'name': 'test'}
        value = data['missing_key']
    except KeyError as e:
        logger.exception(f"键不存在: {e}")

    print("\n✓ 异常日志测试完成")
    print("💡 异常信息包含完整的堆栈跟踪，方便调试")


def test_scraper_workflow():
    """模拟爬虫工作流程"""
    print("\n" + "=" * 80)
    print("测试 3: 模拟爬虫工作流程")
    print("=" * 80 + "\n")

    logger = get_logger()

    # 模拟爬虫流程
    logger.info("=" * 60)
    logger.info("开始爬取产品数据")
    logger.info("=" * 60)

    logger.debug("初始化浏览器驱动...")
    logger.info("✓ 浏览器已启动")

    url = "https://example.com/products"
    logger.info(f"访问页面: {url}")
    logger.debug(f"当前 User-Agent: Mozilla/5.0...")

    logger.info("✓ 页面加载完成")
    logger.debug("等待 Cookie 弹窗...")

    logger.info("✓ 已接受 Cookie")
    logger.info("✓ 找到 20 个产品")

    # 模拟提取产品
    for i in range(1, 4):
        logger.debug(f"提取产品 {i}...")

        if i == 2:
            logger.warning(f"产品 {i} 缺少价格信息")

        logger.debug(f"✓ 产品 {i} 提取完成")

    logger.info("=" * 60)
    logger.info("爬取完成！共 20 个产品")
    logger.info("=" * 60)

    print("\n✓ 工作流程测试完成")


def test_structured_data():
    """测试结构化数据日志"""
    print("\n" + "=" * 80)
    print("测试 4: 结构化数据日志")
    print("=" * 80 + "\n")

    logger = get_logger()

    # 记录产品数据
    product = {
        "name": "Vitamin C 1000mg",
        "price": "£12.99",
        "brand": "Holland & Barrett",
        "url": "https://..."
    }

    logger.info(f"提取产品: {product['name']}")
    logger.debug(f"产品详情: {product}")

    # 记录统计信息
    stats = {
        "total_products": 20,
        "successful": 18,
        "failed": 2,
        "duration": "3.5s"
    }

    logger.info(f"爬取统计: 成功 {stats['successful']}/{stats['total_products']}")
    logger.debug(f"完整统计: {stats}")

    print("\n✓ 结构化数据测试完成")


def show_log_files():
    """显示生成的日志文件"""
    print("\n" + "=" * 80)
    print("生成的日志文件")
    print("=" * 80 + "\n")

    log_dir = Path("logs")
    if not log_dir.exists():
        print("日志目录不存在")
        return

    log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)

    for log_file in log_files[:5]:  # 只显示最新的5个
        size_kb = log_file.stat().st_size / 1024
        print(f"📄 {log_file.name:<40} ({size_kb:.2f} KB)")

    print(f"\n💡 使用 'python scripts/view_logs.py' 查看日志详情")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("日志系统测试")
    print("=" * 80)

    # 运行所有测试
    test_basic_logging()
    test_exception_logging()
    test_scraper_workflow()
    test_structured_data()
    show_log_files()

    print("\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)
    print("\n下一步:")
    print("  1. 查看日志文件: python scripts/view_logs.py list")
    print("  2. 查看最新日志: python scripts/view_logs.py view")
    print("  3. 搜索日志: python scripts/view_logs.py search -k '关键词'")
    print("  4. 实时跟踪: python scripts/view_logs.py tail")
    print("\n")

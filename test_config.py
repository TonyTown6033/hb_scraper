"""测试配置文件加载"""

import config
from pathlib import Path


def test_config():
    """测试配置是否正确加载"""
    print("=" * 60)
    print("配置文件加载测试")
    print("=" * 60)

    # 测试目录配置
    print("\n【目录配置】")
    print(f"项目根目录: {config.PROJECT_ROOT}")
    print(f"数据目录: {config.DATA_DIR}")
    print(f"输出目录: {config.OUTPUT_DIR}")
    print(f"输入目录: {config.INPUT_DIR}")
    print(f"日志目录: {config.LOGS_DIR}")

    # 测试URL配置
    print("\n【爬虫URL配置】")
    print(f"默认分类URL: {config.DEFAULT_CATEGORY_URL}")
    product_type = config.get_product_type_from_url(config.DEFAULT_CATEGORY_URL)
    print(f"产品类型: {product_type}")

    # 测试输出文件配置
    print("\n【输出文件配置】")
    print(f"基本信息输出: {config.OUTPUT_BASIC_CSV}")
    print(f"完整信息输出: {config.OUTPUT_COMPLETE_CSV}")
    print(f"失败记录输出: {config.OUTPUT_FAILED_JSON}")
    multipage_output = config.get_output_path(product_type=product_type, output_type='multipage')
    print(f"多页爬取输出: {multipage_output}")

    # 测试CSV字段配置
    print("\n【CSV字段配置】")
    print(f"基本字段: {config.CSV_FIELDNAMES_BASIC}")
    print(f"完整字段数量: {len(config.CSV_FIELDNAMES_COMPLETE)}")

    # 测试Chrome配置
    print("\n【Chrome浏览器配置】")
    print(f"User-Agent: {config.CHROME_USER_AGENT[:50]}...")
    print(f"Headless模式: {config.CHROME_HEADLESS}")
    print(f"页面加载策略: {config.CHROME_PAGE_LOAD_STRATEGY}")
    print(f"Chrome选项数量: {len(config.CHROME_OPTIONS)}")

    # 测试爬虫行为配置
    print("\n【爬虫行为配置】")
    print(f"页面加载超时: {config.PAGE_LOAD_TIMEOUT}秒")
    print(f"脚本执行超时: {config.SCRIPT_TIMEOUT}秒")
    print(f"页面等待时间: {config.PAGE_WAIT_TIME}秒")
    print(f"Cookie超时: {config.COOKIE_TIMEOUT}秒")
    print(f"Cookie选择器数量: {len(config.COOKIE_SELECTORS)}")

    # 测试并行配置
    print("\n【并行爬取配置】")
    print(f"默认并发数: {config.DEFAULT_MAX_WORKERS}")
    print(f"最大并发限制: {config.MAX_WORKERS_LIMIT}")
    print(f"重试次数: {config.RETRY_TIMES}")
    print(f"请求延迟: {config.REQUEST_DELAY_MIN}-{config.REQUEST_DELAY_MAX}秒")
    print(f"批次大小: {config.BATCH_SIZE}")

    # 测试多页配置
    print("\n【多页爬取配置】")
    print(f"默认最大页数: {config.DEFAULT_MAX_PAGES or '不限制'}")
    print(f"启用断点续传: {config.ENABLE_RESUME}")

    # 测试选择器配置
    print("\n【产品选择器配置】")
    print(f"产品卡片选择器: {config.PRODUCT_CARD_SELECTOR}")
    print(f"品牌选择器: {config.BRAND_SELECTOR}")
    print(f"标题选择器: {config.TITLE_SELECTOR}")
    print(f"价格选择器: {config.PRICE_SELECTOR}")
    print(f"图片选择器: {config.IMAGE_SELECTOR}")

    # 测试辅助函数
    print("\n【辅助函数测试】")
    try:
        chrome_options = config.get_chrome_options()
        print(f"✓ get_chrome_options() 成功")
        print(f"  - ChromeOptions类型: {type(chrome_options).__name__}")
    except Exception as e:
        print(f"✗ get_chrome_options() 失败: {e}")

    try:
        basic_path = config.get_output_path(output_type='basic')
        complete_path = config.get_output_path(output_type='complete')
        failed_path = config.get_output_path(output_type='failed')
        print(f"✓ get_output_path() 成功")
    except Exception as e:
        print(f"✗ get_output_path() 失败: {e}")

    # 目录检查
    print("\n【目录检查】")
    dirs_to_check = [
        config.OUTPUT_DIR,
        config.INPUT_DIR,
        config.LOGS_DIR,
    ]
    for dir_path in dirs_to_check:
        if dir_path.exists():
            print(f"✓ {dir_path.name}/ 目录存在")
        else:
            print(f"✗ {dir_path.name}/ 目录不存在")

    print("\n" + "=" * 60)
    print("✓ 配置文件加载测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_config()

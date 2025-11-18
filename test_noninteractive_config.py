"""测试非交互式模式配置"""

import config


def test_noninteractive_config():
    """测试非交互式模式的所有配置项"""
    print("=" * 60)
    print("非交互式模式配置测试")
    print("=" * 60)

    print("\n【交互式模式控制】")
    print(f"交互式模式: {config.INTERACTIVE_MODE}")
    print(f"  → {'启用' if config.INTERACTIVE_MODE else '禁用'}交互式询问")

    print("\n【爬取模式配置】")
    print(f"爬取模式: {config.SCRAPE_MODE}")
    mode_desc = {
        1: "单页模式（仅第一页）",
        2: "多页模式（所有页面）",
        3: "限制页数模式"
    }
    print(f"  → {mode_desc.get(config.SCRAPE_MODE, '未知')}")
    if config.SCRAPE_MODE == 3:
        print(f"  → 最大页数限制: {config.MAX_PAGES_LIMIT}页")

    print("\n【详情页配置】")
    print(f"爬取详情页: {config.SCRAPE_DETAILS}")
    print(f"  → {'是' if config.SCRAPE_DETAILS else '否'}爬取产品详情")
    if config.SCRAPE_DETAILS:
        if config.MAX_PRODUCTS_TO_SCRAPE:
            print(f"  → 最多爬取: {config.MAX_PRODUCTS_TO_SCRAPE}个产品")
        else:
            print(f"  → 爬取全部产品")
        mode_name = "并行模式" if config.DETAIL_SCRAPE_MODE == 2 else "顺序模式"
        print(f"  → 详情爬取模式: {mode_name}")
        if config.DETAIL_SCRAPE_MODE == 2:
            print(f"  → 并发线程数: {config.DEFAULT_MAX_WORKERS}")

    print("\n【断点续传配置】")
    print(f"启用断点续传: {config.ENABLE_RESUME}")
    if config.ENABLE_RESUME:
        print(f"自动继续: {config.AUTO_RESUME}")
        print(f"  → 发现进度时{'自动继续' if config.AUTO_RESUME else '询问用户'}")

    print("\n【后处理配置】")
    print(f"运行翻译: {config.RUN_TRANSLATION}")
    print(f"  → {'是' if config.RUN_TRANSLATION else '否'}自动翻译")
    print(f"运行图片处理: {config.RUN_IMAGE_PROCESSING}")
    print(f"  → {'是' if config.RUN_IMAGE_PROCESSING else '否'}自动处理图片")

    print("\n【并发性能配置】")
    print(f"默认并发数: {config.DEFAULT_MAX_WORKERS}")
    print(f"最大并发限制: {config.MAX_WORKERS_LIMIT}")
    print(f"请求延迟范围: {config.REQUEST_DELAY_MIN}-{config.REQUEST_DELAY_MAX}秒")

    print("\n" + "=" * 60)
    print("✓ 非交互式配置测试完成！")
    print("=" * 60)

    # 总结
    print("\n【运行行为总结】")
    if config.INTERACTIVE_MODE:
        print("✓ 交互式模式：运行时会询问用户选择")
    else:
        print("✓ 非交互式模式：使用配置文件自动运行")
        print(f"\n预期行为：")
        print(f"  1. 爬取模式: {mode_desc.get(config.SCRAPE_MODE)}")
        if config.SCRAPE_MODE == 3:
            print(f"     - 限制{config.MAX_PAGES_LIMIT}页")
        print(f"  2. 详情页: {'爬取' if config.SCRAPE_DETAILS else '跳过'}")
        if config.SCRAPE_DETAILS:
            products = config.MAX_PRODUCTS_TO_SCRAPE or "全部"
            print(f"     - 产品数: {products}")
            print(f"     - 模式: {mode_name}")
            print(f"     - 线程数: {config.DEFAULT_MAX_WORKERS}")
        if config.ENABLE_RESUME:
            print(f"  3. 断点续传: {'自动继续' if config.AUTO_RESUME else '重新开始'}")
        print(f"  4. 翻译: {'运行' if config.RUN_TRANSLATION else '跳过'}")
        print(f"  5. 图片处理: {'运行' if config.RUN_IMAGE_PROCESSING else '跳过'}")


if __name__ == "__main__":
    test_noninteractive_config()

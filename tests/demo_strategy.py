"""演示不同宽高比图片的处理策略对比"""


def compare_strategies(original_width, original_height, name=""):
    """对比新旧策略"""
    target_width, target_height = 800, 800

    print(f"\n{'=' * 70}")
    print(f"测试场景: {name}")
    print(f"{'=' * 70}")
    print(f"原始尺寸: {original_width}x{original_height}")
    print(f"宽高比: {original_width / original_height:.2f} {'(竖长图)' if original_width < original_height else '(横图)' if original_width > original_height else '(正方形)'}")

    # 旧策略
    scale_old = min(target_width / original_width, target_height / original_height)
    new_width_old = int(original_width * scale_old)
    new_height_old = int(original_height * scale_old)

    # 新策略
    aspect_ratio = original_width / original_height
    if aspect_ratio < 1:  # 竖长图片
        scale_new = target_width / original_width
        if original_height * scale_new > target_height:
            scale_new = target_height / original_height
    else:
        scale_new = min(target_width / original_width, target_height / original_height)

    new_width_new = int(original_width * scale_new)
    new_height_new = int(original_height * scale_new)

    print(f"\n【旧策略】")
    print(f"  缩放后: {new_width_old}x{new_height_old}")
    print(f"  左右留白: {(target_width - new_width_old) / 2:.0f}px × 2 = {target_width - new_width_old}px")
    print(f"  上下留白: {(target_height - new_height_old) / 2:.0f}px × 2 = {target_height - new_height_old}px")
    print(f"  图片占比: {(new_width_old * new_height_old) / (target_width * target_height) * 100:.1f}%")

    print(f"\n【新策略】智能优化")
    print(f"  缩放后: {new_width_new}x{new_height_new}")
    print(f"  左右留白: {(target_width - new_width_new) / 2:.0f}px × 2 = {target_width - new_width_new}px")
    print(f"  上下留白: {(target_height - new_height_new) / 2:.0f}px × 2 = {target_height - new_height_new}px")
    print(f"  图片占比: {(new_width_new * new_height_new) / (target_width * target_height) * 100:.1f}%")

    if new_width_new != new_width_old or new_height_new != new_height_old:
        improvement = ((new_width_new * new_height_new) - (new_width_old * new_height_old)) / (
            new_width_old * new_height_old
        ) * 100
        print(f"\n✓ 优化效果:")
        print(f"  • 图片面积增加: {improvement:.1f}%")
        print(f"  • 左右留白减少: {(target_width - new_width_old) - (target_width - new_width_new):.0f}px")
    else:
        print(f"\n→ 此场景下两种策略相同")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("图片处理策略对比演示")
    print("目标尺寸: 800x800")
    print("=" * 70)

    # 测试场景1：典型药品瓶子（竖长）
    compare_strategies(300, 600, "典型药品瓶子 (1:2)")

    # 测试场景2：更窄的瓶子
    compare_strategies(200, 600, "窄瓶子 (1:3)")

    # 测试场景3：正方形包装
    compare_strategies(400, 400, "正方形包装 (1:1)")

    # 测试场景4：横向包装盒
    compare_strategies(600, 300, "横向包装盒 (2:1)")

    # 测试场景5：极窄瓶子
    compare_strategies(150, 600, "极窄瓶子 (1:4)")

    print("\n" + "=" * 70)
    print("总结:")
    print("=" * 70)
    print("新策略对竖长图片（药品瓶子）进行了优化：")
    print("• 优先填充宽度到800px，让产品更大更清晰")
    print("• 减少左右留白，提高空间利用率")
    print("• 对正方形和横图保持原有策略不变")
    print("=" * 70)

"""演示 800x400 横条形尺寸的效果"""


def demo_size(original_width, original_height, name=""):
    """演示不同尺寸的效果"""
    print(f"\n{'=' * 70}")
    print(f"产品: {name}")
    print(f"{'=' * 70}")
    print(f"原始尺寸: {original_width}x{original_height}")

    aspect_ratio = original_width / original_height
    print(f"宽高比: {aspect_ratio:.2f} ", end="")
    if aspect_ratio < 0.8:
        print("(竖长图 - 典型瓶子)")
    elif aspect_ratio > 1.2:
        print("(横图)")
    else:
        print("(近似方形)")

    # 800x800 正方形
    target_800x800 = (800, 800)
    scale_800 = min(target_800x800[0] / original_width, target_800x800[1] / original_height)
    w_800 = int(original_width * scale_800)
    h_800 = int(original_height * scale_800)

    # 800x400 横条形
    target_800x400 = (800, 400)
    scale_400 = min(target_800x400[0] / original_width, target_800x400[1] / original_height)
    w_400 = int(original_width * scale_400)
    h_400 = int(original_height * scale_400)

    print(f"\n【800x800 正方形】")
    print(f"  缩放后: {w_800}x{h_800}")
    print(f"  左右留白: {800 - w_800}px (每边 {(800 - w_800) / 2:.0f}px)")
    print(f"  上下留白: {800 - h_800}px (每边 {(800 - h_800) / 2:.0f}px)")
    print(f"  图片占比: {(w_800 * h_800) / (800 * 800) * 100:.1f}%")

    print(f"\n【800x400 横条形】✨ 新方案")
    print(f"  缩放后: {w_400}x{h_400}")
    print(f"  左右留白: {800 - w_400}px (每边 {(800 - w_400) / 2:.0f}px)")
    print(f"  上下留白: {400 - h_400}px (每边 {(400 - h_400) / 2:.0f}px)")
    print(f"  图片占比: {(w_400 * h_400) / (800 * 400) * 100:.1f}%")

    # 对比
    if aspect_ratio < 0.8:  # 竖长图
        print(f"\n✓ 优化效果（针对竖长瓶子）:")
        print(f"  • 上下留白大幅减少: {800 - h_800}px → {400 - h_400}px")
        print(f"  • 左右留白略增: {800 - w_800}px → {800 - w_400}px")
        print(f"  • 产品在画面中更突出，视觉更聚焦")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("800x400 横条形尺寸优化方案")
    print("=" * 70)

    # 测试场景
    demo_size(250, 250, "正方形产品 (250x250)")
    demo_size(300, 600, "典型瓶子 (300x600 - 1:2)")
    demo_size(200, 600, "细长瓶子 (200x600 - 1:3)")
    demo_size(600, 300, "横向盒装 (600x300 - 2:1)")

    print("\n" + "=" * 70)
    print("总结:")
    print("=" * 70)
    print("✓ 800x400 横条形设计的优势：")
    print("  1. 竖长瓶子上下留白大幅减少，产品更突出")
    print("  2. 视觉聚焦在产品本身，不会被大片空白分散注意力")
    print("  3. 适合电商列表展示，占用空间更合理")
    print("  4. 对正方形和横图也能良好适配")
    print("=" * 70)

"""测试新旧图片处理策略的对比"""
import httpx
from PIL import Image
from io import BytesIO


def test_strategies():
    """对比新旧策略"""
    # 测试图片URL（药品瓶子 - 竖长图）
    # 使用第二个产品的图片
    test_url = "https://images.hollandandbarrettimages.co.uk/productimages/HB/250/079720_A.png"

    print("下载测试图片...")
    with httpx.Client(timeout=30.0) as client:
        response = client.get(test_url)
        image_data = response.content

    img = Image.open(BytesIO(image_data))
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    original_width, original_height = img.size
    target_width, target_height = 800, 800

    print(f"\n原始图片尺寸: {original_width}x{original_height}")
    print(f"宽高比: {original_width / original_height:.2f}")
    print(f"目标尺寸: {target_width}x{target_height}")

    # 旧策略：统一缩放
    print("\n" + "=" * 60)
    print("【旧策略】统一缩放")
    print("=" * 60)
    scale_old = min(target_width / original_width, target_height / original_height)
    new_width_old = int(original_width * scale_old)
    new_height_old = int(original_height * scale_old)
    print(f"缩放比例: {scale_old:.3f}")
    print(f"缩放后尺寸: {new_width_old}x{new_height_old}")
    print(f"左右留白: {(target_width - new_width_old) / 2:.1f}px 每边")
    print(f"上下留白: {(target_height - new_height_old) / 2:.1f}px 每边")
    print(f"图片占比: {(new_width_old * new_height_old) / (target_width * target_height) * 100:.1f}%")

    # 新策略：智能缩放
    print("\n" + "=" * 60)
    print("【新策略】智能缩放（竖图优先填充宽度）")
    print("=" * 60)
    aspect_ratio = original_width / original_height

    if aspect_ratio < 1:  # 竖长图片
        scale_new = target_width / original_width
        if original_height * scale_new > target_height:
            scale_new = target_height / original_height
    else:
        scale_new = min(target_width / original_width, target_height / original_height)

    new_width_new = int(original_width * scale_new)
    new_height_new = int(original_height * scale_new)
    print(f"缩放比例: {scale_new:.3f}")
    print(f"缩放后尺寸: {new_width_new}x{new_height_new}")
    print(f"左右留白: {(target_width - new_width_new) / 2:.1f}px 每边")
    print(f"上下留白: {(target_height - new_height_new) / 2:.1f}px 每边")
    print(f"图片占比: {(new_width_new * new_height_new) / (target_width * target_height) * 100:.1f}%")

    # 对比
    print("\n" + "=" * 60)
    print("【对比结果】")
    print("=" * 60)
    improvement = ((new_width_new * new_height_new) - (new_width_old * new_height_old)) / (
        new_width_old * new_height_old
    ) * 100
    print(f"图片面积增加: {improvement:.1f}%")
    print(f"左右留白减少: {((target_width - new_width_old) - (target_width - new_width_new)):.1f}px")


if __name__ == "__main__":
    test_strategies()

"""本地测试 800x400 处理效果"""
from PIL import Image
from io import BytesIO
import httpx


def create_test_image():
    """创建一个模拟的竖长药品瓶子图片"""
    # 创建一个 300x600 的测试图片（模拟药品瓶子）
    img = Image.new("RGB", (300, 600), color=(100, 150, 200))

    # 添加一些细节让它看起来像个瓶子
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    # 瓶身
    draw.rectangle([50, 100, 250, 500], fill=(150, 180, 220), outline=(50, 80, 120))
    # 瓶盖
    draw.rectangle([100, 50, 200, 100], fill=(180, 200, 230), outline=(50, 80, 120))
    # 标签
    draw.rectangle([80, 250, 220, 350], fill=(255, 255, 255), outline=(100, 100, 100))

    return img


def process_to_800x400(img):
    """处理图片到 800x400"""
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    original_width, original_height = img.size
    target_width, target_height = 800, 400

    # 等比例缩放
    scale = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    # 缩放图片
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 创建白色背景
    background = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # 居中粘贴
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2
    background.paste(img_resized, (x, y), img_resized)

    return background, new_width, new_height


def process_to_800x800(img):
    """处理图片到 800x800 (对比)"""
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    original_width, original_height = img.size
    target_width, target_height = 800, 800

    # 等比例缩放
    scale = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    # 缩放图片
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 创建白色背景
    background = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # 居中粘贴
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2
    background.paste(img_resized, (x, y), img_resized)

    return background, new_width, new_height


if __name__ == "__main__":
    print("创建测试图片（模拟药品瓶子 300x600）...")
    test_img = create_test_image()

    print("\n处理为 800x800 正方形...")
    img_800x800, w1, h1 = process_to_800x800(test_img)
    img_800x800.save("/tmp/test_800x800.png")
    print(f"  保存到: /tmp/test_800x800.png")
    print(f"  实际图片尺寸: {w1}x{h1}")
    print(f"  左右留白: {800 - w1}px")
    print(f"  上下留白: {800 - h1}px")

    print("\n处理为 800x400 横条形...")
    img_800x400, w2, h2 = process_to_800x400(test_img)
    img_800x400.save("/tmp/test_800x400.png")
    print(f"  保存到: /tmp/test_800x400.png")
    print(f"  实际图片尺寸: {w2}x{h2}")
    print(f"  左右留白: {800 - w2}px")
    print(f"  上下留白: {400 - h2}px")

    print("\n✓ 测试图片已生成，可以查看对比效果")
    print("  打开 /tmp/test_800x800.png 和 /tmp/test_800x400.png 对比")

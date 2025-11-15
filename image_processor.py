"""图片处理和上传工具"""
import httpx
from PIL import Image
from io import BytesIO
from pathlib import Path
from typing import Optional
import time


class ImageProcessor:
    """图片处理器：下载、居中处理、上传到图床"""

    def __init__(self, api_url: str, token: str, target_size: tuple = (800, 800)):
        """
        初始化图片处理器

        Args:
            api_url: EasyImage API 地址
            token: API token
            target_size: 目标尺寸，默认 (800, 800)
        """
        self.api_url = api_url
        self.token = token
        self.target_size = target_size
        self.client = httpx.Client(timeout=60.0)

    def download_image(self, url: str) -> Optional[bytes]:
        """
        下载图片

        Args:
            url: 图片URL

        Returns:
            图片字节数据，失败返回 None
        """
        try:
            response = self.client.get(url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"  ✗ 下载失败 (状态码: {response.status_code}): {url}")
                return None
        except Exception as e:
            print(f"  ✗ 下载出错: {e}")
            return None

    def process_image(self, image_data: bytes) -> Optional[bytes]:
        """
        处理图片：调整尺寸并居中到白色背景

        Args:
            image_data: 原始图片字节数据

        Returns:
            处理后的图片字节数据（PNG格式），失败返回 None
        """
        try:
            # 打开图片
            img = Image.open(BytesIO(image_data))

            # 转换为 RGBA 模式（支持透明度）
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # 计算缩放比例（保持宽高比）
            original_width, original_height = img.size
            target_width, target_height = self.target_size

            # 计算缩放比例，使图片能够完全放入目标尺寸
            scale = min(target_width / original_width, target_height / original_height)

            # 计算新尺寸
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            # 缩放图片（使用高质量抗锯齿）
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 创建白色背景
            background = Image.new("RGB", self.target_size, (255, 255, 255))

            # 计算居中位置
            x = (target_width - new_width) // 2
            y = (target_height - new_height) // 2

            # 将缩放后的图片粘贴到白色背景上（处理透明度）
            background.paste(img_resized, (x, y), img_resized)

            # 转换为字节数据
            output = BytesIO()
            background.save(output, format="PNG", quality=95)
            return output.getvalue()

        except Exception as e:
            print(f"  ✗ 图片处理出错: {e}")
            return None

    def upload_to_imagebed(self, image_data: bytes, filename: str = "product.png") -> Optional[str]:
        """
        上传图片到 EasyImage 图床

        Args:
            image_data: 图片字节数据
            filename: 文件名

        Returns:
            上传后的图片URL，失败返回 None
        """
        try:
            files = {"image": (filename, image_data, "image/png")}
            data = {"token": self.token}

            response = self.client.post(self.api_url, files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                if result.get("result") == "success":
                    return result.get("url")
                else:
                    print(f"  ✗ 上传失败: {result.get('message', '未知错误')}")
                    return None
            else:
                print(f"  ✗ 上传失败 (状态码: {response.status_code})")
                return None

        except Exception as e:
            print(f"  ✗ 上传出错: {e}")
            return None

    def process_and_upload(self, image_url: str, product_name: str = "") -> Optional[str]:
        """
        完整流程：下载 -> 处理 -> 上传

        Args:
            image_url: 原始图片URL
            product_name: 产品名称（用于日志）

        Returns:
            新的图片URL，失败返回 None
        """
        if not image_url or image_url.strip() == "":
            print(f"  → 跳过：无图片URL")
            return None

        # 下载图片
        image_data = self.download_image(image_url)
        if not image_data:
            return None

        # 处理图片
        processed_data = self.process_image(image_data)
        if not processed_data:
            return None

        # 生成文件名
        filename = f"{product_name[:30].replace(' ', '_')}.png" if product_name else "product.png"

        # 上传到图床
        new_url = self.upload_to_imagebed(processed_data, filename)

        # 延迟一下，避免请求过快
        time.sleep(0.5)

        return new_url

    def close(self):
        """关闭 HTTP 客户端"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 测试代码
if __name__ == "__main__":
    # 配置
    API_URL = "http://81.68.170.234/api/index.php"
    TOKEN = "1c17b11693cb5ec63859b091c5b9c1b2"

    # 测试图片
    test_url = "https://images.hollandandbarrettimages.co.uk/productimages/HB/250/084867_A.png"

    print("开始测试图片处理和上传...")
    print("=" * 60)

    with ImageProcessor(API_URL, TOKEN) as processor:
        new_url = processor.process_and_upload(test_url, "Test_Product")

        if new_url:
            print(f"\n✓ 完成！")
            print(f"原始URL: {test_url}")
            print(f"新URL:   {new_url}")
        else:
            print("\n✗ 处理失败")

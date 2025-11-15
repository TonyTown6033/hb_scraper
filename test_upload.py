"""测试 EasyImage 图床上传功能"""
import httpx
from pathlib import Path


def test_easyimage_upload():
    """测试 EasyImage API 上传"""
    api_url = "http://81.68.170.234/api/index.php"
    token = "1c17b11693cb5ec63859b091c5b9c1b2"

    # 下载一个测试图片
    test_image_url = "https://images.hollandandbarrettimages.co.uk/productimages/HB/250/084867_A.png"

    print("正在下载测试图片...")
    with httpx.Client(timeout=30.0) as client:
        # 下载图片
        img_response = client.get(test_image_url)
        if img_response.status_code != 200:
            print(f"✗ 下载失败: {img_response.status_code}")
            return

        print(f"✓ 图片下载成功，大小: {len(img_response.content)} bytes")

        # 尝试上传到 EasyImage
        print("\n测试上传到 EasyImage...")

        # EasyImage 常见的上传格式
        files = {"image": ("test.png", img_response.content, "image/png")}
        data = {"token": token}

        try:
            upload_response = client.post(api_url, files=files, data=data, timeout=30.0)
            print(f"响应状态码: {upload_response.status_code}")
            print(f"响应内容: {upload_response.text}")

            if upload_response.status_code == 200:
                result = upload_response.json()
                print("\n✓ 上传成功!")
                print(f"返回数据: {result}")
            else:
                print(f"\n✗ 上传失败")

        except Exception as e:
            print(f"✗ 上传出错: {e}")


if __name__ == "__main__":
    test_easyimage_upload()

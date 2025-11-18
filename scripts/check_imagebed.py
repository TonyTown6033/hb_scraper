#!/usr/bin/env python3
"""
检查图床服务状态

使用方法:
    uv run python scripts/check_imagebed.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
from config import IMAGE_API_URL, IMAGE_API_TOKEN


def check_api_connectivity():
    """检查API连接性"""
    print("=" * 70)
    print("图床API连接性检查")
    print("=" * 70)
    print(f"API URL: {IMAGE_API_URL}")
    print(f"Token: {IMAGE_API_TOKEN[:10]}..." if len(IMAGE_API_TOKEN) > 10 else IMAGE_API_TOKEN)
    print("=" * 70)

    try:
        print("\n1. 检查API是否可访问...")
        client = httpx.Client(timeout=10.0)
        response = client.get(IMAGE_API_URL)

        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")

        if response.status_code == 200:
            print("   ✓ API可访问")
        elif response.status_code == 502:
            print("   ✗ 502 Bad Gateway - 服务器错误")
            print("   可能原因:")
            print("     - 图床服务已关闭或迁移")
            print("     - 服务器配置错误")
            print("     - 网络代理问题")
            return False
        elif response.status_code == 404:
            print("   ✗ 404 Not Found - API地址可能已变更")
            return False
        else:
            print(f"   ⚠️  异常状态码: {response.status_code}")
            return False

    except httpx.ConnectTimeout:
        print("   ✗ 连接超时")
        return False
    except httpx.ConnectError as e:
        print(f"   ✗ 连接错误: {e}")
        return False
    except Exception as e:
        print(f"   ✗ 未知错误: {e}")
        return False

    # 测试上传功能
    print("\n2. 测试图片上传...")
    try:
        # 创建一个1x1像素的测试图片
        from PIL import Image
        from io import BytesIO

        img = Image.new('RGB', (1, 1), color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_data = buffer.getvalue()

        files = {"image": ("test.png", image_data, "image/png")}
        data = {"token": IMAGE_API_TOKEN}

        response = client.post(IMAGE_API_URL, files=files, data=data)

        print(f"   状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get("result") == "success":
                print(f"   ✓ 上传成功: {result.get('url')}")
                return True
            else:
                print(f"   ✗ 上传失败: {result.get('message', '未知错误')}")
                return False
        elif response.status_code == 502:
            print("   ✗ 502 Bad Gateway - 服务不可用")
            return False
        else:
            print(f"   ✗ 上传失败 (状态码: {response.status_code})")
            try:
                print(f"   响应: {response.text}")
            except:
                pass
            return False

    except Exception as e:
        print(f"   ✗ 上传测试失败: {e}")
        return False
    finally:
        client.close()


def suggest_alternatives():
    """建议替代方案"""
    print("\n" + "=" * 70)
    print("替代方案建议")
    print("=" * 70)

    print("\n如果当前图床不可用，你可以：")
    print("\n1. 使用其他图床服务:")
    print("   - ImgBB (https://imgbb.com)")
    print("   - Imgur (https://imgur.com)")
    print("   - SM.MS (https://sm.ms)")
    print("   - 路过图床 (https://imgse.com)")

    print("\n2. 自建图床:")
    print("   - EasyImage (https://github.com/icret/EasyImages2.0)")
    print("   - Lsky Pro (https://github.com/lsky-org/lsky-pro)")
    print("   - Chevereto (https://chevereto.com)")

    print("\n3. 使用云存储:")
    print("   - 阿里云OSS")
    print("   - 腾讯云COS")
    print("   - 七牛云")
    print("   - AWS S3")

    print("\n4. 临时方案:")
    print("   - 保留原始图片URL（不上传）")
    print("   - 本地保存处理后的图片")

    print("\n5. 修复当前图床:")
    print("   - 联系图床管理员")
    print("   - 检查服务器状态")
    print("   - 更新API地址")


def main():
    print("\n图床服务诊断工具\n")

    is_working = check_api_connectivity()

    if is_working:
        print("\n" + "=" * 70)
        print("✓ 图床服务正常，可以使用！")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✗ 图床服务不可用")
        print("=" * 70)
        suggest_alternatives()

        print("\n" + "=" * 70)
        print("配置说明")
        print("=" * 70)
        print("\n如果需要更换图床，请修改配置:")
        print("1. 复制 .env.example 为 .env")
        print("2. 编辑 .env 文件，修改:")
        print("   IMAGE_API_URL=你的图床API地址")
        print("   IMAGE_API_TOKEN=你的图床Token")
        print("3. 重新运行此脚本测试")

    print("\n")


if __name__ == "__main__":
    main()

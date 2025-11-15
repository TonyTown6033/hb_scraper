"""批量处理CSV文件中的图片"""

import csv
import os
from pathlib import Path
from image_processor import ImageProcessor
from tqdm import tqdm


def process_csv_images(
    input_csv: str,
    output_csv: str,
    api_url: str,
    token: str,
    image_column: str = "产品图",
    name_column: str = "产品名称",
):
    """
    批量处理CSV中的图片

    Args:
        input_csv: 输入CSV文件路径
        output_csv: 输出CSV文件路径
        api_url: EasyImage API地址
        token: API token
        image_column: 图片列名
        name_column: 产品名称列名
    """
    print(f"\n{'=' * 70}")
    print(f"处理文件: {input_csv}")
    print(f"{'=' * 70}")

    # 读取CSV
    with open(input_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not rows:
        print("✗ CSV文件为空")
        return

    print(f"✓ 读取到 {len(rows)} 条产品数据")
    print(f"✓ 列名: {', '.join(fieldnames)}")

    # 检查必需的列是否存在
    if image_column not in fieldnames:
        print(f"✗ 未找到图片列: {image_column}")
        return

    # 初始化图片处理器
    with ImageProcessor(api_url, token) as processor:
        success_count = 0
        skip_count = 0
        fail_count = 0

        # 使用进度条处理每一行
        for idx, row in enumerate(tqdm(rows, desc="处理进度"), 1):
            original_url = row.get(image_column, "").strip()
            product_name = row.get(name_column, f"product_{idx}")

            # 显示当前处理的产品
            tqdm.write(f"\n[{idx}/{len(rows)}] {product_name[:50]}")

            if not original_url:
                tqdm.write(f"  → 跳过：无图片URL")
                skip_count += 1
                continue

            # 处理并上传图片
            new_url = processor.process_and_upload(original_url, product_name)

            if new_url:
                row[image_column] = new_url
                tqdm.write(f"  ✓ 成功: {new_url}")
                success_count += 1
            else:
                tqdm.write(f"  ✗ 失败: 保留原URL")
                fail_count += 1

    # 保存结果
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'=' * 70}")
    print(f"处理完成！")
    print(f"{'=' * 70}")
    print(f"✓ 成功: {success_count}")
    print(f"→ 跳过: {skip_count}")
    print(f"✗ 失败: {fail_count}")
    print(f"总计: {len(rows)}")
    print(f"\n保存到: {output_csv}")
    print(f"{'=' * 70}\n")


def image_post_precessor():
    """主函数"""
    # 配置
    API_URL = "http://81.68.170.234/api/index.php"
    TOKEN = "1c17b11693cb5ec63859b091c5b9c1b2"

    # 数据目录
    data_dir = Path("data/output")

    # 要处理的文件列表
    files_to_process = [
        {
            "input": data_dir / "products_complete.csv",
            "output": data_dir / "products_complete_processed.csv",
        },
        {
            "input": data_dir / "products_complete_zh.csv",
            "output": data_dir / "products_complete_zh_processed.csv",
        },
    ]

    print("\n" + "=" * 70)
    print("CSV 图片批量处理工具")
    print("=" * 70)
    print(f"图床API: {API_URL}")
    print(f"目标尺寸: 800x800 (白底居中)")
    print("=" * 70)

    for file_info in files_to_process:
        input_file = file_info["input"]
        output_file = file_info["output"]

        # 检查文件是否存在
        if not input_file.exists():
            print(f"\n→ 跳过 {input_file.name}：文件不存在")
            continue

        # 询问是否处理
        print(f"\n找到文件: {input_file.name}")
        response = input(f"是否处理此文件？(y/n，默认y): ").strip().lower()

        if response in ["", "y", "yes"]:
            process_csv_images(
                input_csv=str(input_file),
                output_csv=str(output_file),
                api_url=API_URL,
                token=TOKEN,
            )
        else:
            print(f"→ 跳过 {input_file.name}")

    print("\n" + "=" * 70)
    print("全部完成！")
    print("=" * 70)


if __name__ == "__main__":
    image_post_precessor()

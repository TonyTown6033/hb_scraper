"""批量处理CSV文件中的图片 - 非交互式版本"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.process_csv_images import process_csv_images


def main():
    """非交互式批量处理"""
    # 配置
    API_URL = "http://81.68.170.234/api/index.php"
    TOKEN = "1c17b11693cb5ec63859b091c5b9c1b2"

    # 数据目录
    data_dir = Path("data/output")

    # 要处理的文件列表
    files_to_process = [
        {
            "input": data_dir / "products_complete.csv",
            "output": data_dir / "products_complete_800x400.csv",
        },
        {
            "input": data_dir / "products_complete_zh.csv",
            "output": data_dir / "products_complete_zh_800x400.csv",
        },
    ]

    print("\n" + "=" * 70)
    print("CSV 图片批量处理工具 - 非交互式版本")
    print("=" * 70)
    print(f"图床API: {API_URL}")
    print(f"目标尺寸: 800x400 (横条形白底居中)")
    print("=" * 70)

    for file_info in files_to_process:
        input_file = file_info["input"]
        output_file = file_info["output"]

        # 检查文件是否存在
        if not input_file.exists():
            print(f"\n→ 跳过 {input_file.name}：文件不存在")
            continue

        print(f"\n正在处理: {input_file.name}")
        process_csv_images(
            input_csv=str(input_file),
            output_csv=str(output_file),
            api_url=API_URL,
            token=TOKEN,
        )

    print("\n" + "=" * 70)
    print("全部完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()

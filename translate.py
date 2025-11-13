import os
import pandas as pd
from openai import OpenAI
import time
from pathlib import Path

# ======= 配置区域 =======

# 从环境变量读取 API Key（更安全）
API_KEY = os.getenv("OPENAI_API_KEY", "sk-i4E6if7Ksb1oqiFC8MIm0wacx5HaOJjhzlvByD3vH3Pe5vJW")

# OpenAI Host（可自定义代理）
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai-proxy.org/v1")

# 输入和输出文件
INPUT_CSV = "./data/output/products_complete.csv"
OUTPUT_CSV = "./data/output/products_complete_zh.csv"

# 需要翻译的列（其他列保持原样）
COLUMNS_TO_TRANSLATE = ["产品名称", "产品亮点", "产品描述", "用法服量", "营养成分", "配料表"]


# ======= 翻译函数 =======
def translate_text(client, text, target_lang="中文", max_retries=3):
    """翻译文本，支持重试"""
    if pd.isna(text) or not str(text).strip():
        return text

    # 如果文本太短或已经是中文，跳过
    text_str = str(text).strip()
    if len(text_str) < 3:
        return text

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的翻译助手，只翻译内容，不解释、不增删。保持原有的格式（如分号分隔）。",
                    },
                    {"role": "user", "content": f"请将以下内容翻译为{target_lang}：\n{text}"},
                ],
                timeout=60,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"   ⚠️ 翻译失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                print(f"   ✗ 达到最大重试次数，保留原文")
                return text  # 出错时保留原文


# ======= 主函数 =======
def translate_main():
    # 检查输入文件是否存在
    if not Path(INPUT_CSV).exists():
        print(f"❌ 错误：输入文件不存在 {INPUT_CSV}")
        print(f"提示：请先运行 main.py 生成产品数据")
        return

    # 初始化客户端
    print(f"🔧 初始化 OpenAI 客户端...")
    print(f"   Base URL: {OPENAI_BASE_URL}")
    try:
        client = OpenAI(api_key=API_KEY, base_url=OPENAI_BASE_URL)
        print(f"✓ 客户端初始化成功")
    except Exception as e:
        print(f"❌ 客户端初始化失败: {e}")
        return

    # 读取 CSV
    print(f"\n📖 读取文件：{INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)
    print(f"✓ 共 {len(df)} 行数据，{len(df.columns)} 列")

    # 显示需要翻译的列
    available_cols = [col for col in COLUMNS_TO_TRANSLATE if col in df.columns]
    print(f"\n🔄 需要翻译的列：{', '.join(available_cols)}")
    print(f"⏭️  跳过的列：{', '.join([col for col in df.columns if col not in available_cols])}")

    # 询问是否继续
    response = input(f"\n是否开始翻译？预计耗时：{len(df) * len(available_cols) * 2}秒 (y/n): ")
    if response.lower() != "y":
        print("已取消")
        return

    # 逐列翻译
    total_cells = len(df) * len(available_cols)
    current_cell = 0

    for col in available_cols:
        print(f"\n{'=' * 60}")
        print(f"🈶 正在翻译列：{col}")
        print(f"{'=' * 60}")

        for idx, value in enumerate(df[col], 1):
            current_cell += 1
            progress = (current_cell / total_cells) * 100

            print(f"  [{idx}/{len(df)}] 进度: {progress:.1f}% ", end="")

            if pd.isna(value) or not str(value).strip():
                print("(跳过空值)")
                continue

            print(f"- 正在翻译...")
            translated = translate_text(client, value)
            df.at[idx - 1, col] = translated
            time.sleep(0.5)  # 避免请求过快

    # 保存结果
    print(f"\n{'=' * 60}")
    print(f"💾 保存翻译结果...")
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ 翻译完成！文件已保存为: {OUTPUT_CSV}")
    print(f"{'=' * 60}")

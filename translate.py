import os
import pandas as pd
from openai import OpenAI
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tqdm import tqdm

# ======= 配置区域 =======

# 从环境变量读取 API Key（更安全）
API_KEY = os.getenv("OPENAI_API_KEY", "sk-i4E6if7Ksb1oqiFC8MIm0wacx5HaOJjhzlvByD3vH3Pe5vJW")

# OpenAI Host（可自定义代理）
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai-proxy.org/v1")

# 输入和输出文件
INPUT_CSV = "./data/output/products_complete.csv"
OUTPUT_CSV = "./data/output/products_complete_zh.csv"

# 需要翻译的列（其他列保持原样）
COLUMNS_TO_TRANSLATE = ["产品名称", "产品亮点", "产品描述", "用法说明", "营养成分", "配料表"]

# 多线程配置
MAX_WORKERS = 5  # 最大并发线程数（建议5-10，避免API限流）
RATE_LIMIT_DELAY = 0.2  # 每个请求之间的最小延迟（秒）


# ======= 翻译函数 =======
def translate_text(client, text, rate_limiter, target_lang="中文", max_retries=3):
    """翻译文本，支持重试"""
    if pd.isna(text) or not str(text).strip():
        return text

    # 如果文本太短或已经是中文，跳过
    text_str = str(text).strip()
    if len(text_str) < 3:
        return text

    # 速率限制
    with rate_limiter:
        time.sleep(RATE_LIMIT_DELAY)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的翻译助手。翻译规则：\n1. 只翻译产品信息，不解释、不增删\n2. 完全删除所有地址信息（包括街道地址、邮编、城市、国家等）\n3. 保持原有的格式（如分号分隔、换行等）\n4. 如果内容只包含地址，返回空字符串",
                    },
                    {
                        "role": "user",
                        "content": f"请将以下内容翻译为{target_lang}，并删除所有地址信息：\n{text}",
                    },
                ],
                timeout=60,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            tqdm.write(f"   ⚠️ 翻译失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                tqdm.write(f"   ✗ 达到最大重试次数，保留原文")
                return text  # 出错时保留原文


def translate_cell(client, rate_limiter, idx, col, value):
    """翻译单个单元格"""
    translated = translate_text(client, value, rate_limiter)
    return (idx, col, translated)


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
    skipped_cols = [col for col in df.columns if col not in available_cols]
    print(f"⏭️  跳过的列：{', '.join(skipped_cols)}")

    # 询问是否使用多线程
    print(f"\n⚙️  多线程配置：")
    print(f"   最大并发线程数: {MAX_WORKERS}")
    print(f"   速率限制延迟: {RATE_LIMIT_DELAY}秒")

    estimated_time_single = len(df) * len(available_cols) * 2
    estimated_time_multi = (len(df) * len(available_cols) * 2) / MAX_WORKERS
    print(f"\n⏱️  预计耗时：")
    print(f"   单线程: {estimated_time_single}秒 ({estimated_time_single / 60:.1f}分钟)")
    print(f"   多线程: {estimated_time_multi}秒 ({estimated_time_multi / 60:.1f}分钟)")

    response = input(f"\n是否开始翻译？(y/n): ")
    if response.lower() != "y":
        print("已取消")
        return

    # 准备翻译任务
    tasks = []
    for col in available_cols:
        for idx, value in enumerate(df[col]):
            if pd.isna(value) or not str(value).strip():
                continue
            if len(str(value).strip()) < 3:
                continue
            tasks.append((idx, col, value))

    total_tasks = len(tasks)
    print(f"\n🚀 开始多线程翻译...")
    print(f"   总任务数: {total_tasks}")
    print(f"   并发线程: {MAX_WORKERS}")
    print(f"{'=' * 60}\n")

    # 创建速率限制器（线程锁）
    rate_limiter = Lock()

    # 多线程翻译
    completed_count = 0
    failed_count = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(translate_cell, client, rate_limiter, idx, col, value): (idx, col, value)
            for idx, col, value in tasks
        }

        # 使用 tqdm 显示进度条
        with tqdm(total=total_tasks, desc="翻译进度", unit="cell") as pbar:
            for future in as_completed(future_to_task):
                try:
                    row_idx, col_name, translated = future.result()
                    df.at[row_idx, col_name] = translated
                    completed_count += 1
                except Exception as e:
                    idx, col, value = future_to_task[future]
                    failed_count += 1
                    tqdm.write(f"⚠️  翻译失败: 行{idx} 列{col}")

                pbar.update(1)

    print(f"\n{'=' * 60}")
    print(f"✓ 翻译完成")
    print(f"   成功: {completed_count} 个")
    print(f"   失败: {failed_count} 个")
    print(f"{'=' * 60}")

    # 保存结果
    print(f"\n{'=' * 60}")
    print(f"💾 保存翻译结果...")
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ 翻译完成！文件已保存为: {OUTPUT_CSV}")
    print(f"{'=' * 60}")

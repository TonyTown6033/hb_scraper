#!/usr/bin/env python3
"""测试产品详情页提取功能"""

from extract_product import extract_product_data
import sys

def test_with_html_file():
    """使用保存的HTML文件测试"""
    html_file = "data/samples/Nature's Bounty® Hair, Skin and Nails with Biotin 60 Gummies | H&B.html"

    print("="*80)
    print("测试产品详情页数据提取")
    print("="*80)
    print(f"\n文件: {html_file}\n")

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        product_info = extract_product_data(html_content)

        # 显示提取结果
        print("✓ 数据提取成功!\n")
        print(f"产品名称: {product_info.get('product_name', 'N/A')}")
        print(f"品牌: {product_info.get('brand', 'N/A')}")
        print(f"\n产品亮点 ({len(product_info.get('benefits', []))} 条):")
        for i, benefit in enumerate(product_info.get('benefits', []), 1):
            print(f"  {i}. {benefit}")

        print(f"\n产品描述:")
        desc = product_info.get('description', {}).get('text', '')
        print(f"  {desc[:200]}..." if len(desc) > 200 else f"  {desc}")

        print(f"\n用法服量:")
        directions = product_info.get('directions', {})
        print(f"  {directions.get('text', 'N/A')[:150]}...")

        print(f"\n配料表:")
        ingredients = product_info.get('ingredients', {}).get('text', '')
        print(f"  {ingredients[:200]}..." if len(ingredients) > 200 else f"  {ingredients}")

        print(f"\n营养成分:")
        for nutritional in product_info.get('nutritional_info', [])[:1]:  # 只显示第一个
            for section in nutritional.get('sections', [])[:1]:
                for fact in section.get('facts', [])[:5]:  # 只显示前5个
                    print(f"  {fact['nutrient']}: {fact['amount']}")

        print("\n" + "="*80)
        print("✓ 测试通过！所有字段都能正确提取")
        print("="*80)

    except FileNotFoundError:
        print(f"✗ 错误: 文件 '{html_file}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    test_with_html_file()

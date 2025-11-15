#!/usr/bin/env python3
"""
Holland & Barrett 产品信息提取器

从 HTML 文件或网页中提取产品信息，包括：
- Benefits (产品亮点)
- Description (产品描述)
- Directions (用法服量)
- Ingredients (配料表)
- Nutritional Information (营养成分)
- Warnings (警告)
- Disclaimer (免责声明)
"""

import json
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional


def find_product_uuid(widgets: List[Dict]) -> Optional[str]:
    """
    递归查找产品数据的 UUID
    
    Args:
        widgets: Widget 列表
        
    Returns:
        产品数据的 UUID，如果未找到则返回 None
    """
    for widget in widgets:
        # 检查是否是 accordions widget
        if widget.get('name') == 'accordions':
            refs = widget.get('resolveParamRefs', {})
            for key, uuid in refs.items():
                if 'pdp_product_data' in key:
                    return uuid
        
        # 递归查找子 widget
        if 'children' in widget and widget['children']:
            uuid = find_product_uuid(widget['children'])
            if uuid:
                return uuid
    
    return None


def clean_html(html_text: str) -> str:
    """
    清理 HTML 标签，返回纯文本
    
    Args:
        html_text: HTML 格式的文本
        
    Returns:
        清理后的纯文本
    """
    if not html_text:
        return ''
    
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.get_text(strip=True)


def extract_product_data(html_content: str) -> Dict[str, Any]:
    """
    从 Holland & Barrett 产品页面提取所有产品信息
    
    Args:
        html_content: HTML 页面内容
        
    Returns:
        包含所有产品信息的字典
        
    Raises:
        ValueError: 如果无法找到必要的数据
    """
    # 1. 提取 JSON 数据
    match = re.search(
        r'<script id="__LAYOUT__"[^>]*>(.*?)</script>', 
        html_content, 
        re.DOTALL
    )
    
    if not match:
        raise ValueError("No __LAYOUT__ script found in HTML")
    
    try:
        layout_data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse layout JSON: {e}")
    
    # 2. 查找产品数据 UUID
    product_uuid = find_product_uuid(layout_data.get('widgets', []))
    
    if not product_uuid:
        raise ValueError("Product data UUID not found in layout")
    
    # 3. 获取产品数据
    resolve_values = layout_data.get('resolveParamValues', {})
    
    if product_uuid not in resolve_values:
        raise ValueError(f"Product UUID {product_uuid} not found in resolveParamValues")
    
    product_wrapper = resolve_values[product_uuid]
    
    if 'data' not in product_wrapper:
        raise ValueError("Product data wrapper does not contain 'data' key")
    
    product_data = product_wrapper['data']
    
    # 4. 提取各个字段
    result = {}
    
    # Benefits (产品亮点)
    result['benefits'] = product_data.get('benefits', [])
    
    # Description (产品描述)
    description_html = product_data.get('description', '')
    result['description'] = {
        'html': description_html,
        'text': clean_html(description_html)
    }
    
    # Info Sections
    info_sections = product_data.get('infoSections', {})
    info_section = info_sections.get('infoSection', {})
    
    # Directions (用法服量)
    directions = info_section.get('directions', {})
    result['directions'] = {
        'heading': directions.get('heading', ''),
        'text': directions.get('text', '')
    }
    
    # Ingredients (配料表)
    ingredients = info_section.get('otherIngredients', {})
    ingredients_html = ingredients.get('text', '')
    result['ingredients'] = {
        'heading': ingredients.get('heading', ''),
        'html': ingredients_html,
        'text': clean_html(ingredients_html)
    }
    
    # Nutritional Information (营养成分)
    nutritionals = info_sections.get('nutritionals', [])
    result['nutritional_info'] = []
    
    for nutritional in nutritionals:
        nutritional_data = {
            'heading': nutritional.get('heading', ''),
            'sections': []
        }
        
        for section in nutritional.get('sections', []):
            section_data = {
                'heading': section.get('heading', ''),
                'facts': [],
                'notes': []
            }
            
            # 提取营养成分
            fact = section.get('fact', {})
            for item in fact.get('keys', []):
                section_data['facts'].append({
                    'nutrient': item.get('key', '').strip(),
                    'amount': item.get('value', '').strip()
                })
            
            # 提取备注
            section_data['notes'] = fact.get('notes', [])
            
            nutritional_data['sections'].append(section_data)
        
        result['nutritional_info'].append(nutritional_data)
    
    # Warnings (警告)
    warnings = info_section.get('warnings', {})
    result['warnings'] = {
        'heading': warnings.get('heading', ''),
        'text': warnings.get('text', '')
    }
    
    # Disclaimer (免责声明)
    disclaimer = info_section.get('disclaimer', {})
    result['disclaimer'] = {
        'heading': disclaimer.get('heading', ''),
        'text': disclaimer.get('text', '')
    }
    
    # 产品基本信息
    result['product_name'] = product_data.get('productName', '')
    result['product_id'] = product_data.get('productId', '')
    result['brand'] = product_data.get('brand', {}).get('name', '') if isinstance(product_data.get('brand'), dict) else product_data.get('brand', '')
    
    return result


def print_product_info(product_info: Dict[str, Any]) -> None:
    """
    格式化打印产品信息
    
    Args:
        product_info: 产品信息字典
    """
    print("=" * 80)
    print(f"产品名称: {product_info.get('product_name', 'N/A')}")
    print(f"品牌: {product_info.get('brand', 'N/A')}")
    print(f"产品ID: {product_info.get('product_id', 'N/A')}")
    print("=" * 80)
    
    # Benefits
    print("\n【产品亮点 / Benefits】")
    print("-" * 80)
    for i, benefit in enumerate(product_info.get('benefits', []), 1):
        print(f"{i}. {benefit}")
    
    # Description
    print("\n【产品描述 / Description】")
    print("-" * 80)
    print(product_info.get('description', {}).get('text', 'N/A'))
    
    # Directions
    print("\n【用法服量 / Directions】")
    print("-" * 80)
    directions = product_info.get('directions', {})
    print(f"{directions.get('heading', '')} {directions.get('text', '')}")
    
    # Ingredients
    print("\n【配料表 / Ingredients】")
    print("-" * 80)
    ingredients = product_info.get('ingredients', {})
    print(f"{ingredients.get('heading', '')} {ingredients.get('text', '')}")
    
    # Nutritional Information
    print("\n【营养成分 / Nutritional Information】")
    print("-" * 80)
    for nutritional in product_info.get('nutritional_info', []):
        print(f"\n{nutritional.get('heading', '')}")
        for section in nutritional.get('sections', []):
            print(f"  {section.get('heading', '')}")
            for fact in section.get('facts', []):
                print(f"    {fact['nutrient']}: {fact['amount']}")
            if section.get('notes'):
                print(f"    备注: {', '.join(section['notes'])}")
    
    # Warnings
    print("\n【警告信息 / Warnings】")
    print("-" * 80)
    warnings = product_info.get('warnings', {})
    print(f"{warnings.get('heading', '')} {warnings.get('text', '')}")
    
    # Disclaimer
    print("\n【免责声明 / Disclaimer】")
    print("-" * 80)
    disclaimer = product_info.get('disclaimer', {})
    print(f"{disclaimer.get('heading', '')} {disclaimer.get('text', '')}")
    
    print("\n" + "=" * 80)


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python extract_product.py <html_file_path>")
        print("示例: python extract_product.py 'Nature\\'s Bounty® Hair, Skin and Nails with Biotin 60 Gummies | H&B.html'")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    try:
        # 读取 HTML 文件
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 提取产品信息
        product_info = extract_product_data(html_content)
        
        # 打印信息
        print_product_info(product_info)
        
        # 可选：保存为 JSON
        output_file = html_file.rsplit('.', 1)[0] + '_extracted.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(product_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n数据已保存到: {output_file}")
        
    except FileNotFoundError:
        print(f"错误: 文件 '{html_file}' 不存在")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

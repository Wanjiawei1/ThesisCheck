import re

def find_full_width_punctuation_positions(text):
    """
    查找中文/全角标点符号的位置。
    包括：中文标点（\u3000–\u303F）+ 全角 ASCII（\uFF01–\uFF5E）
    """
    pattern = r'[\u3000-\u303F\uFF01-\uFF5E]'
    return [(m.group(), m.start()) for m in re.finditer(pattern, text)]

def is_reference_format_valid(ref):
    """
    简单判断参考文献格式是否规范：
    - 是否以序号开头（如【1】、[1]、1.等）
    - 是否包含4位年份（1900-2099）
    """
    if not re.match(r'^(\【\d+\】|\[\d+\]|\d+\.)', ref):
        return False, "缺少序号开头（如【1】、[1]、1.）"
    
    if not re.search(r'(19|20)\d{2}', ref):
        return False, "缺少年份信息"
    
    # 可以在这里继续加其他规则
    
    return True, ""

def analyze_txt_references(txt_path):
    """
    读取txt文件，定位参考文献部分，
    检测每条参考文献是否存在全角符号和格式是否规范。
    """
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f]

    in_reference_section = False
    references = []

    for line in lines:
        clean_line = re.sub(r'\s+', '', line)
        if not in_reference_section:
            if clean_line == '参考文献':
                in_reference_section = True
            continue
        if clean_line == '致谢':  # 假设“致谢”后参考文献结束
            break
        if line.strip():
            references.append(line.strip())

    if not references:
        print("⚠️ 没有检测到参考文献条目，请确认格式是否正确。")
        return

    print(f"\n✅ 共检测到 {len(references)} 条参考文献：\n")

    for i, ref in enumerate(references):
        full_width = find_full_width_punctuation_positions(ref)
        format_ok, format_msg = is_reference_format_valid(ref)
        
        if full_width or not format_ok:
            print("—" * 60)
            print(f"❌ 文献{i+1} 存在问题")
            print(f"内容：{ref}")
            
            if full_width:
                print("  - 含有全角标点：")
                for char, pos in full_width:
                    print(f"    位置 {pos}: '{char}' (Unicode: {hex(ord(char))})")
            
            if not format_ok:
                print(f"  - 格式错误：{format_msg}")
            
            print("—" * 60 + "\n")
        else:
            print(f"✅ 文献{i+1} 格式合规且无全角符号：{ref}")


# 示例调用
if __name__ == '__main__':
    analyze_txt_references('references.txt')  # 把这里改成你的txt路径

import re

def find_full_width_punctuation_positions(text):
    """
    查找中文/全角标点符号的位置。
    包括：中文标点（\u3000–\u303F）+ 全角 ASCII（\uFF01–\uFF5E）
    """
    pattern = r'[\u3000-\u303F\uFF01-\uFF5E]'
    return [(m.group(), m.start()) for m in re.finditer(pattern, text)]


def analyze_txt_references(txt_path):
    """
    只检测 .txt 文件中参考文献部分的全角标点
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
        if clean_line == '致谢':
            break
        if line.strip():
            references.append(line.strip())

    if not references:
        print("⚠️ 没有检测到参考文献条目，请确认格式是否正确。")
        return

    print(f"\n✅ 共检测到 {len(references)} 条参考文献：\n")

    for i, ref in enumerate(references):
        full_width = find_full_width_punctuation_positions(ref)
        if full_width:
            print("—" * 60)
            print(f"❌ 文献{i+1} 含有全角标点")
            print(f"内容：{ref}")
            for char, pos in full_width:
                print(f"  - 位置 {pos}: '{char}' (Unicode: {hex(ord(char))})")
            print("—" * 60 + "\n")
        else:
            print(f"✅ 文献{i+1} 无全角标点：{ref}")


# 示例使用方式
if __name__ == '__main__':
    analyze_txt_references('references.txt')  # 请替换成你的 txt 路径

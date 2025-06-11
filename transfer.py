from docx import Document

def extract_text_preserve_full_width(docx_path):
    """
    提取 docx 中的所有文字内容（保留 run 中的全角符号）
    """
    doc = Document(docx_path)
    all_lines = []
    for para in doc.paragraphs:
        line = ''.join(run.text for run in para.runs)
        if line.strip():  # 保留非空行
            all_lines.append(line)
    return all_lines


def convert_docx_to_utf8_txt(docx_path, txt_path):
    """
    将 docx 中内容完整写入 UTF-8 编码的 txt 文件，不丢失全角符号
    """
    lines = extract_text_preserve_full_width(docx_path)
    with open(txt_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    print(f"✅ 成功转换为 UTF-8 TXT，保存至：{txt_path}")


if __name__ == '__main__':
    docx_path = '3.docx'       # ← 修改为你的 Word 文件路径
    txt_path = 'references.txt'       # ← 生成的 UTF-8 txt 文件
    convert_docx_to_utf8_txt(docx_path, txt_path)

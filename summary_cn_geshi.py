from docx import Document
from docx.oxml.ns import qn
import zipfile
from lxml import etree
import re

# 读取 word/styles.xml 默认字体
def get_default_fonts(docx_path):
    default_fonts = {}
    try:
        with zipfile.ZipFile(docx_path) as docx_zip:
            with docx_zip.open('word/styles.xml') as styles_file:
                styles_xml = etree.parse(styles_file)
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

                rpr_default = styles_xml.find('.//w:docDefaults/w:rPrDefault/w:rPr', ns)
                if rpr_default is not None:
                    rFonts = rpr_default.find('w:rFonts', ns)
                    if rFonts is not None:
                        default_fonts['eastAsia'] = rFonts.get(qn('w:eastAsia'))
                        default_fonts['ascii'] = rFonts.get(qn('w:ascii'))
    except Exception as e:
        pass
    return default_fonts

# 优先从 run 读取字体（含 XML），否则用 default_fonts fallback
def get_run_font_name_full(run, default_fonts):
    try:
        rPr = run._element.rPr
        if rPr is not None and rPr.rFonts is not None:
            rFonts = rPr.rFonts
            font_east = rFonts.get(qn('w:eastAsia'))
            font_ascii = rFonts.get(qn('w:ascii'))
            font_cs = rFonts.get(qn('w:cs'))
            if font_east or font_ascii or font_cs:
                return font_east or font_ascii or font_cs

        # fallback 到 run.font.name
        if run.font.name:
            return run.font.name
    except Exception:
        pass

    # fallback 到文档默认字体
    return default_fonts.get('eastAsia') or default_fonts.get('ascii') or "未知"

# 获取字号 pt
def get_effective_font_size(run, para):
    if run.font.size:
        return run.font.size.pt
    if run.style and run.style.font and run.style.font.size:
        return run.style.font.size.pt
    if para.style and para.style.font and para.style.font.size:
        return para.style.font.size.pt
    return "未知"

# 输出 run 内容
def describe_run(run, para, default_fonts):
    font_name = get_run_font_name_full(run, default_fonts)
    font_size = get_effective_font_size(run, para)
    text = run.text
    return f"【{text}】 字体: {font_name} 大小: {font_size}pt"

# 输出段落格式
def describe_paragraph(para, default_fonts):
    alignment_map = {0: "左对齐", 1: "居中", 2: "右对齐"}
    alignment = para.alignment
    align_str = alignment_map.get(alignment, "默认")

    indent = para.paragraph_format.first_line_indent
    indent_str = f"{indent.pt}pt" if indent else "无缩进"

    line_spacing = para.paragraph_format.line_spacing
    spacing_str = f"{line_spacing}" if line_spacing else "未知"

    print(f"\n段落内容: {para.text.strip()}")
    print(f"→ 对齐方式: {align_str}，首行缩进: {indent_str}，行距: {spacing_str}")
    for run in para.runs:
        print("   ", describe_run(run, para, default_fonts))

# 主函数
def print_summary_format(docx_path):
    default_fonts = get_default_fonts(docx_path)
    doc = Document(docx_path)
    paragraphs = doc.paragraphs

    in_summary = False
    print("========== 中文摘要格式对照输出 ==========")

    for i, para in enumerate(paragraphs):
        text = para.text.strip()

        # 摘要标题段
        if re.fullmatch(r"摘\s{2}要", text):
            print("\n【摘要标题段】")
            describe_paragraph(para, default_fonts)
            in_summary = True
            continue

        if in_summary:
            if text.startswith("关键词") or text.startswith("关键词："):
                print("\n【关键词段】")
                describe_paragraph(para, default_fonts)
                break
            elif text:
                print("\n【摘要正文段】")
                describe_paragraph(para, default_fonts)
        else:
            if 10 <= len(text) <= 50 and "摘要" not in text and i < 10:
                print("\n【可能是论文题目段】")
                describe_paragraph(para, default_fonts)

if __name__ == "__main__":
    print_summary_format("测试论文.docx")  # 修改为你的文件路径
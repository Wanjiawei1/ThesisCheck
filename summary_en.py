from docx import Document
from docx.oxml.ns import qn
import zipfile
from lxml import etree
import re

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
                        default_fonts['ascii'] = rFonts.get(qn('w:ascii'))
    except:
        pass
    return default_fonts

def get_font_name(run, default_fonts, para=None):
    try:
        rPr = run._element.rPr
        if rPr is not None and rPr.rFonts is not None:
            font_ascii = rPr.rFonts.get(qn('w:ascii'))
            if font_ascii:
                return font_ascii
        if run.font.name:
            return run.font.name
        if para and para.style and para.style.font and para.style.font.name:
            return para.style.font.name
    except:
        pass
    return default_fonts.get('ascii') or "未知"

def get_font_size(run, para):
    if run.font.size:
        return run.font.size.pt
    if run.style and run.style.font and run.style.font.size:
        return run.style.font.size.pt
    if para.style and para.style.font and para.style.font.size:
        return para.style.font.size.pt
    return "未知"

def get_paragraph_info(para, default_fonts):
    return {
        'text': para.text.strip(),
        'alignment': para.alignment,
        'line_spacing': para.paragraph_format.line_spacing,
        'fonts': [(run.text, get_font_name(run, default_fonts, para), get_font_size(run, para)) for run in para.runs],
    }

def explain_check(label, info, expected):
    errors = []
    notes = []

    for txt, font, size in info['fonts']:
        if txt.strip():
            if expected['font'] and font != expected['font']:
                errors.append(f"✘ 字体错误 → 实际：{font}，应为：{expected['font']}")
                break
            else:
                notes.append("✓ 字体正确")
            if expected['size'] and size not in expected['size']:
                errors.append(f"✘ 字号错误 → 实际：{size}pt，应为：{expected['size']}")
                break
            else:
                notes.append("✓ 字号正确")

    if expected.get('alignment') is not None:
        if info['alignment'] != expected['alignment']:
            errors.append(f"✘ 对齐方式错误 → 实际：{info['alignment']}，应为：{expected['alignment']}")
        else:
            notes.append("✓ 对齐正确")

    if expected.get('line_spacing') is not None:
        if info['line_spacing'] not in expected['line_spacing']:
            errors.append(f"✘ 行距错误 → 实际：{info['line_spacing']}，应为：{expected['line_spacing']}")
        else:
            notes.append("✓ 行距正确")

    return errors, notes

def print_check(label, info, expected, preview=30):
    errors, notes = explain_check(label, info, expected)
    text = info['text']
    if errors:
        print(f"{label:<14}：❌ 不合格 → 内容预览：{text[:preview]}")
        for e in errors:
            print("  ", e)
    else:
        print(f"{label:<14}：✅ 合格   → 内容预览：{text[:preview]}")
        for n in notes:
            print("  ", n)

# 新增：模糊定位 Abstract / Keywords
def extract_en_summary_range(paras):
    start = end = None
    for i, para in enumerate(paras):
        text = para.text.strip().lower().replace(" ", "")
        if text == "abstract":
            start = i
            break
    if start is None:
        return None, None
    for j in range(start + 1, len(paras)):
        text = paras[j].text.strip().lower().replace(" ", "")
        if text.startswith("keywords") or text.startswith("key:") or "keyword" in text:
            end = j
            break
    return start, end

def check_english_summary(docx_path):
    default_fonts = get_default_fonts(docx_path)
    doc = Document(docx_path)
    paras = doc.paragraphs

    start, end = extract_en_summary_range(paras)
    if start is None or end is None:
        print("❌ 无法定位英文摘要 Abstract → Keywords 区间")
        return

    abstract_paras = paras[start:end + 1]
    print("\n========== 英文摘要 检查报告（v2.1）==========")

    for idx, para in enumerate(abstract_paras):
        info = get_paragraph_info(para, default_fonts)
        text = info['text']

        if idx == 0:
            label = "Abstract标题"
            expected = {'font': 'Times New Roman', 'size': [15.0, 16.0], 'alignment': 1}
        elif idx == len(abstract_paras) - 1:
            label = "Keywords段"
            expected = {'font': None, 'size': [10.5, 12.0]}
            kw_text = text.lower().replace("keywords", "").replace("key words", "").replace(":", "")
            keywords = [k.strip() for k in re.split(r'[，,]', kw_text) if k.strip()]
            if not (3 <= len(keywords) <= 5):
                print(f"{label:<14}：❌ 不合格 → 内容预览：{text[:40]}")
                print(f"  ✘ 关键词数量错误：{len(keywords)} 个，应为 3～5 个")
                continue
        else:
            label = "摘要正文段"
            expected = {'font': 'Times New Roman', 'size': [10.5, 12.0], 'line_spacing': [1.5, 27.6, 28.0]}

        print_check(label, info, expected)

if __name__ == "__main__":
    check_english_summary("测试论文.docx")  # ← 替换成你的 Word 文件路径

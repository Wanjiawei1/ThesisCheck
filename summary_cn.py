from docx import Document
from docx.oxml.ns import qn
import zipfile
from lxml import etree
import re

# ========== 获取默认字体 ===============
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
    except Exception:
        pass
    return default_fonts

def get_font_name(run, default_fonts):
    try:
        rPr = run._element.rPr
        if rPr is not None and rPr.rFonts is not None:
            rFonts = rPr.rFonts
            font_east = rFonts.get(qn('w:eastAsia'))
            font_ascii = rFonts.get(qn('w:ascii'))
            font_cs = rFonts.get(qn('w:cs'))
            if font_east or font_ascii or font_cs:
                return font_east or font_ascii or font_cs
        if run.font.name:
            return run.font.name
    except:
        pass
    return default_fonts.get('eastAsia') or default_fonts.get('ascii') or "未知"

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
        'fonts': [(run.text, get_font_name(run, default_fonts), get_font_size(run, para)) for run in para.runs],
    }

def explain_check(label, info, expected):
    errors = []
    notes = []

    # 字体和字号检查
    for txt, font, size in info['fonts']:
        if txt.strip():
            if expected['font'] and font != expected['font']:
                errors.append(f"✘ 字体不是{expected['font']} → 实际：{font}")
                break
            else:
                notes.append("✓ 字体正确")
            if expected['size'] and size not in expected['size']:
                errors.append(f"✘ 字号不正确 → 实际：{size}pt，应为：{expected['size']}")
                break
            else:
                notes.append("✓ 字号正确")

    # 对齐方式
    if expected.get('alignment') is not None:
        if info['alignment'] != expected['alignment']:
            errors.append(f"✘ 对齐方式错误 → 实际：{info['alignment']}，应为：{expected['alignment']}")
        else:
            notes.append("✓ 对齐正确")

    # 行距
    if expected.get('line_spacing') is not None:
        if info['line_spacing'] not in expected['line_spacing']:
            errors.append(f"✘ 行距错误 → 实际行距：{info['line_spacing']}，应为：{expected['line_spacing']}")
        else:
            notes.append("✓ 行距正确")

    return errors, notes

def check_summary_part(docx_path):
    default_fonts = get_default_fonts(docx_path)
    doc = Document(docx_path)
    paras = doc.paragraphs

    summary_start = summary_end = None
    for i, para in enumerate(paras):
        if re.fullmatch(r"摘\s{2}要", para.text.strip()):
            summary_start = i
            break
    for i in range(summary_start + 1, len(paras)):
        if paras[i].text.strip().startswith("关键词"):
            summary_end = i
            break
    if summary_start is None or summary_end is None:
        print("❌ 无法定位摘要区域")
        return

    summary_paras = paras[summary_start:summary_end + 1]

    print("========== 中文摘要 检查报告（无缩进） ==========")
    for idx, para in enumerate(summary_paras):
        info = get_paragraph_info(para, default_fonts)
        text = info['text']

        if idx == 0:  # 摘要标题
            label = "摘要标题段"
            expected = {'font': '黑体', 'size': [15.0, 16.0], 'alignment': 1}
        elif idx == len(summary_paras) - 1:  # 关键词
            label = "关键词段"
            keyword_text = text.replace("关键词", "").replace("：", "").replace(":", "")
            keywords = [k.strip() for k in re.split(r'[，,]', keyword_text) if k.strip()]
            count_ok = 3 <= len(keywords) <= 5
            if not count_ok:
                print(f"{label:<10}：❌ 不合格 → 内容预览：{text[:30]}")
                print(f"  ✘ 关键词数量错误：{len(keywords)} 个，应为 3～5 个")
                continue
            expected = {'font': None, 'size': [10.5, 12.0]}
        else:
            label = "摘要正文段"
            expected = {'font': '宋体', 'size': [10.5, 12.0], 'line_spacing': [1.5, 27.6, 28.0]}

        errors, notes = explain_check(label, info, expected)
        if errors:
            print(f"{label:<10}：❌ 不合格 → 内容预览：{text[:30]}")
            for e in errors:
                print("  ", e)
        else:
            print(f"{label:<10}：✅ 合格  → 内容预览：{text[:30]}")
            for n in notes:
                print("  ", n)

if __name__ == "__main__":
    check_summary_part("测试论文.docx")  # ← 修改为你的文件路径

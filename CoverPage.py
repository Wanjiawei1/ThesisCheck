from docx import Document
import re

# 字号对应磅值（近似）
font_size_map = {
    "小二": 36,
    "三号": 16,
    "小三号": 15
}

def get_effective_font_name(run, paragraph):
    return run.font.name or paragraph.style.font.name or "None"

def check_font_style(runs, paragraph, expected_fonts, expected_size):
    reasons = []
    if not runs:
        return False, "无有效内容"

    for run in runs:
        font_name = get_effective_font_name(run, paragraph)
        size = run.font.size.pt if run.font.size else None

        font_ok = any(f in font_name for f in expected_fonts)
        size_ok = size and abs(size - expected_size) < 0.5

        if not font_ok:
            reasons.append(f"字体应为{'或'.join(expected_fonts)}，当前为：{font_name}")
        if not size_ok:
            reasons.append(f"字号应为{expected_size:.1f}pt，当前为：{size:.1f}pt" if size else "字号未设置")

    if not reasons:
        return True, ""
    else:
        return False, "，".join(reasons)

def check_cover_page_final(docx_path):
    doc = Document(docx_path)
    paragraphs = [p for p in doc.paragraphs if p.text.strip()]
    para_texts = [p.text.strip() for p in paragraphs]
    cover_paragraphs = paragraphs[:20]
    full_text = "\n".join(para_texts)

    result = {}

    # 学校名称
    style_ok, reason = check_font_style(cover_paragraphs[0].runs, cover_paragraphs[0], ["宋体", "黑体"], font_size_map["小二"])
    result["学校名称"] = {
        "内容": any("浙江工业大学" in p.text for p in cover_paragraphs),
        "样式": style_ok,
        "原因": reason
    }

    # 论文题目：跳过“题目”两个字
    title_idx = 1 if len(cover_paragraphs) > 1 else 0
    title_para = cover_paragraphs[title_idx]
    content_runs = []
    found_title_label = False
    for run in title_para.runs:
        if not found_title_label and "题目" in run.text:
            found_title_label = True
            continue
        if found_title_label:
            content_runs.append(run)

    style_ok, reason = check_font_style(content_runs, title_para, ["黑体", "宋体"], font_size_map["三号"])
    result["论文题目"] = {
        "内容": len(title_para.text.strip()) > 5,
        "样式": style_ok,
        "原因": reason
    }

    # 常规字段
    field_keywords = {
        "学院": "学院",
        "班级": "班级",
        "学号": "学号",
        "学生姓名": "学生姓名",
        "指导老师": "指导老师"
    }

    used_texts = set()
    for field, keyword in field_keywords.items():
        pattern = re.sub(r"(.)", lambda m: re.escape(m.group(1)) + r"\s*", keyword)
        matched = re.search(pattern, full_text)
        result[field] = {
            "内容": bool(matched),
            "样式": None,
            "原因": ""
        }
        if matched:
            for p in cover_paragraphs:
                if re.search(pattern, p.text):
                    used_texts.add(p.text.strip())
                    style_ok, reason = check_font_style(p.runs, p, ["宋体", "黑体"], font_size_map["小三号"])
                    result[field]["样式"] = style_ok
                    result[field]["原因"] = reason
                    break

    # 专业字段（宽松匹配 + 样式要求）
    candidate_para = None
    for p in cover_paragraphs:
        text = p.text.strip()
        if (
            text not in used_texts
            and 3 <= len(text) <= 20
            and not any(k in text for k in ["浙江工业大学", "论文", "指导", "学号", "班级", "学院", "姓名", "题目", "提交", "学生"])
        ):
            candidate_para = p
            break

    result["专业"] = {
        "内容": candidate_para is not None,
        "样式": None,
        "原因": ""
    }
    if candidate_para:
        used_texts.add(candidate_para.text.strip())
        style_ok, reason = check_font_style(candidate_para.runs, candidate_para, ["宋体", "黑体"], font_size_map["小三号"])
        result["专业"]["样式"] = style_ok
        result["专业"]["原因"] = reason

    # 校外指导教师（可选）
    label = "校外指导教师"
    matched = re.search(label, full_text)
    result[label] = {
        "内容": bool(matched),
        "样式": None,
        "原因": ""
    }
    if matched:
        for p in cover_paragraphs:
            if label in p.text:
                style_ok, reason = check_font_style(p.runs, p, ["宋体", "黑体"], font_size_map["小三号"])
                result[label]["样式"] = style_ok
                result[label]["原因"] = reason
                break

    # 提交日期
    date_match = re.search(r"\d{4}年\d{1,2}月", full_text)
    result["提交日期"] = {
        "内容": bool(date_match),
        "样式": None,
        "原因": ""
    }
    if date_match:
        for p in cover_paragraphs:
            if date_match.group() in p.text:
                style_ok, reason = check_font_style(p.runs, p, ["宋体", "黑体"], font_size_map["小三号"])
                result["提交日期"]["样式"] = style_ok
                result["提交日期"]["原因"] = reason
                break

    # 输出检测结果
    print("\n📘 浙江工业大学信息学院封面检测结果：")
    for field, status in result.items():
        if field == "校外指导教师" and not status["内容"]:
            continue
        c = "✔️" if status["内容"] else "❌"
        s = "✔️" if status["样式"] else "❌" if status["样式"] is not None else "（未检测）"
        print(f"- {field}：内容 {c} / 样式 {s}")
        if status["样式"] is False and status["原因"]:
            print(f"    ↪ 样式问题：{status['原因']}")

    return result

# 示例调用
if __name__ == '__main__':
    docx_path = '毕业论文-陈耿洋1.docx'  # 替换为你自己的路径
    check_cover_page_final(docx_path)

from docx import Document

def describe_alignment(alignment):
    if alignment == 0:
        return "左对齐"
    elif alignment == 1:
        return "居中"
    elif alignment == 2:
        return "右对齐"
    else:
        return "未知/默认"

def describe_cover_styles(docx_path, max_lines=20):
    doc = Document(docx_path)
    paragraphs = [p for p in doc.paragraphs if p.text.strip() != ""]

    print(f"📘 检测封面样式（前 {max_lines} 段）:\n")

    for i, para in enumerate(paragraphs[:max_lines]):
        print(f"🔹 第{i+1}段：{para.text.strip()}")
        align_desc = describe_alignment(para.alignment)
        print(f"   - 段落对齐方式：{align_desc}")

        for j, run in enumerate(para.runs):
            font_name = run.font.name 
            font_size = f"{run.font.size.pt:.1f} pt" if run.font.size else "（未设置）"
            bold = run.bold
            bold_str = "加粗" if bold else "不加粗" if bold is False else "默认/继承"

            text_sample = run.text.strip()
            if text_sample == "":
                continue
            print(f"     · Run{j+1}：'{text_sample}'")
            print(f"       - 字体：{font_name}，字号：{font_size}，加粗：{bold_str}")
        print("")

# 示例调用
if __name__ == "__main__":
    describe_cover_styles("毕业论文-陈耿洋1.docx")

import re
import zipfile
from docx import Document

def check_commitment_info_by_zip(docx_path):
    """
    同时检测承诺书内容、是否插入 jpeg 图片、是否填写日期
    """
    doc = Document(docx_path)
    has_commitment = False
    has_written_date = False

    # 正则匹配中文日期
    date_pattern = re.compile(r"20\d{2}年\d{1,2}月\d{1,2}日")
    keywords = ["诚信承诺书", "本人慎重承诺", "签名", "浙江工业大学"]

    # 遍历段落查找关键词和日期
    for para in doc.paragraphs:
        text = para.text.strip()
        if any(keyword in text for keyword in keywords):
            has_commitment = True
        if date_pattern.search(text):
            has_written_date = True

    # 用 zipfile 检查是否包含 JPEG 文件
    has_jpeg_image = False
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        image_files = [f for f in docx_zip.namelist() if f.startswith("word/media/")]
        for img in image_files:
            if img.lower().endswith(".jpeg") or img.lower().endswith(".jpg"):
                has_jpeg_image = True
                break

    return has_commitment, has_jpeg_image, has_written_date

def main(docx_path):
    has_commitment, has_jpeg, has_date = check_commitment_info_by_zip(docx_path)

    print("====== 承诺书检测报告======")

    if not has_commitment:
        print("❌ 未检测到承诺书内容")
        return

    print("✅ 检测到承诺书内容")

    if has_jpeg:
        print("✅ 检测到插入的 JPEG 图像（可能是签名）")
    else:
        print("⚠️ 未检测到 JPEG 图片")

    if has_date:
        print("✅ 检测到日期填写")
    else:
        print("⚠️ 未检测到日期")

if __name__ == "__main__":
    docx_path = "测试论文.docx"  # ← 替换为你的文件名
    main(docx_path)

import os
from docx2pdf import convert
from pdf2image import convert_from_path
import cv2
import numpy as np

# 1. DOCX -> PDF
def docx_to_pdf(docx_path, output_pdf_path):
    convert(docx_path, output_pdf_path)
    print(f"转换完成: {docx_path} -> {output_pdf_path}")

# 2. PDF -> 图片列表
def pdf_to_images(pdf_path, dpi=200):
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=r'D:\develop\poppler-24.08.0\Library\bin')
    print(f"PDF 转图片完成，共 {len(images)} 张")
    return images

# 3. 简单图像检测示例（检测图片是否偏暗）
def detect_image_darkness(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    mean_brightness = np.mean(gray)
    result = "偏暗" if mean_brightness < 100 else "正常"
    return result, mean_brightness

# 4. 生成检测报告
def generate_report(results, report_path):
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 图像检测报告\n\n")
        for i, (status, brightness) in enumerate(results):
            f.write(f"第{i+1}页：状态：{status}，平均亮度：{brightness:.2f}\n\n")
    print(f"报告已生成: {report_path}")

# 主流程
def main(docx_path):
    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    pdf_path = f"{base_name}.pdf"
    report_path = f"{base_name}_report.md"

    # 创建图片保存文件夹
    images_dir = f"{base_name}_images"
    os.makedirs(images_dir, exist_ok=True)

    # 1. 转PDF
    docx_to_pdf(docx_path, pdf_path)

    # 2. 转图片
    images = pdf_to_images(pdf_path)

    # 3. 逐页检测并保存图片到指定文件夹
    results = []
    for idx, img in enumerate(images):
        status, brightness = detect_image_darkness(img)
        img_path = os.path.join(images_dir, f"page_{idx+1}.png")
        img.save(img_path)
        results.append((status, brightness))

    # 4. 生成报告
    generate_report(results, report_path)

if __name__ == "__main__":
    docx_file = "测试论文.docx"  # 改成你的文件名
    main(docx_file)

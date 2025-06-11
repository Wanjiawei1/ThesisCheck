import os
from docx import Document

def extract_images_from_docx(docx_path, save_folder):
    # 检查保存图片的文件夹是否存在，如果不存在则创建
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 打开 DOCX 文件
    doc = Document(docx_path)

    # 遍历文档中的所有关系
    for rel in doc.part.rels.values():
        if rel.reltype.startswith('http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'):
            # 获取图片的二进制数据
            image_data = rel.target_part.blob
            # 获取图片的文件名
            image_filename = rel.target_part.filename
            # 生成图片的完整保存路径
            image_save_path = os.path.join(save_folder, image_filename)
            # 保存图片到指定文件夹
            with open(image_save_path, "wb") as f:
                f.write(image_data)
            print(f"图片已保存为: {image_save_path}")

if __name__ == "__main__":
    # 替换为你的 DOCX 文件路径
    docx_file_path = "毕业论文-陈耿洋1.docx"
    # 替换为你想要保存图片的文件夹路径
    save_image_folder = "~/pic"
    extract_images_from_docx(docx_file_path, save_image_folder)

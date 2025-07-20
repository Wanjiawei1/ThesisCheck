import zipfile
import os

def extract_images_from_docx(docx_path, output_dir="pic"):
    # 创建保存图片的文件夹
    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        # 找出所有内嵌图片
        image_files = [f for f in docx_zip.namelist() if f.startswith("word/media/")]

        if not image_files:
            print("❌ 文档中未发现任何图片。")
            return

        print(f"✅ 共发现 {len(image_files)} 张图片，正在提取至文件夹：{output_dir}/\n")

        for img_name in image_files:
            img_data = docx_zip.read(img_name)
            img_filename = os.path.basename(img_name)
            output_path = os.path.join(output_dir, img_filename)

            with open(output_path, "wb") as f:
                f.write(img_data)

            print(f"📎 提取：{img_filename}")

        print("\n🎉 所有图片提取完成！")

if __name__ == "__main__":
    docx_path = "测试论文.docx"  # 修改为你的实际路径
    extract_images_from_docx(docx_path)

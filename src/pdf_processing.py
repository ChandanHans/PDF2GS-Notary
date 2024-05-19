import os
import fitz
from tqdm import tqdm


def delete_images(directory_path):
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        pass

def pdf_to_images(pdf_path, output_folder, resolution):
    delete_images(output_folder)
    print("\nGetting All Images From PDF...")
    doc = fitz.open(pdf_path)
    for i in tqdm(range(len(doc)), ncols=60, bar_format="{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"):
        page = doc.load_page(i)
        image = page.get_pixmap(matrix=fitz.Matrix(resolution / 72, resolution / 72))
        image_path = f"{output_folder}/page-{i + 1}.png"
        image.save(image_path)
    doc.close()
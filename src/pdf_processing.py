import fitz
from tqdm import tqdm

def pdf_to_images(pdf_path, output_folder, resolution=200):
    doc = fitz.open(pdf_path)
    for i in tqdm(range(len(doc)), ncols=60, bar_format="{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"):
        page = doc.load_page(i)
        image = page.get_pixmap(matrix=fitz.Matrix(resolution / 72, resolution / 72))
        image_path = f"{output_folder}/page-{i + 1}.png"
        image.save(image_path)
    doc.close()
import os
import time
import shutil
import pandas as pd

from tqdm import tqdm
from src.pdf_processing import pdf_to_images
from src.excel_util import save_table
from src.image_processing import process_image
from src.utils import *


def main():
    time_start = time.time()
    pdf_files = [file for file in os.listdir(INPUT_FOLDER) if file.lower().endswith(".pdf")]

    for pdf in pdf_files:
        ptime = time.time()
        print(f"\nProcess Started For {pdf}\n")
    
        pdf_path = f"{INPUT_FOLDER}/{pdf}"
        pdf_to_images(pdf_path, IMAGE_FOLDER, 200)
        images = [file for file in os.listdir(IMAGE_FOLDER) if file.lower().endswith(".png")]
        images = sorted(images, key = extract_number)
        data = []
        print("\nSTART :\n")
        for image in tqdm(images, ncols=60, bar_format="{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"):
            data.append(process_image(image))
        print()
        df = pd.DataFrame(data)
        df.columns = ["Name","Data Of Birth","Data Of Death","Declarant","Data Of Notoriety","Notary","Address","Phone","Email","Website","Status"]
        df = df.replace([pd.NA, pd.NaT, float('inf'), float('-inf')], 'N/A')
        save_table(df, pdf_path.replace(".pdf",".xlsx").replace(INPUT_FOLDER,OUTPUT_FOLDER))

        shutil.move(pdf_path, f"{COMPLETED_FOLDER}/{pdf}")
        print(f"\n\nCompleted in {int(time.time() - ptime)} sec\nTotal : {int(time.time()-time_start)} sec")
        
if __name__ == "__main__":
    main()